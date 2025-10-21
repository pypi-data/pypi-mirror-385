# encoding: utf-8
'''
@author:     Juncheng Chen

@copyright:  1999-2015 Alibaba.com. All rights reserved.

@license:    Apache Software License 2.0

@contact:    juncheng.cjc@outlook.com
'''
import os
from datetime import datetime
import copy
import re
import logging
logger = logging.getLogger(__name__)
from time import sleep
from tvb.namespace import GlobalVariables
from tvb.dump_hprof import DumpHProf
import re
class CMDError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CMDError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


class Command(object):
    def __init__(self, name, command=None, clean_command=None):
        self.name = name
        self.command = command
        self.clean_command = clean_command
        self.process = None
        
    def new(self, device, args):
        self.device = device
        self.args = args
        if not device.check_busybox_killall and self.clean_command is not None:
            self.clean_command = self.clean_command.replace("killall", "pkill")
        return copy.deepcopy(self)
    
    def kill(self):
        if self.process:
            self.process.kill()
            self.process.wait()
            self.process = None
            logger.debug('kill %s %s' % (self.name, self.command))
    
    def is_done(self):
        if self.process:
            return self.process.poll() is not None
        return True
    
    def execute(self):
        pass
    
    def clean(self):
        pass

class LastCommand(Command):
    def execute(self):
        if self.command:
            logger.debug('execute single command %s' % self.command)
            with open(os.path.join(self.device.log_dir, '%s.txt' % self.name), 'a') as f:
                self.process = self.device.shell(self.command)
                f.write(self.device.get_process_stdout(self.process))

class TombstonesCommand(Command):
    def execute(self):
        tombstones_local = os.path.join(self.device.log_dir, 'tombstones')
        if not os.path.isdir(tombstones_local):
            os.makedirs(tombstones_local)
        cmd = 'pull {remote} {local}'.format(remote='/data/tombstones/', local=tombstones_local)
        logger.debug('execute single command adb %s' % cmd)
        self.device.adb(cmd)

class LogcatParserCommand(LastCommand):
    def minis(self, timedic):
        result = dict()
        for (i,dic) in timedic.items():
