# encoding: utf-8
'''
@author:     Juncheng Chen

@copyright:  1999-2015 Alibaba.com. All rights reserved.

@license:    Apache Software License 2.0

@contact:    juncheng.cjc@outlook.com
'''
import json
import sys
import os
import threading
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from time import sleep, time
from threading import Timer

from tvb.command import support_commands, default_commands, LogcatParserCommand, UPLOAD_FILE_CONFIG
from tvb.config import Config
from tvb.dump_hprof import DumpHProf
from tvb.report import Report
from tvb.upload import Upload
from tvb.namespace import GlobalVariables
import logging

logger = logging.getLogger(__name__)

__version__ = '2.1.7'
__date__ = '2015-09-10'
__updated__ = '2025-10-21'

DEBUG = True


def get_version():
    return __version__


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_version_message = __version__
    program_license = '''tvb -- TV Bridge

  Created by Juncheng Chen on %s.
  Copyright 2015 Alibaba.com. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (__date__)

    try:
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-d', dest="devices", help=u"device ip address or name", metavar="ip_address", nargs='*')
        parser.add_argument('-c', dest="commands", choices=support_commands,
                            help=u"collection commands, default %(default)s", default=default_commands, nargs='*')
        parser.add_argument('-l', '--log', dest="log_dir", help=u"specify the file path where to store logs",
                            default=os.path.abspath('.'), metavar="log path", nargs='?')
        parser.add_argument('-t', '--time', dest="time", type=float, help=u"execution time, unit(minutes)", default=-1,
                            metavar="minutes", nargs='?')
        parser.add_argument('-i', '--interval', dest="interval", type=int,
                            help=u"time interval of command, unit(seconds), default %(default)s seconds", default=15,
                            metavar="seconds", nargs='?')
        parser.add_argument('-p', '--process', dest="process_names",
                            help=u"specify process names to generate line chart", metavar="process names", nargs='*')
        parser.add_argument('-k', '--startkeyword', dest="startup_keyword", help=u"specify keyword to locate app start",
                            metavar="key words", nargs='*')
        parser.add_argument('-m', '--monkey', dest="monkey",
                            help=u"monkey will only allow the system to visit activities within those packages",
                            metavar="packages", nargs='*')
        parser.add_argument('-b', '--blacklist', dest="blacklist",
                            help=u"monkey will not allow the system to visit activities within those packages",
                            metavar="packages", nargs='+')
        parser.add_argument('-s', '--script', dest="script", help=u"monkey will repeat run according the script",
                            metavar="script_path", nargs='?')
        parser.add_argument('-o', '--throttle', dest="throttle", type=int,
                            help=u"inserts a fixed delay between monkey events, unit(millisecond), default %(default)s millisecond",
                            default=500, metavar="millisecond", nargs='?')
        parser.add_argument('-w', '--waitapp', dest="wait_app_startup", type=int,
                            help=u"inserts a fixed delay after application startup, unit(millisecond), default %(default)s millisecond",
                            default=500, metavar="millisecond", nargs='?')
        parser.add_argument('-u', '--user', dest="emp_id", help=u"execution manual number", metavar="emp_id", nargs='?')
        parser.add_argument('-upload', '--upload', dest="is_upload", help=u"Upload the generated file",
                            metavar="is_upload", type=bool, const=True, default=True, nargs='?', )

        parser.add_argument('--anr-dumpheap', dest="anr_dumpheap", help=u"dumpheap when anr", action="store_true",
                            default=False)
        parser.add_argument('--dumpheap-interval', dest="dumpheap_interval", type=float,
                            help=u"dumpheap interval, unit(minutes)", default=60, metavar="minutes", nargs='?')

        parser.add_argument('--pct-touch', dest="pct-touch", type=int, help=u"adjust percentage of touch events.",
                            metavar="percentage", nargs='?')
        parser.add_argument('--pct-motion', dest="pct-motion", type=int, help=u"adjust percentage of motion events.",
                            metavar="percentage", nargs='?')
        parser.add_argument('--pct-trackball', dest="pct-trackball", type=int,
                            help=u"adjust percentage of trackball events, default 5", metavar="percent", nargs='?')
        parser.add_argument('--pct-nav', dest="pct-nav", type=int,
                            help=u'adjust percentage of "basic" navigation events, default 55', metavar="percent",
                            nargs='?')
        parser.add_argument('--pct-majornav', dest="pct-majornav", type=int,
                            help=u'adjust percentage of "major" navigation events, default 15', metavar="percent",
                            nargs='?')
        parser.add_argument('--pct-syskeys', dest="pct-syskeys", type=int,
                            help=u'adjust percentage of "system" key events, default 15', metavar="percent", nargs='?')
        parser.add_argument('--pct-appswitch', dest="pct-appswitch", type=int,
                            help=u'adjust percentage of activity launches, default 9', metavar="percent", nargs='?')
        parser.add_argument('--pct-anyevent', dest="pct-anyevent", type=int,
                            help=u'adjust percentage of other types of events, default 1', metavar="percent", nargs='?')

        parser.add_argument("-r", "--report", dest="report", help=u"regenerate excel report", metavar="report path",
                            nargs='?')
        parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0, help=u"verbose level")
        parser.add_argument('-V', '--version', action='version', help=u"show version and exit",
                            version=program_version_message)
        parser.add_argument("-j", "--json", dest="json", help=u"regenerate json report", metavar="report path",
                            nargs='?')
        parser.add_argument("-a", "--activity", dest="activity", help=u"dump hprof star activity",
                            metavar="activity path", nargs='?',
                            default=u"com.youku.taitan.tv/com.youku.android.devtools.activities.BasicInfoActivity",
                            const="com.youku.taitan.tv/com.youku.android.devtools.activities.BasicInfoActivity")
        parser.add_argument("-mem", "--mem_list", dest="mem_list", help=u"memory threshold list", type=int,
                            metavar="mem list", nargs='*')
        parser.add_argument('-n', '--native', dest="is_native", help=u"Produce native files", metavar="is_native",
                            type=bool, const=True, default=False, nargs='?', )

        # Process arguments
        args = parser.parse_args()
        # 初始化全局参数
        GlobalVariables.package = args.process_names[0]
        GlobalVariables.is_native = args.is_native
        logging.basicConfig(level=logging.INFO if args.verbose == 0 else logging.DEBUG,
                            format='%(asctime)s %(levelname)-5s %(message)s',
                            datefmt='%y-%m-%d %H:%M:%S')
        logger.debug(args)
        if not args.devices and not args.report and not args.json:
            raise Exception
        if not args.emp_id:
            logger.info('请增加执行人工号，例如 -u wb123')
            raise Exception('请增加执行人工号，例如 -u wb123')

        if args.report:
            logger.info('report dir %s' % args.report)
            r = Report(args.report, args.process_names)
            for device_dir in r.list_device_dirs():
                LogcatParserCommand('logcatParser').execute(os.path.join(args.report, device_dir))
            return 0
        if args.monkey is not None:
            args.commands.insert(0, 'monkey')
            GlobalVariables.is_monkey = True
            if not args.process_names:
                args.process_names = args.monkey
        # if args.json:
        #     jsonReport = JsonReport(args.json, args.process_names)

        if args.blacklist:
            args.commands.insert(0, 'blacklist')

        if args.script:
            args.commands.insert(0, 'script')

        if 'logcat' in args.commands:
            args.commands.append('logcatparser')

        if 'anr' in args.commands and args.anr_dumpheap:
            args.commands.append('anrdumpheap')
        if args.activity is not None:
            GlobalVariables.activity = args.activity
        if args.mem_list is not None and len(args.mem_list) > 0:
            GlobalVariables.mem_list = args.mem_list

        config = Config(args)
        total_time = args.time * 60 if args.time > 0 else None
        timeout = len(config.commands) * 10 + 5

        def watchdog():
            logger.error('watchdog %s seconds timeout' % timeout)
            for command in config.commands:
                command.kill()

        logger.info('start collection')

        try:
            while total_time is None or total_time > 0:
                timer = Timer(timeout, watchdog)
                # timer.setDaemon(True)
                timer.start()
                logger.debug('watchdog start')
                before = time()
                for command in config.commands:
                    command.execute()
                # python版本小于等于使用timer.isAlive()
                try:
                    alive = timer.is_alive()
                except AttributeError:
                    alive = timer.isAlive()
                if alive:
                    timer.cancel()
                    logger.debug('watchdog cancel')
                timer.join()
                if total_time is not None:
                    total_time -= args.interval
                    logger.debug("remain time: %s sec." % total_time)
                delta = time() - before
                if delta < args.interval:
                    sleep(args.interval - delta)
        except KeyboardInterrupt:
            logger.info('KeyboardInterrupt')
        # try:
        #     stop_event = threading.Event()
        #
        #     def watchdog():
        #         if not stop_event.is_set():
        #             logger.error('Command execution timeout!')
        #             # 执行超时处理逻辑
        #             for command in config.commands:
        #                 command.kill()
        #
        #     while total_time is None or total_time > 0:
        #         if stop_event.is_set():
        #             break
        #
        #         timer = threading.Timer(timeout, watchdog)
        #         timer.daemon = True  # 设置为守护线程
        #
        #         before = time()
        #         timer.start()
        #         logger.debug('watchdog start')
        #
        #         try:
        #             # 执行命令
        #             for command in config.commands:
        #                 if stop_event.is_set():
        #                     break
        #                 command.execute()
        #
        #             # 检查定时器状态并取消
        #             if timer.is_alive():
        #                 timer.cancel()
        #                 logger.debug('watchdog cancel')
        #
        #         except Exception as e:
        #             logger.error(f'Command execution error: {e}')
        #             timer.cancel()
        #             stop_event.set()
        #             break
        #
        #         # 计算剩余时间
        #         if total_time is not None:
        #             total_time -= args.interval
        #             logger.debug("remain time: %s sec." % total_time)
        #
        #         # 等待间隔时间
        #         delta = time() - before
        #         if delta < args.interval and not stop_event.is_set():
        #             sleep(args.interval - delta)
        #
        # except KeyboardInterrupt:
        #     logger.info('KeyboardInterrupt')
        #     stop_event.set()
        for command in config.commands:
            command.clean()
            # hprof_thread.stop()
            # hprof_thread.join()

        if config.last_commads:
            logger.info('please wait a moment')

        logger.info('collection finish')
        Report(config.log_dir, args.process_names)

        # 上传tvb数据
        if args.is_upload:
            logger.info("upload data start")
            Upload(config,args)

        # for command in config.last_commads:
        #     command.execute()
            # pass

        logger.info('finish')
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        if DEBUG:
            print(e)
            raise
        sys.stderr.write(str(e) + "\n")
        sys.stderr.write("  for help use --help")
        return 2


if __name__ == '__main__':
    # main(['-v', '-d', '192.168.10.177:5555', '-c', 'meminfo', 'cpuinfo', 'top', '-p', 'com.youku.taitan.tv', '-m', 'com.youku.taitan.tv',
    #       '-a','yunostv_homeshell://start_home' ,'-mem','200' ,'240','300', '-l','/Users/wjh/Documents/output/tvb'])
    # main(['-v', '-d', '30.11.32.142', '-c', 'uptime', 'free', 'top', '-p', 'node', '-m', 'bluray.tv.yunos.com', 'settings.tv.yunos.com', '-o', '800', '-w', '900'])
    # main(['-r', '/Users/wjh/Documents/output/2025.07.09-15.40.24',  '-p', 'com.cibn.tv', ])
    main(['-v', '-d', '192.168.10.242:5555', '-c', 'meminfo', 'cpuinfo', 'top', 'logcat', '-p', 'com.youku.taitan.tv',
          '-l', '/Users/wjh/Documents/output/tvb', '-m', 'com.youku.taitan.tv', '-u', 'WB01366562', '-t', '25',
          '-mem', '400', '450', '480', '500', '560', '800'])
