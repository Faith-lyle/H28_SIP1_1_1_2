#!/usr/bin/python3
# -- coding: utf-8 --
# @Author : Long.Hou
# @Email : Long2.Hou@luxshare-ict.com
# @File : logHelper.py
# @Project : H28_SIP1_1_1_2
# @Time : 2022/5/31 09:05
# -------------------------------
import datetime
import logging


# 日志类
class LogHelper(object):
    def __init__(self, log_name, log_level):
        self.index = 1
        self.log_name = log_name
        self.log_level = log_level
        self._log = logging.Logger(self.log_name, self.log_level)

    def create_new_log(self, log_name):
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(log_name, encoding='utf-8', mode='a')
        fh.setLevel(self.log_level)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(self.log_level)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s\t\t<Process>(pid: %(process)d,tid: %(thread)d)\t\t<function>%(name)s.%(funcName)s\t\t%('
            'message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self._log.addHandler(fh)
        self._log.addHandler(ch)

    def get_log(self):
        return self._log

    def debug(self, msg):
        self._log.debug(msg)

    def info(self, msg):
        self._log.info(msg)

    def warning(self, msg):
        self._log.warning(msg)

    def error(self, msg):
        self._log.error(msg)

    def critical(self, msg):
        self._log.critical(msg)

    def exception(self, msg):
        self._log.exception(msg)

    def receive_log(self, msg):
        self._log.info("Receive Content:\n" + msg)

    def send_log(self, msg):
        self._log.info("Send Content:\n" + msg)

    def set_item_result(self, value, result,slot,lower,upper):
        self._log.info("slot {}{}\n".format(slot, '-' * 20))
        self._log.debug("Lower Limit: {}".format(lower))
        self._log.debug("Upper Limit: {}".format(upper))
        self._log.debug("Get Value: {}".format(value))
        self._log.debug('Test Result: {}'.format(result))

    def item_end(self, item):
        EndTime = datetime.datetime.now().__sub__(self.stratTime)
        msg = "Elapsed Seconds:{}".format(EndTime.microseconds / 1000000 + EndTime.seconds)
        self._log.info(msg)
        self._log.info('Step{}  "{}"  End   <------------------------------\n'.format(self.index, item))
        self.index += 1

    def item_start(self, item):
        self.stratTime = datetime.datetime.now()
        msg = 'Step{}  "{}" Start   ------------------------------>'.format(self.index, item)
        self._log.info(msg)

    def mes_log(self, func_name, url, data, response):
        self._log.debug("{}\nFunction:{}\nRequest URL:{}\nRequest Method: POST\nRequest Date:{}\n"
                        "Response Status Code:{}\nResponse Text:{}\n".format('-' * 20, func_name, url, data,
                                                                             response.status_code, response.text))

    def mes_error_log(self, func_name, url, data, error):
        self._log.error(
            "{}\nFunction:{}\nRequest URL:{}\nRequest Method: POST\nRequest Date:{}\nError information:{}\n".format(
                '-' * 20, func_name, url, data, error))


if __name__ == '__main__':
    log = LogHelper('test.log', logging.DEBUG)
    log.item_start('test')
    log.critical('hello')
    log.item_end('test')
