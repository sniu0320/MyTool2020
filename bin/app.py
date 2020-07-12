# -*- coding: UTF-8 -*-

import sys
import os

BASE_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(BASE_PATH)
# 当我们导入一个模块时：import  xxx，默认情况下python解析器会搜索当前目录、已安装的内
# 置模块和第三方模块，搜索路径存放在sys.path中
print(sys.path)

from core.modules.class_Logger import MyLogger
print("Welcome to my app!")
