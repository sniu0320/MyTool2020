# -*- coding: UTF-8 -*-

import threading
import logging
from time import ctime, sleep

class MyThread(threading.Thread):
    
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def get_result(self):
        return self.res

    def run(self):
        logging.debug('starting {} at: {}'.format(self.name, ctime()))
        self.res = self.func(self.args)
        logging.debug('{} finished at: {}'.format(self.name, ctime()))




if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')

    def test(ip):
        sleep(2)
        return ip
    
    ip_list=[1,2,3,4,5,6,2,3,1]

    threads=[]
    for i in ip_list:
        t = MyThread(test,(i),test.__name__)
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
        print(i.get_result())