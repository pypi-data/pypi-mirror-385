# encoding: utf-8
'''
@author:     shanzhou.csz
'''
import os
import json

from tvb.info2 import INFO_CONFIG

import logging
import time

logger = logging.getLogger(__name__)


class JsonReport(object):
    def __init__(self, log_dir, process_names=[]):
        os.chdir(log_dir)
        data_dict = {}
        result_path = ''
        if process_names is None:
            process_names = []
        self.process_names = process_names
        for device_dir in self.list_device_dirs():
            logger.info('create json report for %s' % device_dir)
            core_num = 1
            try:
                with open(os.path.join(device_dir, 'corenum.txt'), 'r') as f:
                    core_num = int(f.read())
            except:
                pass
            file_names = self.filter_file_names(device_dir)
            logger.debug('%s' % file_names)
            if file_names:
                for file_name in file_names:
                    name = file_name.split('.')[0]
                    info = INFO_CONFIG.get(name)(device_dir, file_name, process_names, core_num)
                    logging.debug('get report config %s' % info)
                    sheet_data = []
                    for sheet in info.get_sheet_list():
                        sheet_data.append(self.add_json(*sheet))
                    data_dict[name] = sheet_data
        json_result = json.dumps(data_dict)
        fp = open("tvbResult.txt", "w")
        fp.write(json_result)
        result_path = os.path.abspath(fp.name)
        self.result_path = result_path
        fp.close()

    def list_device_dirs(self):
        return [d for d in os.listdir('.') if os.path.isdir(d)]

    def filter_file_names(self, device):
        return [f for f in os.listdir(device) if
                os.path.isfile(os.path.join(device, f)) and f.split('.')[0] in INFO_CONFIG.keys()]

    def add_json(self, sheet_name, x_axis, y_axis, headings, lines):
        json_data = {}
        ws_data = {}
        columns = len(headings)
        rows = len(lines)
        for i in range(1, columns):
            item_data = []
            for j in range(0, rows):
                result = lines[j][i]
                if type(result) == str and result == "":
                    result = None
                if type(lines[j][0]) == str and lines[j][0].isdigit():
                    lines[j][0] = int(lines[j][0])
                item_data.append([lines[j][0], result])
            ws_data[headings[i]] = item_data
        json_data["title"] = sheet_name
        json_data["data"] = ws_data
        json_data["yTitle"] = y_axis
        json_data["xTitle"] = x_axis
        return json_data
