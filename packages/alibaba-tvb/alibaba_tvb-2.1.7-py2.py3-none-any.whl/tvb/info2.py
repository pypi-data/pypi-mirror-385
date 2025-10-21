# encoding: utf-8
import os
import re
from functools import cmp_to_key
import logging
import chardet

logger = logging.getLogger(__name__)

class Data(object):
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.lines = []
        self.data = None
        
    def add_line(self, line):
        self.lines.append(line)
        
    def get_data(self):
        return ''.join(self.lines)

class Info(object):
    def __init__(self, device_dir, file_name, process_names=[], core_num=1):
        self.device_dir = device_dir
        self.file_name = file_name
        self.core_num = str(core_num)
        self.process_names = r'|'.join(process_names)
        
    def data_iter(self):
        with open(os.path.join(self.device_dir, self.file_name), 'rb') as f:
            lines = []
            for _ in range(10):  # 使用下划线表示循环变量未使用
                line = f.readline()
                if not line:  # 修正拼写错误：`brek` → `break`
                    break
                lines.append(line)

            # 将 bytes 列表合并为一个 bytes 对象（chardet 需要传入 bytes）
            raw_data = b''.join(lines)
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            f.close()
        with open(os.path.join(self.device_dir, self.file_name), 'r', encoding=encoding,errors='ignore') as f:
            data = None
            for line in f:
                if line.startswith('>>'):
                    if data:
                        yield data
                    data = Data(line.split('>>')[1])
                elif data:
                    data.add_line(line)
            if data:
                yield data
                
    #sheet_name, x_axis, y_axis, headings, lines
    def get_sheet2(self, name, y_axis, p, key, operation='float("%s")', type = 'cpu'):
        headings = []
        lines = []
        for i in self.data_iter():
            line = [i.timestamp]
            ds = []
            for m in p.finditer(i.get_data()):
                if m:
                    ds.append(m.groupdict())
            if key == 'cpu':
                if not ds:
                    # x = re.compile(f'^\s*(?P<pid>\d*?)\s.*\s(?P<cpu>\d*?)\s.*\s(?P<pname>%s)' % self.process_names, re.M)
                    x = re.compile(f'\s+(\d+).*[S|R]\s+([\d.\d+]+).*%s' % self.process_names, re.M)
                    for m in x.finditer(i.get_data()):
                        if m:
                            a = {}
                            a['pid'] = str(m.group(1))
                            a[key] = str(m.group(2))
                            a['pname'] = self.process_names
                            ds.append(a)
            r = {}
            for d in ds:
                try:
                    _k = d['pname']
                    if 'pid' in d.keys() and type != 'top':
                        _k += '.%s' % d['pid']
                    r[_k] = eval(operation % d[key])
                except:
                    pass
            for k in r.keys():
                if k not in headings:
                    headings.append(k)
            for h in headings:
                line.append(r.get(h, ''))
            lines.append(line)
        raw_dict = {}
        raw_headings = []
        for i, head in enumerate(headings, 1):
            d = {'sum': 0, 'head': head}
            raw_headings.append(d)
            raw_dict[head] = []
            for line in lines:
                try:
                    raw_dict[head].append(line[i])
                    try:
                        d['sum'] += line[i]
                    except:
                        pass
                except:
                    raw_dict[head].append('')
        # raw_headings = sorted(raw_headings, key=cmp_to_key(lambda x,y:cmp(x['sum'], y['sum'])), reverse=True)
        headings = [r['head'] for r in raw_headings]
        _headings = ['timestamp'] + headings
        _lines = []
        for i in range(len(lines)):
            _line = [lines[i][0]]
            for head in headings:
                _line.append(raw_dict[head][i])
            _lines.append(_line)
        return name, 'time (m/d H:M:S)', y_axis, _headings, _lines
    
    def get_sheet1(self, name, y_axis, p, headings=[], operation='float("%s")'):
        lines = []
        for i in self.data_iter():
            line = [i.timestamp]
            r = {}
            m = p.search(i.get_data())
            if m:
                r = m.groupdict()
            for h in headings:
                d = r.get(h)
                if d:
                    line.append(eval(operation % d))
                else:
                    line.append('')
            lines.append(line)
        headings = ['timestamp'] + headings
        return name, 'time (m/d H:M:S)', y_axis, headings, lines

    def get_top_sheet(self, name, y_axis, p, headings=[], operation='float("%s")'):
        lines = []
        fist_r = {}
        for i in self.data_iter():
            line = [i.timestamp]
            r = {}
            m = p.search(i.get_data())
            if m:
                r = m.groupdict()
                if not fist_r:
                    fist_r = r
            if not fist_r:
                try:
                    a = re.compile(r'(\d+)%user.+(\d+)%sys.+(\d+)%iow.+(\d+)%irq')
                    compile_str = a.search(i.get_data())
                    str_group = compile_str.group()
                except:
                    str_group =''
                headings = ['user', 'sys', 'iow', 'irq']
                for i in headings:
                    b = re.findall(f'(\d+)%{i}', str_group)
                    if len(b) > 0:
                        r[i] = b[0]
            for h in headings:
                d = r.get(h)
                if d:
                    line.append(eval(operation % d))
                else:
                    line.append('')
            lines.append(line)
        headings = ['timestamp'] + headings
        return name, 'time (m/d H:M:S)', y_axis, headings, lines

    def get_uptime_sheet(self):
        lines = []
        headings = ['uptime']
        y_axis = 'uptime (seconds)'
        name = 'uptime'
        p = re.compile('up time:\s+(\d+) days,\s+(\d{2}):(\d{2}):(\d{2}),|up time:\s+(\d{2}):(\d{2}):(\d{2}),')
        for i in self.data_iter():
            line = [i.timestamp]
            m = p.search(i.get_data())
            if m:
                (day, hour, minute, second) = (m.group(1), m.group(2), m.group(3), m.group(4)) if m.group(1) else (0, m.group(5), m.group(6), m.group(7))
                uptime_sec = int(day) * 24 * 3600 + int(hour) * 3600 + int(minute) * 60 + int(second)
                logging.debug('uptime_sheet: uptime secondes %s' % uptime_sec)
                line.append(uptime_sec)
            else:
                line.append('')
            lines.append(line)
        headings = ['timestamp'] + headings
        return name, 'time (m/d H:M:S)', y_axis, headings, lines