#            print 'loop data i is %s, data is %s' %(i, dic)
            starttime = 0
            middletime = 0
            endtime = 0
            start = dic['start']
            middle = dic['middle']
            end = dic['end']
            timelist = []
            for t in start.split('.'):
                for tt in t.split(':'):
                    timelist.append(int(tt))
            for ii in range(0, len(timelist)-1):
                timelist[ii] *= 1000
                for n in range(ii, len(timelist)-2):
                    timelist[ii] *= 60
            for num in timelist:
                starttime += num
            timelist = []
            for t in middle.split('.'):
                for tt in t.split(':'):
                    timelist.append(int(tt))
            for ii in range(0, len(timelist)-1):
                timelist[ii] *= 1000
                for n in range(ii, len(timelist)-2):
                    timelist[ii] *= 60
            for num in timelist:
                middletime += num
            timelist = []
            for t in end.split('.'):
                for tt in t.split(':'):
                    timelist.append(int(tt))
            for ii in range(0, len(timelist)-1):
                timelist[ii] *= 1000
                for n in range(ii, len(timelist)-2):
                    timelist[ii] *= 60
            for num in timelist:
                endtime += num
            result[i] ={'t1':middletime-starttime, 't2':endtime - starttime}
        return result

    def execute(self, log_dir=None):
        if log_dir is None:
            log_dir = self.device.log_dir
        mo_stats = dict()
        stats_p = re.compile(r'^\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}.\d{3}\s+\d+\s+\d+\s+([A-Z]{1})\s+(\w+)\s*:')
        sleep(10)
        for log_file in os.listdir(log_dir):
            if log_file.startswith('logcat_'):
                self.log = os.path.join(log_dir, log_file)

                if hasattr(self, 'args') and self.args.startup_keyword:
                    keywords = self.args.startup_keyword
                    nwstart_p = re.compile(r'^\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2}.\d{3})\s+\d+\s+\d+\s+[A-Z]{1}\s+\w+\s*:\sStageManagerService.startStage line=\d+ verbose enter uri=\S*')
                    appshow_p = re.compile(r'^\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2}.\d{3})\s+\d+\s+\d+\s+[A-Z]{1}\s+\w+\s*:\s%s'%(keywords[0]))
                    blitzshow_p = re.compile(r'^\d{2}-\d{2}\s+(\d{2}:\d{2}:\d{2}.\d{3})\s+\d+\s+\d+\s+[A-Z]{1}\s+\w+\s*:\sfirst render end')
                    comsumetime = dict()
                    nwtime = dict()
                    with open(self.log, 'rb') as f:
                        n = 0
                        for i, line in enumerate(f):
                            line = line.decode('utf-8')  # 转换为字符串
                            start_info = re.search(nwstart_p, line)
                            if start_info:
                                n += 1
                                time_info0 = start_info.group(1)
                                nwtime[str(n)] = {'start': time_info0}
                            middle_info = re.search(blitzshow_p, line)
                            if middle_info:
                                time_info1 = middle_info.group(1)
                                nwtime[str(n)]['middle'] = time_info1
                            end_info = re.search(appshow_p, line)
                            if end_info:
                                time_info2 = end_info.group(1)
                                nwtime[str(n)]['end'] = time_info2
                        comsumetime = self.minis(nwtime)
                        f.close()
                    with open(os.path.join(log_dir, 'appstartuptime.txt'), 'w') as fp:
                        for (times, time) in comsumetime.items():
                            line = '{0:<10}{1:<10}{2:<10}'.format(times, time['t1'], time['t2'])
                            fp.write(line + '\n')
                    fp.close()

                self.last_chunk_id = 1
                self.chunk_log = self.open_log(self.last_chunk_id)
                self.error_log = self.open_log('error')
                self.warn_log = self.open_log('warn')
                self.fatal_log = self.open_log('fatal')
                with open(self.log, 'rb') as f:
                    for i, line in enumerate(f):
                        # line = line.decode('utf-8', errors='ignore')  # 忽略无效字节
                        mo_info = re.search(stats_p, line)
                        if mo_info:
                            mo_level = mo_info.group(1)
                            mo_name = mo_info.group(2)
                            stats = mo_stats.get(mo_name, {})
                            stats[mo_level] = stats.get(mo_level, 0) + 1
                            mo_stats[mo_name] = stats
                        if (i / self.last_chunk_id) >= 800000:
                            self.chunk_log.close()
                            self.last_chunk_id += 1
                            self.chunk_log = self.open_log(self.last_chunk_id)
                        line = line.replace('\r\r', '').replace('\r\n', '\n')
                        self.chunk_log.write(line)
                        if ' E ' in line:
                            self.error_log.write(line)
                        elif ' W ' in line:
                            self.warn_log.write(line)
                        elif ' F ' in line:
                            self.fatal_log.write(line)
                    self.chunk_log.close()
                    self.error_log.close()
                    self.warn_log.close()
                    self.fatal_log.close()
        with open(os.path.join(log_dir, 'logcat_modules'), 'w') as fp:
            for (name, stats) in mo_stats.items():
                total = sum(stats.values())
                stats['total'] = total
                sort_stats = [name]
                for key in ['V', 'D', 'I', 'W', 'E', 'F', 'S', 'total']:
                    sort_stats.append('(%s)%s' % (key, stats.get(key, 0)))
                line = '{0[0]:<40}{0[1]:<10}{0[2]:<10}{0[3]:<10}{0[4]:<10}{0[5]:<10}{0[6]:<10}{0[7]:<10}{0[8]:<10}'.format(sort_stats)
                fp.write(line + '\n')

    def open_log(self, suffix):
        log_file = '%s.%s.txt' % (self.log, suffix)
        logger.info(log_file)
        return open(log_file, 'w')
                
