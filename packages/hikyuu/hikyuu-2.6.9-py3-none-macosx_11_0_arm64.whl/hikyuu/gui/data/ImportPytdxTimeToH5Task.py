# coding:utf-8
#
# The MIT License (MIT)
#
# Copyright (c) 2010-2017 fasiondog/hikyuu
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

import logging
import sqlite3
import mysql.connector
import clickhouse_connect
from pytdx.hq import TdxHq_API
from hikyuu.data.pytdx_to_h5 import import_time as h5_import_time
from hikyuu.data.pytdx_to_mysql import import_time as mysql_import_time
from hikyuu.data.pytdx_to_clickhouse import import_time as clickhouse_import_time
from hikyuu.util import *


class ProgressBar:
    def __init__(self, src):
        self.src = src

    def __call__(self, cur, total):
        progress = (cur + 1) * 100 // total if total > 0 else 100
        # hku_info(f"{self.src.market} 分时数据: {progress}%")
        self.src.queue.put([self.src.task_name, self.src.market, 'TIME', progress, 0])


class ImportPytdxTimeToH5:
    def __init__(self, log_queue, queue, config, market, quotations, ip, port, dest_dir, max_days):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.task_name = 'IMPORT_TIME'
        self.queue = queue
        self.log_queue = log_queue
        self.config = config
        self.market = market
        self.quotations = quotations
        self.ip = ip
        self.port = port
        self.dest_dir = dest_dir
        self.max_days = int(max_days)
        self.status = "no run"

    @hku_catch(trace=True)
    def __call__(self):
        self.status = "running"
        capture_multiprocess_all_logger(self.log_queue)
        if self.config.getboolean('hdf5', 'enable', fallback=True):
            sqlite_file = "{}/stock.db".format(self.config['hdf5']['dir'])
            connect = sqlite3.connect(sqlite_file, timeout=1800)
            import_time = h5_import_time
        elif self.config.getboolean('mysql', 'enable', fallback=True):
            db_config = {
                'user': self.config['mysql']['usr'],
                'password': self.config['mysql']['pwd'],
                'host': self.config['mysql']['host'],
                'port': self.config['mysql']['port']
            }
            connect = mysql.connector.connect(**db_config)
            import_time = mysql_import_time
        elif self.config.getboolean('clickhouse', 'enable', fallback=True):
            db_config = {
                'username': self.config['clickhouse']['usr'],
                'password': self.config['clickhouse']['pwd'],
                'host': self.config['clickhouse']['host'],
                'port': self.config['clickhouse']['http_port']
            }
            connect = clickhouse_connect.get_client(**db_config)
            import_time = clickhouse_import_time

        count = 0
        try:
            progress = ProgressBar(self)
            api = TdxHq_API()
            hku_info("导入 {} 分时数据 from {}", self.market, self.ip)
            hku_check(api.connect(self.ip, self.port), "failed connect pytdx {}:{}", self.ip, self.port)
            count = import_time(
                connect, self.market, self.quotations, api, self.dest_dir, max_days=self.max_days, progress=progress
            )
            self.logger.info("导入 {} 分时记录数: {}".format(self.market, count))
            api.disconnect()
        except Exception as e:
            self.logger.error(e)
        finally:
            api.close()
            connect.close()

        self.queue.put([self.task_name, self.market, 'TIME', None, count])
        self.status = "finished"
