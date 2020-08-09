# -*- coding: UTF-8 -*-

import os
import logging
import logging.config
from functools import wraps

CONF_LOG = os.path.join(os.path.abspath(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__)))), "conf", "logging_config.ini")

logging.config.fileConfig(CONF_LOG)

# LOG_KEY = 'root'

# https://www.runoob.com/w3cnote/python-func-decorators.html
# https://blog.csdn.net/lilygg/article/details/86775226?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-7.nonecase&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromBaidu-7.nonecase


def use_log(func):
    """
    函数被调用打印 ”func is running“ （装饰器示例）
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.debug("%s is running" % func.__name__)  # 这记录的是wrapper 而不是func
        return func(*args, **kwargs)
    return wrapper


def use_log2(level):
    """
    函数被调用打印 ”func is running“ （带参数装饰器示例）
    :param level: warn info
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if level == "warn":
                logging.warn("%s is running" % func.__name__)
            elif level == "info":
                logging.info("%s is running" % func.__name__)
            return func(*args)
        return wrapper
    return decorator


class logit(object):
    """
    装饰器类 主要使用call，可以创建子类，添加功能（示例）;这个还没弄明白
    """

    def __init__(self):
        pass

    def __call__(self, func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            self.notify()
            return func(*args, **kwargs)
        return wrapped_function

    def notify(self):
        # 随便干点啥
        print("notify call*****************")
        pass


def log_error(func):
    """
    给func 添加 try except,记录error信息
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # logger = logging.getLogger(LOG_KEY)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e, exc_info=True)
    return wrapper


def log_selflog(cls):
    """
    给类添加 self.log
    """
    @wraps(cls)
    def wrapper(*args, **kwargs):
        # logger = logging.getLogger(LOG_KEY)
        if not hasattr(cls, 'log'):
            setattr(cls, 'log', logging)
        return(cls(*args, **kwargs))
    return wrapper


if __name__ == '__main__':
    @logit()
    @log_error
    def test():
        a = '1'
        b = a+1
        return b
    test()

    @use_log
    @log_selflog
    class Test:
        def add(self):
            for _ in range(5):
                self.log.info('test.')
    t = Test()
    t.add()