class LoopCommand(Command):
    def execute(self):
        if self.command:
            logger.debug('execute loop command %s' % self.command)
            with open(os.path.join(self.device.log_dir, '%s.txt' % self.name), 'a') as f:
                self.process = self.device.shell(self.command)
                f.write(">>%s>>\n%s\n" % (datetime.now().strftime('%m/%d %H:%M:%S'), self.device.get_process_stdout(self.process)))

class AnrLoopCommand(LoopCommand):
    def execute(self):
        logger.debug('execute loop command %s' % self.command)

        if not hasattr(self, 'timestamp'):
            if self.args.anr_dumpheap:
                self.device.get_process_stdout(self.device.shell('rm -rf /sdcard/anr_dump/'))
                self.device.get_process_stdout(self.device.shell('mkdir /sdcard/anr_dump/'))
            self.process = self.device.shell(self.command)
            self.timestamp = self.device.get_process_stdout(self.process)
            return
        self.process = self.device.shell(self.command)
        timestamp = self.device.get_process_stdout(self.process)
        if timestamp != self.timestamp:
            self.timestamp = timestamp
            with open(os.path.join(self.device.log_dir, '%s_%s.txt' % (self.name, datetime.now().strftime('%Y%m%d%H%M%S'))), 'w') as f:
                self.process = self.device.shell('cat /data/anr/traces.txt')
                f.write(self.device.get_process_stdout(self.process))
            if self.args.anr_dumpheap and self.args.process_names:
                ps_info = self.device.get_process_stdout(self.device.shell('ps'))
                pid_info = ''
                for line in ps_info.splitlines():
                    if self.args.process_names[0] in line:
                        pid_info = line
                        break
                logger.debug(pid_info)
                if pid_info:
                    try:
                        pid = int(pid_info.split()[1])
                        command = "am dumpheap %s /sdcard/anr_dump/anr_dumpheap_%s.hprof" % (pid, datetime.now().strftime('%Y%m%d_%H%M%S'))
                        logger.debug(command)
                        result = self.device.get_process_stdout(self.device.shell(command))
                        if result:
                            logger.error(result)
                    except Exception as e:
                        logger.error(str(e))

class AnrDumpHeapCommand(Command):
    def execute(self):
        self.device.adb('pull /sdcard/anr_dump/ %s' % os.path.join(self.device.log_dir, 'anr_dump'))
        logger.info('please remove /sdcard/anr_dump/ by your self')
   
class MemdetailLoopCommand(LoopCommand):
    def new(self, device, args):
        if args.process_names:
            self.command = 'dumpsys meminfo -a %s' % args.process_names[0]
        else:
            self.command = None
        return LoopCommand.new(self, device, args)

class ShowMapLoopCommand(LoopCommand):
    def new(self, device, args):
        if args.process_names:
            self.command = "ps | grep %s | awk '{print $2}' | xargs showmap" % args.process_names[0]
        else:
            self.command = None
        return LoopCommand.new(self, device, args)
    
class DumpheapLoopCommand(LoopCommand):
    def new(self, device, args):
        self.delay = args.dumpheap_interval * 60 / args.interval
        if self.delay < 10:
            self.delay = 10
        self.hprof = '/sdcard/dumpheap.hprof'
        self.clean_command = 'rm -f %s' % self.hprof
        self.i = 0
        return LoopCommand.new(self, device, args)
    
    def execute(self):
        if self.i == (self.delay - 5):
            logger.debug('execute loop command am dumpheap')
            self.clean()
            ps_info = self.device.get_process_stdout(self.device.shell('ps'))
            pid_info = ''
            for line in ps_info.splitlines():
                if self.args.process_names[0] in line:
                    pid_info = line
                    break
            logger.debug(pid_info)
            if pid_info:
                try:
                    pid = int(pid_info.split()[1])
                    self.command = "am dumpheap %s %s" % (pid, self.hprof)
                    logger.debug(self.command)
                    result = self.device.get_process_stdout(self.device.shell(self.command))
                    if result:
                        logger.error(result)
                except Exception as e:
                    logger.error(str(e))
        elif self.i == self.delay:
            self.i = 0
            self.device.adb('pull %s %s' % (self.hprof, os.path.join(self.device.log_dir, '%s_%s.hprof' % (self.name, datetime.now().strftime('%Y%m%d_%H%M%S')))))
            self.device.get_process_stdout(self.device.shell(self.clean_command))
        self.i += 1
            
