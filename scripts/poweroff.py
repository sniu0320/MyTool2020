# -*- coding: utf-8 -*-
import os
import platform

'''
关电脑脚本
'''
if platform.system() == "Windows":
    os.system('shutdown -s -f -t 0')  #强制立即关机
    # os.system("shutdown -s -t 0")
else:
    #linux系统
    os.system("poweroff")
