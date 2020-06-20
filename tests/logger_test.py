# -*- coding: UTF-8 -*-

import os
import sys
print (sys.path)

from .moduls.class_Logger import Logger
logger= Logger(out=0)


logger.debug('this is a debug level message')
logger.info('this is info level message')
logger.warning('this is warning level message')
logger.error('this is error level message')
logger.critical('this is critical level message')