# -*- coding: UTF-8 -*-

import os
import sys
import time
import logging
from logging.handlers import TimedRotatingFileHandler

class Logger():
    def __init__(self, set_level="DEBUG",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 log_name=time.strftime("%Y-%m-%d.log", time.localtime()),
                 log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "log"),
                 use_console=True,
                 clevel=logging.DEBUG, 
                 Flevel=logging.DEBUG):
        """
        :param set_level: 日志级别["NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"]，默认为DEBUG
        :param name: 日志中打印的name，默认为运行程序的name
        :param log_name: 日志文件的名字，默认为当前时间（年-月-日.log）
        :param log_path: 日志文件夹的路径，默认为logger.py同级目录中的log文件夹
        :param use_console: 是否在控制台打印，默认为True
        """
        self.__logger = logging.getLogger(str(name))
        self.logger.setLevel(logging.DEBUG) #Log等级总开关
        fmt = logging.Formatter('%(asctime)s - %(filename)s [%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')
        '''
        %(name)s            Logger的名字
        %(levelname)s       文本形式的日志级别
        %(message)s         用户输出的消息
        %(asctime)s         字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
        %(levelno)s         数字形式的日志级别
        %(pathname)s        调用日志输出函数的模块的完整路径名，可能没有
        %(filename)s        调用日志输出函数的模块的文件名
        %(module)s          调用日志输出函数的模块名
        %(funcName)s        调用日志输出函数的函数名
        %(lineno)d          调用日志输出函数的语句所在的代码行
        %(created)f         当前时间，用UNIX标准的表示时间的浮 点数表示
        %(relativeCreated)d 输出日志信息时来自Logger创建的毫秒数
        %(thread)d          线程ID。可能没有
        %(threadName)s      线程名。可能没有
        %(process)d         进程ID。可能没有
        '''
        if use_console:
            # 建立一个streamhandler来把日志打在控制台窗口上，级别为Flevel以上
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            sh.setLevel(clevel)
            self.logger.addHandler(sh)

        # 建立一个filehandler来把日志记录在文件里，级别为Flevel以上
        if not os.path.exists(log_path):  # 创建日志目录
            os.makedirs(log_path)
        # fh = logging.FileHandler(os.path.join(log_path, log_name), mode='a')
        # 每天生成一个新的日志文件,保留两天的日志文件
        fh = TimedRotatingFileHandler(os.path.join(log_path, log_name), when='D', interval=1, backupCount=2, encoding='utf-8')
        fh.setFormatter(fmt)
        fh.setLevel(Flevel)
        self.logger.addHandler(fh)


    def __getattr__(self, item):
        return getattr(self.logger, item)
 
    @property
    def logger(self):
        return self.__logger
 
    @logger.setter
    def logger(self, func):
        self.__logger = func

    # def _exec_type(self):
    #     #暂时不知道干啥用的s
    #     return "DEBUG" if os.environ.get("IPYTHONENABLE") else "INFO"
'''
简单配置输出到控制台
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')
'''
if __name__ == '__main__':
    logger = Logger()
    logger.debug('一个debug信息')
    logger.info('一个info信息')
    logger.warning('一个warning信息')
    logger.error('一个error信息')
    logger.critical('一个致命critical信息')