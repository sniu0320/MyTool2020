# -*- coding: UTF-8 -*-


class Dut(object):
    '''
    设备类
    '''

    def __init__(self, mng_ip, username='test', password='test'):
        '''
        设备初始化
        '''
        self.mng_ip = mng_ip
        self.username = username
        self.password = password
        self.version = None

    def enableSNMP(self):
        pass

    def enableSSH(self):
        pass