class CpuInfo(Info):
    def _get_sheet_info_total(self):
        headings = ['TOTAL', 'user', 'kernel', 'iowait', 'softirq']
        lines = []
        for i in self.data_iter():
            line = [i.timestamp]
            last_line = i.lines[-1]
            rowd = {}
            items = last_line.replace(':', '').replace('+', '').replace('%', '').split()
            ilen = len(items)
            for i in range(int(ilen / 2)):
                rowd[items[i * 2 + 1]] = items[i * 2]
            for head in headings:
                try:
                    d = rowd.get(head)
                    assert '-' not in d
                    line.append(float(d))
                except:
                    line.append('')
            lines.append(line)
        headings = ['timestamp'] + headings
        return 'cpuinfo.total', 'time (m/d H:M:S)', 'total (%)', headings, lines
        
    def get_sheet_list(self):
        sheet_list = [
            self._get_sheet_info_total(),
            self.get_sheet1('cpuinfo.load', 'load (%s)' % self.core_num,
                                re.compile(r'Load: (?P<lavg_1>.*) / (?P<lavg_5>.*) / (?P<lavg_15>\S*)'), ['lavg_1', 'lavg_5', 'lavg_15'])
        ]
        if self.process_names:
            sheet_list.append(self.get_sheet2('cpuinfo.usage', 'usage (%)',
                                re.compile(r'^\D*(?P<cpu>\d.*?)%%\s*(?P<pid>\d*?)/(?P<pname>%s):.*' % self.process_names, re.M), 'cpu'))
        return sheet_list
    
class MemInfo(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_sheet1('meminfo.uptime', 'uptime (second)',
                                re.compile(r'Uptime: (?P<uptime>\d*) Realtime:.*'), ['uptime'], operation='%s / 6000.0'),
#             self.get_sheet1('meminfo.total', 'meminfo (MB)',
#                                 re.compile(r'Total (RAM|PSS): (?P<Total>\d*?) kB.* Free (RAM|PSS): (?P<Free>\d*?) kB.* Used (RAM|PSS): (?P<Used>\d*?) kB.* Lost (RAM|PSS): (?P<Lost>\d*?) kB.*', re.DOTALL),
#                                 ['Total', 'Free', 'Used', 'Lost'], operation='%s / 1024.0')
        ]
        if self.process_names:
            sheet_list.append(self.get_sheet2('meminfo.total', 'meminfo (MB)',
                                re.compile(r'(?P<pname>Total|Free|Used|Lost) (RAM|PSS):\s*(?P<pss>[\d,]*?)( kB|K)'), 'pss', operation='float("%s".replace(",", "")) / 1024'))
            sheet_list.append(self.get_sheet2('meminfo.pss', 'pss (MB)',
                                re.compile(r'^\D*(?P<mem>[\d,]*?)( kB|K): (?P<pname>%s) \(pid (?P<pid>\d*?)\D.*' % self.process_names, re.M), 'mem', operation='float("%s".replace(",", "")) / 1024'))
        return sheet_list

