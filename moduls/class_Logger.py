# -*- coding: UTF-8 -*-

import os
import sys
import time
import logging
from logging.handlers import TimedRotatingFileHandler

def __singletion(cls):
    """
    单例模式的装饰器函数
    :param cls: 实体类
    :return: 返回实体类对象
    """
    instances = {}
    def getInstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getInstance

@__singletion
class MyLogger():
    def __init__(self, enable=True,out=0,
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                #  name=__name__,
                 set_level=logging.DEBUG,
                #  log_name=time.strftime("%Y-%m-%d.log", time.localtime()),
                 log_path=os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "log"),
                 console_level=logging.DEBUG, 
                 file_level=logging.DEBUG):
        """
        :param enable: False 禁用日志输出

        :param out: 设置输出端：0：默认控制台和文件都输出，1：仅控制台输出，其他：仅文件输出

        :param name: 日志中打印的name，默认为运行程序的name

        :param set_level: 日志级别["NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL"]，默认为logging.DEBUG

        :param log_name: 日志文件的名字，默认为当前时间（年-月-日.log）

        :param log_path: 日志文件夹的路径，默认为logger.py上级目录中的log文件夹

        """
        #print(log_path)
        self.__logger = logging.getLogger(name)
        self.logger.setLevel(set_level) #Log等级总开关
        self.out = out
        formater = logging.Formatter('%(asctime)s - %(name)s - %(filename)s [%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')
        '''
        %(filename)-25s -25的意思是左对齐，固定长度25 ，默认用空格填充
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
        # 控制台日志
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formater)
        console_handler.setLevel(console_level)

        # 文件日志
        if not os.path.exists(log_path):  # 创建日志目录
            os.makedirs(log_path)
        # fh = logging.FileHandler(os.path.join(log_path, log_name), mode='a')
        # 每天生成一个新的日志文件,保留两天的日志文件
        #file_handler = TimedRotatingFileHandler(os.path.join(log_path, log_name), when='D', interval=1, backupCount=2, encoding='utf-8')
        # 每隔 Byte 划分一个日志文件，备份文件为 1 个
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(log_path, 'debug.log'), maxBytes=1024*1024, backupCount=1, encoding="utf-8")
        file_handler.setFormatter(formater)
        file_handler.setLevel(file_level)
        
        if self.out == 0:
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
        elif  self.out == 1:
            self.logger.addHandler(console_handler)
        else:
            self.logger.addHandler(file_handler)

        if enable:
            pass
        else:
            self.logger.disabled = True

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
    logger = MyLogger(out=1)
    logger.debug('一个debug信息')
    logger.info('一个info信息')
    logger.warning('一个warning信息')
    logger.error('一个error信息')
    logger.critical('一个致命critical信息')