
import os
from tvb.command import UPLOAD_FILE_CONFIG
from tvb.json_report import JsonReport
import zipfile
import subprocess
import logging
import requests
import json
import time

logger = logging.getLogger(__name__)


class Upload(object):

    def __init__(self,config, args):
        devices = ''
        if ':' in args.devices:
            devices = args.devices.split(':')[0]
        else:
            devices = args.devices
        jsonReport = JsonReport(config.log_dir, args.process_names)
        path = os.path.join(config.log_dir, devices[0])
        try:
            result_data_path = self.upload_result_data(jsonReport.result_path)
            self.upload_data(path, args, result_data_path)
        except Exception as e:
            logger.info('文件上传失败')
    # 上传mem top cpu 等数据


    # 上传resultData数据
    def upload_result_data(self,file_path):
        logger.info("upload result data start")
        oss_file_url = None
        files = {'file': open(file_path, 'rb')}
        r = requests.post('https://pans.alibaba-inc.com/api/oss/commonUpload', files=files)  # 发起POST请求，将文件内容传入
        # 打印服务器返回的结果
        data = json.loads(r.text)
        logger.info(r.text)
        if "SUCCESS" in data['message']:
            oss_file_url = data['data']
            return oss_file_url
        return oss_file_url

    def upload_data(self,path, args,result_data_path):
        ip = args.devices[0]
        self.reconnect(ip)
        urlArr = []
        package = args.process_names[0]
        versionName = ''
        versionCode = ''
        for name in UPLOAD_FILE_CONFIG:
            file_path = os.path.join(path, name)
            file_url = self.uploadFile(file_path, name)
            urlArr.append(file_url)
        release = subprocess.check_output('adb -s {} shell "getprop ro.build.version.release"'.format(ip), shell=True).decode(
            'utf-8').strip()
        model = subprocess.check_output('adb -s {} shell "getprop ro.product.model"'.format(ip), shell=True).decode('utf-8').strip()
        uuid = subprocess.check_output('adb -s {} shell "getprop ro.aliyun.clouduuid"'.format(ip), shell=True).decode('utf-8').strip()
        if package:
            versionName = self.get_version_name(package,ip)
            versionCode = self.get_version_code(package,ip)
        device = {"empId": args.emp_id, "sysVersion": release, "deviceModel": model, "uuid": uuid,
                  "packageName": package, "versionName": versionName,
                  "versionCode": versionCode, "cpuInfo": urlArr[0], "memInfo": urlArr[1], "top": urlArr[2],
                  "memDetail": urlArr[3],"resultData":result_data_path}
        print(device)
        requests.post('http://pans.alibaba-inc.com/api/sh/autotest/tvb/insert', json=device)

    def get_version_name(slef,package_name,ip):
        response = subprocess.Popen(f'adb -s {ip} shell "dumpsys package {package_name} |grep versionName" ', stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True).communicate()[0].decode()
        result = str(response).split()[0].split('=')[1].strip()
        return result

    def get_version_code(self,package_name,ip):
        response = subprocess.Popen(f'adb -s {ip} shell "dumpsys package {package_name} |grep versionCode" ', stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True).communicate()[0].decode()
        result = str(response).split()[0].split('=')[1].strip()
        return result
    def uploadFile(self,file_path, file_name):
        oss_file_url = None
        if os.path.isfile(file_path):
            zip_file = self.create_zip(file_path, file_path + '.zip', file_name)
            files = {'file': open(zip_file, 'rb')}  # 指定要上传的文件，以字典形式传入，文件名为'file.txt'

            r = requests.post('https://pans.alibaba-inc.com/api/oss/commonUpload', files=files)  # 发起POST请求，将文件内容传入
            # 打印服务器返回的结果
            data = json.loads(r.text)
            if "SUCCESS" in data['message']:
                oss_file_url = data['data']
                return oss_file_url
        return oss_file_url

    def create_zip(self,file_path, zip_file_name, file_name):
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 只将文件写入 ZIP，arcname 是存储在 ZIP 中的文件名
            zipf.write(file_path, arcname=file_name)
            zipf.close()
        return zip_file_name
    def reconnect(self,ip):

        result = subprocess.getoutput('adb devices')
        if 'offline' in result or ip not in result:
            subprocess.call('adb disconnect {}'.format(ip), shell=True)
            time.sleep(10)
            subprocess.call('adb connect {}'.format(ip), shell=True)