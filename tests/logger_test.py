# -*- coding: UTF-8 -*-

import os
import sys
# print (sys.path)
#from moduls.class_Logger import MyLogger
from MyTool2020.moduls.class_Logger import MyLogger

logger= MyLogger(out=2)
print(os.path.abspath(__file__))
print(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))

logger.debug('this is a debug level message')
logger.info('this is info level message')
logger.warning('this is warning level message')
logger.error('this isss error level message')
logger.critical('this is critical level message')