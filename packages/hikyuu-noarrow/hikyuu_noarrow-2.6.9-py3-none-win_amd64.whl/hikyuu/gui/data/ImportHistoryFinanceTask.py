# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) fasiondog/hikyuu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shutil
import hashlib
import sqlite3
import mysql.connector
import clickhouse_connect
from pytdx.hq import TdxHq_API
from hikyuu.data.pytdx_finance_to_mysql import history_finance_import_mysql
from hikyuu.data.pytdx_finance_to_sqlite import history_finance_import_sqlite
from hikyuu.data.pytdx_finance_to_clickhouse import history_finance_import_clickhouse
from hikyuu.util import *


class ImportHistoryFinanceTask:
    def __init__(self, log_queue, queue, config, dest_dir):
        self.log_queue = log_queue
        self.queue = queue
        self.config = config
        self.dest_dir = dest_dir + '/downloads/finance'
        if not os.path.lexists(self.dest_dir):
            os.makedirs(self.dest_dir)
        self.task_name = 'IMPORT_FINANCE'
        self.total_count = 0
        self.status = "no run"

    def connect_to_pytdx(self):
        api = TdxHq_API()
        # 不是所有服务器都提供下载
        hku_check(api.connect('120.76.152.87', 7709), "failed connect pytdx!")
        return api

    def get_list_info(self):
        content = self.api.get_report_file_by_size('tdxfin/gpcw.txt')
        content = content.decode('utf-8')
        content = content.strip().split('\r\n')

        def l2d(item):
            return {'filename': item[0], 'hash': item[1], 'filesize': int(item[2])}

        return [l2d(i.strip().split(',')) for i in content]

    def connect_db(self):
        if self.config.getboolean('hdf5', 'enable', fallback=True):
            sqlite_file = "{}/stock.db".format(self.config['hdf5']['dir'])
            self.db_connect = sqlite3.connect(sqlite_file, timeout=1800)
            self.history_finance_import = history_finance_import_sqlite
            self.engine = 'hdf5'
        elif self.config.getboolean('mysql', 'enable', fallback=True):
            db_config = {
                'user': self.config['mysql']['usr'],
                'password': self.config['mysql']['pwd'],
                'host': self.config['mysql']['host'],
                'port': self.config['mysql']['port']
            }
            self.db_connect = mysql.connector.connect(**db_config)
            self.history_finance_import = history_finance_import_mysql
            self.engine = 'mysql'
        elif self.config.getboolean('clickhouse', 'enable', fallback=True):
            db_config = {
                'username': self.config['clickhouse']['usr'],
                'password': self.config['clickhouse']['pwd'],
                'host': self.config['clickhouse']['host'],
                'port': self.config['clickhouse']['http_port']
            }
            self.db_connect = clickhouse_connect.get_client(**db_config)
            self.history_finance_import = history_finance_import_clickhouse
            self.engine = 'clickhouse'

    def import_to_db(self, filename):
        try:
            self.history_finance_import(self.db_connect, filename)
        except Exception as e:
            hku_error(str(e))

    def download_file(self, item, dest_dir):
        filename = item['filename']
        dest_file_name = dest_dir + "/" + filename
        need_download = False
        if not os.path.exists(dest_file_name):
            need_download = True
        else:
            old_md5 = ''
            with open(dest_file_name, 'rb') as f:
                old_md5 = hashlib.md5(f.read()).hexdigest()
            if old_md5 != item['hash']:
                need_download = True

        if need_download:
            api = TdxHq_API()
            # 不是所有服务器都提供下载
            hku_check(api.connect('120.76.152.87', 7709), "failed connect pytdx!")
            data = api.get_report_file_by_size(f'tdxfin/{filename}', 0)
            hku_info(f"Download finance file: {filename}")
            with open(dest_file_name, 'wb') as f:
                f.write(data)
            api.disconnect()

        shutil.unpack_archive(dest_file_name, extract_dir=dest_dir)
        self.import_to_db(f'{dest_dir}/{filename[0:-4]}.dat')
        hku_info(f"Import finance file: {dest_dir}/{filename[0:-4]}.dat")

    @hku_catch(trace=True)
    def __call__(self):
        self.status = "running"
        capture_multiprocess_all_logger(self.log_queue)
        self.api = self.connect_to_pytdx()
        data_list = self.get_list_info()
        self.total_count = len(data_list)
        count = 0
        data_list.sort(key=lambda x: x['filename'])

        self.connect_db()
        for item in data_list:
            try:
                self.download_file(item, self.dest_dir)
                count += 1
                self.queue.put([self.task_name, None, None, int(100 * count / self.total_count), self.total_count])
            except Exception as e:
                hku_error(str(e))
        if self.engine == 'clickhouse':
            hku_run_ignore_exception(self.db_connect.command, "OPTIMIZE TABLE hku_base.historyfinance FINAL")
        self.db_connect.close()
        self.api.disconnect()

        self.queue.put([self.task_name, None, None, None, self.total_count])
        self.status = "finished"


if __name__ == "__main__":
    from multiprocessing import Queue
    from configparser import ConfigParser
    this_dir = os.path.expanduser('~') + '/.hikyuu'
    import_config = ConfigParser()
    import_config.read(this_dir + '/importdata-gui.ini', encoding='utf-8')
    task = ImportHistoryFinanceTask(None, None, import_config, "/Users/fasiondog/stock")
    task()
    print("over!")
