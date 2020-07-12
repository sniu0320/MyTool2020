# -*- coding: UTF-8 -*-

import os

def dfs_showdir(path, depth=0, x=0):
    '''
    打印文件目录树(包含子目录)
    depth文件深度 = excel 列
    x = excel 行
    '''
    for item in os.listdir(path):
        # print("|      " * depth + "+--" + item+"({},{})".format(x,depth))
        print("|      " * depth + "+--" + item)
        x += 1
        newitem = os.path.join(path,item)
        #newitem = path +'/'+ item
        if os.path.isdir(newitem):
            dfs_showdir(newitem, depth +1, x)

if __name__ == '__main__':
    dfs_showdir('.') #当前文件夹
