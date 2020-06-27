# -*- coding: UTF-8 -*-

import threading
import logging
from queue import Queue
from queue import Empty
from time import ctime, sleep

class MyThread(threading.Thread):
    '''
    __init__(self, func, args, name='')

    get_result(self)
    '''
    def __init__(self, func, args):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.name = self.func.__name__

    def get_result(self):
        '''
        return self.res
        '''
        return self.res

    def run(self):
        logging.debug('starting {} at: {}'.format(self.name, ctime()))
        self.res = self.func(self.args)
        logging.debug('{} finished at: {}'.format(self.name, ctime()))

class MyQueue():
    '''
    __init__(self, func, args_list, name='', thread_num=10)
    '''
    def __init__(self, func, args_list, thread_num=10):
        self.func = func
        self.args_list = args_list
        self.thread_num = thread_num

    def func_queue(self, q):
        try:
            while True:
                args = q.get_nowait()
                self.func(args)
        except Empty:
            pass

    def main(self):
        result_list = []
        q = Queue()
        for args in self.args_list:
            q.put(args)
        threads = []
        for i in range(self.thread_num):
            t=MyThread(self.func_queue, (q))
            # t.start()
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            result = t.get_result()
            print(result)
            result_list.append(result)
        print(result_list)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')

    def test(ip):
        sleep(2)
        return ip
    
    ip_list=[1,2,3,4,5,6,2,3,1]

    q=MyQueue(test, ip_list, 10)
    q.main()