class FreeInfo(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_sheet1('free', 'free (MB)',
                            re.compile(r'Mem:\s+(?P<total>\d+)\s+(?P<os_used>\d+)\s+(?P<os_free>\d+)\s+(?P<share>\d+)\s+(?P<buffers>\d+).*-/\+ buffers:\s+(?P<app_used>\d+)\s+(?P<app_free>\d+)', re.DOTALL),
                            ['total', 'os_used', 'os_free', 'share', 'buffers', 'app_used', 'app_free'])
        ]
        return sheet_list

class UptimeInfo(Info):
    def get_sheet_list(self):
        sheet_list = [self.get_uptime_sheet()]
        return sheet_list


class TopInfo(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_top_sheet('top.total', 'usage (%)',
                                re.compile(r'User (?P<User>\d.*?)%, System (?P<System>\d.*?)%, IOW (?P<IOW>\d.*?)%, IRQ (?P<IRQ>\d.*?)%'),
                                ['User', 'System', 'IOW', 'IRQ'])
        ]
        if self.process_names:
            sheet_list.append(self.get_sheet2('top.cpu', 'usage (%)',
                                re.compile(r'^\s*(?P<pid>\d*?)\s.*\s(?P<cpu>\d*?)%%\s.*\s(?P<pname>%s)' % self.process_names, re.M), 'cpu'))
            sheet_list.append(self.get_sheet2('top.thread', 'thread count',
                                re.compile(r'^\s*(?P<pid>\d*)\s.*\d*%%\s\D\s*(?P<thr>\d*)\s.*(?P<pname>%s)' % self.process_names, re.M), 'thr',operation='float("%s")', type= 'top'))
        return sheet_list

class ProcrankInfo(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_sheet1('procrank.total', 'mem (MB)',
                                re.compile(r'\s*(?P<pss>\d.*?)K\s*(?P<uss>\d.*?)K\s*TOTAL'),
                                ['pss', 'uss'], operation='%s / 1024.0'),
            self.get_sheet1('procrank.RAM', 'mem (MB)',
                                re.compile(r'total,\s*(?P<free>\d.*?)K free,\s*(?P<buffers>\d.*?)K buffers,\s*(?P<cached>\d.*?)K cached,\s*(?P<shmem>\d.*?)K shmem,\s*(?P<slab>\d.*?)K slab'),
                                ['free', 'buffers', 'cached', 'shmem', 'slab'], operation='%s / 1024.0')
        ]
        if self.process_names:
            sheet_list.append(self.get_sheet2('procrank.uss', 'uss (MB)',
                                re.compile(r'\s*(?P<pid>\d+)\s+\d+K\s+\d+K\s+\d+K\s+(?P<uss>\d+)K\s+(?P<pname>%s)' % self.process_names, re.M),
                                'uss', operation='%s / 1024.0'))
            sheet_list.append(self.get_sheet2('procrank.pss', 'PSS (MB)',
                                re.compile(r'\s*(?P<pid>\d+)\s+\d+K\s+\d+K\s+(?P<pss>\d+)K\s+\d+K\s+(?P<pname>%s)' % self.process_names, re.M),
                                'pss', operation='%s / 1024.0'))
        return sheet_list

class Temp0Info(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_sheet1('temperature0', u'temperature (℃)',
                                re.compile(r'(?P<temperature>\d*)'), ['temperature'])
        ]
        return sheet_list
    
class Temp1Info(Info):
    def get_sheet_list(self):
        sheet_list = [
            self.get_sheet1('temperature1', u'temperature (℃)',
                                re.compile(r'(?P<temperature>\d*)'), ['temperature'])
        ]
        return sheet_list

INFO_CONFIG = {
    'cpuinfo': CpuInfo,
    'meminfo': MemInfo,
    'top': TopInfo,
    'free': FreeInfo,
    'uptime': UptimeInfo,
    'procrank': ProcrankInfo,
    'temperature_zone0': Temp0Info,
    'temperature_zone1': Temp1Info
}

if __name__ == '__main__':
    pass
    # info = TopInfo('D:/temp', 'top.txt', ['com.youku.taitan.tv'])
    # info = TopInfo('D:/temp', 'top1.txt', ['com.cibn.tv'])
#     info = ProcrankInfo('D:/0git/tvb/tmp/2016.04.15-12.42.25/30.11.32.92', 'procrank.txt', [])
    info = CpuInfo(r'/Users/wjh/Documents/output/2025.07.09-15.40.24/192.168.10.228', 'cpuinfo.txt', ['com.cibn.tv'])
#     info = UptimeInfo('D:/AliDrive/GitLab/tvb/tvb/2016.08.05-17.10.02/30.11.32.150', 'uptime.txt', ['com.yunos.tvtaobao'])
    import json
    print(json.dumps(info.get_sheet_list(), indent=4))
