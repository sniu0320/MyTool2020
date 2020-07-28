# -*- coding: UTF-8 -*-

from multiprocessing import Process
import sys
import os
# import time
current_dir = os.path.split(os.path.realpath(__file__))[0]
if current_dir not in sys.path:
    sys.path.append(current_dir)

# ==========================================================
'''采用多进程方式加载不同版本的testcenter'''


def main():
    ProcessList = []
    tn = Process(target=loadTestCenter, args=('4.75', ))
    tn.start()
    ProcessList.append(tn)
    tn = Process(target=loadTestCenter, args=('4.54', ))
    tn.start()
    ProcessList.append(tn)
    for item in ProcessList:
        item.join()


def loadTestCenter(version):
    from StcPython import StcPython
    stc = StcPython(version)
    print "Spirent TestCenter version : %s" % stc.get("system1", "version")


if __name__ == '__main__':
    main()