#     def clean(self):
#         if self.clean_command:
#             logger.debug('execute loop clean command %s' % self.clean_command)
#             self.device.get_process_stdout(self.device.shell(self.clean_command))
            
            
class DurableCommand(Command):
    def execute(self):
        if self.command and self.is_done():
            # 如果是monkey命令，判断本地文件内容为0时继续启动monkey
            if 'monkey' in self.command and not GlobalVariables.is_stop_monkey:
                logger.debug('execute durable command %s' % self.command)
                self.clean()
                self.process = self.device.shell(self.command, os.path.join(self.device.log_dir, '%s_%s.txt' % (self.name, datetime.now().strftime('%Y%m%d_%H%M%S'))))
            else:
                logger.debug('execute durable command %s' % self.command)
                self.clean()
                self.process = self.device.shell(self.command, os.path.join(self.device.log_dir, '%s_%s.txt' % (self.name, datetime.now().strftime('%Y%m%d_%H%M%S'))))
            
    def clean(self):
        if self.clean_command:
            logger.debug('execute durable clean command %s' % self.clean_command)
            self.device.get_process_stdout(self.device.shell(self.clean_command))
            if self.process:
                self.process.wait()

MONKEYBLACKLIST = '/mnt/sdcard/tvb_monkey_blacklist.txt'
CYCLONE_MONKEYBLACKLIST = '/data/tvb_monkey_blacklist.txt'
MONKEYSCRIPT = '/mnt/sdcard/tvb_monkey_script.txt'
MONKEYSCRIPTTITLE = ['type = tvb_user', 'count = 1', 'speed = 1.0', 'start data >>']
MONKEYCMD = 'monkey -v -v -v --ignore-crashes --ignore-timeouts --ignore-security-exceptions --kill-process-after-error --monitor-native-crashes'
MONKEYCMDB = 'monkey -p {} -v -v -v -s 1000 --ignore-crashes --ignore-timeouts --ignore-security-exceptions --kill-process-after-error --pct-trackball 0 --pct-touch 0 --pct-motion 0 --pct-rotation 0 --pct-anyevent 0 --pct-flip 0 --pct-pinchzoom 0 --throttle 1500 1200000000 > /dev/null 2>&1 &'

CYCLONE_MONKEYCMD = 'monkey'
MONKEYCOUNT = 1200000000

MONKEYPCT = {'pct-touch': 0, 'pct-motion': 0, 'pct-trackball': 5, 'pct-nav': 55, 'pct-majornav': 15, 'pct-syskeys': 15, 'pct-appswitch': 9, 'pct-anyevent': 1}

class AppstartLoopCommand(DurableCommand):
    def new(self, device, args):
        self.clean_command = 'busybox pkill %s' % args.process_names[0]
        if args.process_names:
            self.command = 'nw start -n stage://%s' % args.process_names[0]
        else:
            self.command = None
        return DurableCommand.new(self, device, args)

class MonkeyDurableCommand(DurableCommand):
    def new(self, device, args):
        if device.cyclone:
            self.clean_command = 'busybox killall monkey'
        else:
            self.clean_command = 'busybox killall com.android.commands.monkey'
        return DurableCommand.new(self, device, args)
    
    def get_monkey_percent(self, args):
        percent = []
        for pct in MONKEYPCT:
            if hasattr(args, pct):
                value = getattr(args, pct)
                if value is not None:
                    percent.append('--%s %s' % (pct, value))
        if percent:
            return ' '.join(percent)
        return ' '.join(['--%s %s' % (k, v) for k, v in MONKEYPCT.items() if v])

