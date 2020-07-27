import SecureCRTlib as my
# -*- coding: UTF-8 -*-

import sys
import os
import re
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

t = my.DUT(crt)


def list_current_dr(path):
    os.chdir(path)
    dir_list = []
    file_list = []
    path_list = os.listdir(path)
    for obj_name in path_list:
        if os.path.isdir(obj_name):
            dir_list.append(obj_name)
        else:
            file_list.append(obj_name)
    # 排序
    for index in range(len(dir_list)):
        obj_match = re.match(r'(\d+)', dir_list[index])
        if obj_match:
            dir_list[index] = (int(obj_match.group(1)), dir_list[index])
        else:
            dir_list[index] = ''
    while '' in dir_list:
        dir_list.remove('')
    dir_list.sort()
    for index in range(len(dir_list)):
        dir_list[index] = dir_list[index][1]

    for index in range(len(file_list)):
        obj_match = re.match(r'(\d+)', file_list[index])
        if obj_match:
            file_list[index] = (int(obj_match.group(1)), file_list[index])
        else:
            file_list[index] = ''
    while '' in file_list:
        file_list.remove('')
    file_list.sort()
    for index in range(len(file_list)):
        file_list[index] = file_list[index][1]
    return (file_list, dir_list)


def readallfile(path):
    file_list, dir_list = list_current_dr(path)
    if file_list:
        for obj in file_list:
            commandlist = t.readtxt(obj)
            t.send('!!!!!!!!!'+obj+' start!!!!!!!!!')
            for szCommand in commandlist:
                t.send(szCommand)
            t.send('!!!!!!!!!'+obj+' end!!!!!!!!!')
    if dir_list:
        for obj in dir_list:
            readallfile(os.path.join(path, obj))


# ============================================================
# while 1 :
    # readallfile(current_dir)
readallfile(current_dir)
