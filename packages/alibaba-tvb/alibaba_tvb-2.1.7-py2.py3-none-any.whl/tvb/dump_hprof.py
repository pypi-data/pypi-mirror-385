import threading
import time
from datetime import datetime
import subprocess
import re

from tvb.namespace import GlobalVariables

class DumpHProf(threading.Thread):
    globals()["Fail_flag"] = True

    def __init__(self, args=None,device=''):
        threading.Thread.__init__(self)
        if args is None:
            args = {}
        # self.args = args
        # self.package_name = args.process_names[0]
        self.devices = device
        # self.mem_list = args.mem_list
        # print(args.activity)
        # print(args.mem_list)
        # self.activity = args.activity

    def run(self):
        is_monkey =False
        if self.args.monkey is not None:
            is_monkey =True
            print('start dump_hprof')
        while globals()["Fail_flag"]:
            time.sleep(20)
            try:
                mem = self.get_mem()
                print('当前内存:%sMB' % self.KB_to_MB(mem))
                if len(self.mem_list) > 0:
                    if int(mem) > min(self.mem_list) * 1024:
                        if is_monkey:
                            GlobalVariables.is_stop_monkey = True
                            self.stop_monkey()
                        if self.activity:
                            subprocess.call('adb -s {} shell am start {}'.format(self.devices,self.activity),
                                            shell=True)
                        self.dump_mem()
                        for item in self.mem_list.copy():
                            if int(mem) > item * 1024:
                                print('移除内存阈值%d' % item)
                                self.mem_list.remove(item)
                                break
            except Exception as e:
                print(e)
                print('获取不到内存信息')
    def dump_memBysize(self, mem_size = 0):
        if int(mem_size) > min(GlobalVariables.mem_list) :
            if GlobalVariables.is_monkey:
                GlobalVariables.is_stop_monkey = True
                self.stop_monkey()
            if GlobalVariables.activity:
                subprocess.call('adb -s {} shell am start {}'.format(self.devices, GlobalVariables.activity),
                                shell=True)
                time.sleep(30)
            self.dump_mem()
            if GlobalVariables.is_native:
                self.dump_active()
            for item in GlobalVariables.mem_list.copy():
                if int(mem_size) > item:
                    print('移除内存阈值%d' % item)
                    GlobalVariables.mem_list.remove(item)
                    break

    def stop(self):
        globals()["Fail_flag"] = False
        print('stop dump_hprof')

    def get_mem(self):
        """
        获取mem
        :return:
        """
        info_list = subprocess.check_output('adb -s {} shell dumpsys meminfo'.format(self.devices),shell=True)
        try:
            req = re.compile(r"(\d+) kB: |(\d+)K: " + self.package_name)
            result_list = req.findall(str(info_list).replace(",", ""))[0]
            if result_list[0] != "":
                return result_list[0]
            else:
                return result_list[1]
        except Exception as e:
            print(info_list)

    def dump_mem(self):
        subprocess.call(
            'adb -s {} shell am startservice -n '.format(self.devices) + GlobalVariables.package +
            '/com.yunos.tv.yingshi.debug.DumpHeapService -a DUMP_HEAP_ACTION',shell=True)
        time.sleep(30)
        # subprocess.call(
        #     'adb -s {} shell am startservice -n '.format(self.devices) + GlobalVariables.package +
        #     '/com.yunos.tv.yingshi.debug.DumpHeapService -a DUMP_THREAD_ACTION',shell=True)
        print('dump 内存完毕')
    def dump_active(self):
        subprocess.call(
            'adb -s {} shell am startservice -n '.format(self.devices) + GlobalVariables.package +
            '/com.youku.tv.ux.monitor.DumpService -a dump_memory_info', shell=True)
        time.sleep(30)
        subprocess.call(
            'adb -s {} shell am startservice -n '.format(self.devices) + GlobalVariables.package +
            '/com.yunos.tv.yingshi.debug.DumpHeapService -a MMAP_ACTION', shell=True)
        time.sleep(30)

    def KB_to_MB(self, kb):
        return format(int(kb) / 1024, '.2f')

    def stop_monkey(self):
        pid = self.get_monkey_pid()
        subprocess.call('adb -s {} shell "kill -9 {}"'.format(self.devices, pid), shell=True)
    def get_monkey_pid(self):
        try:
            # 使用 adb shell ps 命令获取所有进程的信息
            # command = ["adb", "shell", "ps"]
            command = 'adb -s {} shell ps'.format(self.devices)
            result = subprocess.run(command, capture_output=True, text=True, check=True,shell=True)

            # 在输出中查找包含 'com.android.commands.monkey' 的行
            for line in result.stdout.splitlines():
                if 'com.android.commands.monkey' in line:
                    # 根据输出格式，通常第二列是 PID，打印或返回它
                    parts = line.split()
                    pid = parts[1]  # PID 通常在第二列，但这可能因设备而异
                    print(f"Monkey PID: {pid}")
                    return pid

            print("No Monkey process found.")
            return None

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while fetching process information: {e}")
            return None