class AppMonkeyDurableCommand(MonkeyDurableCommand):
    def new(self, device, args):
        extra = ''
        if args.monkey:
            extra = '-p ' + ' -p '.join(args.monkey)
        if device.cyclone:
            self.command = '%s %s -t %s -w %s' % (CYCLONE_MONKEYCMD, extra, args.throttle, args.wait_app_startup)
        else:
            self.command = '%s %s %s --throttle %s %s' % (MONKEYCMD, self.get_monkey_percent(args), extra, args.throttle, MONKEYCOUNT)
        return MonkeyDurableCommand.new(self, device, args)
    
class BlacklistMonkeyDurableCommand(MonkeyDurableCommand):
    def new(self, device, args):
        if args.blacklist:
            cmd = "echo '%s' > %s" % ('\\n'.join(args.blacklist), CYCLONE_MONKEYBLACKLIST if device.cyclone else MONKEYBLACKLIST)
            device.shell(cmd)
            if device.cyclone:
                extra = '-black_list_file %s' % CYCLONE_MONKEYBLACKLIST
                self.command = '%s %s -t %s -w %s' % (CYCLONE_MONKEYCMD, extra, args.throttle, args.wait_app_startup)
            else:
                extra = '--pkg-blacklist-file %s' % MONKEYBLACKLIST
                self.command = '%s %s %s --throttle %s %s' % (MONKEYCMD, self.get_monkey_percent(args), extra, args.throttle, MONKEYCOUNT)
        else:
            self.command = None
        return MonkeyDurableCommand.new(self, device, args)
    
class ScriptMonkeyDurableCommand(MonkeyDurableCommand):
    def new(self, device, args):
        if args.script:
            with open(args.script, 'r') as f:
                cmd = "echo '%s' > %s" % ('\\n'.join(MONKEYSCRIPTTITLE + f.read().splitlines()), MONKEYSCRIPT)
                device.shell(cmd)
                extra = '-f %s ' % MONKEYSCRIPT
                self.command = '%s %s --throttle %s %s' % (MONKEYCMD, extra, args.throttle, MONKEYCOUNT)
        else:
            self.command = None
        return MonkeyDurableCommand.new(self, device, args)

class DumpMemInfoCommand(Command):
    def execute(self):
        if self.command:
            logger.debug('execute loop command %s' % self.command)
            self.process = self.device.shell(self.command)
            memInfo = self.device.get_process_stdout(self.process)
            # print(memInfo)
            with open(os.path.join(self.device.log_dir, '%s.txt' % self.name), 'a') as f:
                f.write(">>%s>>\n%s\n" % (datetime.now().strftime('%m/%d %H:%M:%S'), memInfo))
                f.close()
            if GlobalVariables.mem_list is not None and len(GlobalVariables.mem_list) > 0:
               mem_size = self.get_package_mem(memInfo)
               h =DumpHProf(args=None,device=self.device.address)
               h.dump_memBysize(mem_size)


    # def get_package_mem(self,text):
    #     pattern = r"\s*([\d,]+)K:\s*"+GlobalVariables.package
    #     match = re.search(pattern, text)
    #     if match:
    #         mem_kb_str = match.group(1)
    #         mem_kb = int(mem_kb_str.replace(',', ''))  # 转换为整数, 去掉逗号
    #         mem_mb = mem_kb / 1024  # 将 KB 转换为 MB
    #         return mem_mb
    #     else:
    #         return 0

    def get_package_mem(self, text):
        # 方式1：优先解析 dumpsys meminfo <package> 的 TOTAL PSS
        match = re.search(r'TOTAL\s+PSS:\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1)) / 1024.0

        pss_block_match = re.search(
            r'^Total PSS by process:\s*$(.*?)$(?=^\w|\Z)',
            text,
            re.MULTILINE | re.DOTALL
        )
        if pss_block_match:
            pss_block = pss_block_match.group(1)
            # 在 PSS 区块内搜索目标包
            pattern = r"^\s*([\d,]+)K:\s*" + re.escape(GlobalVariables.package) + r"\s*\(pid\s+\d+"
            for line in pss_block.splitlines():
                if re.match(pattern, line.strip()):
                    mem_kb_str = re.match(pattern, line.strip()).group(1)
                    mem_kb = int(mem_kb_str.replace(',', ''))
                    return mem_kb / 1024.0
        logger.warning("Failed to extract PSS memory for package: %s", GlobalVariables.package)
        return 0


COMMAND_CONFIG = {
    'top': LoopCommand('top', 'top -n 1'),
    'uptime': LoopCommand('uptime', 'uptime'),
    'free': LoopCommand('free', 'busybox free -m'),
    'procrank': LoopCommand('procrank', 'procrank'),
    # 'meminfo': LoopCommand('meminfo', 'dumpsys meminfo'),
    'cpuinfo': LoopCommand('cpuinfo', 'dumpsys cpuinfo'),
    'mali': LoopCommand('mali', 'librank -P /dev/mali'),
    'activity': LoopCommand('activity', 'dumpsys activity'),
    'oom': LoopCommand('activity_oom', 'dumpsys activity oom'),
    'processes': LoopCommand('activity_processes', 'dumpsys activity processes'),
    'procstats': LoopCommand('activity_procstats', 'dumpsys activity procstats'),
    'temp0': LoopCommand('temperature_zone0', 'cat /sys/class/thermal/thermal_zone0/temp'),
    'temp1': LoopCommand('temperature_zone1', 'cat /sys/class/thermal/thermal_zone1/temp'),
    'anr': AnrLoopCommand('anr', 'ls -l /data/anr/traces.txt'),
    'memdetail': MemdetailLoopCommand('memdetail'),
    'showmap': ShowMapLoopCommand('showmap'),
    'dumpheap': DumpheapLoopCommand('dumpheap'),
    'appstartup': AppstartLoopCommand('appstartup'),

    'logcat': DurableCommand('logcat', 'logcat -v threadtime', 'busybox killall logcat'),
    'event': DurableCommand('logcat_event', 'logcat -v threadtime -b events'),
    'kmsg': DurableCommand('kmsg', 'busybox cat /dev/kmsg', 'busybox killall busybox'),
    
    'monkey': AppMonkeyDurableCommand('monkey'),
    'script': ScriptMonkeyDurableCommand('monkey'),
    'meminfo': DumpMemInfoCommand('meminfo', 'dumpsys meminfo'),
    'meminfoTime': DumpMemInfoCommand('meminfo', 'dumpsys -t 20 meminfo'),

}

LAST_COMMAND_CONFIG = {
    'bugreport': LastCommand('bugreport', 'bugreport'),
    'usagestats': LastCommand('usagestats', 'dumpsys usagestats'),
    'logcatparser': LogcatParserCommand('logcat', ''),
    'tombstone': TombstonesCommand('tombstone', ''),
    'anrdumpheap': AnrDumpHeapCommand('anrdumpheap', '')
}
UPLOAD_FILE_CONFIG = ['cpuinfo.txt', 'meminfo.txt', 'top.txt','memdetail.txt']
excluded = ['monkey', 'blacklist', 'script', 'logcatparser']
support_commands = sorted([key for key in COMMAND_CONFIG.keys() if key not in excluded] + list(LAST_COMMAND_CONFIG.keys()))
default_commands = sorted(['top', 'cpuinfo', 'meminfo', 'logcat', 'anr', 'bugreport', 'free'])
