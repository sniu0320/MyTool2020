# -*- coding: UTF-8 -*-

import logging
import logtool
from telnetclient import TelnetClient
from sshclient import SSHClient


class Dut(object):
    '''
    设备类
    '''

    def __init__(self,
                 mng_ip,
                 username='test',
                 password='test',
                 enable='enable',
                 password_enable='zxr10',
                 telnet_port=23,
                 ssh_port=22):
        '''
        设备初始化
        '''
        self.mng_ip = mng_ip
        self.username = username
        self.password = password
        self.enable = enable
        self.password_enable = password_enable
        self.telnet = TelnetClient()
        self.telnet_port = telnet_port
        self.ssh = SSHClient()
        self.ssh_port = ssh_port

        self.dutType = None  # 设备类型 9900 or 5960 or 其他
        self.version = None  # 版本信息
        self.snmp_enable = False

    def enableSNMP(self):
        """
        配置snmpv2c
        """
        if self.snmp_enable is not True:
            if self.telnet.login(host=self.mng_ip,
                                 username=self.username,
                                 password=self.password,
                                 enable=self.enable,
                                 password_enable=self.password_enable,
                                 port=self.telnet_port):
                if self.telnet.enter_config_terminal(multi_user=1, clear_vty=1):
                    self.telnet.send_commands(['snmp-server community public view AutoTest ro',
                                               'snmp-server community private view AutoTest rw',
                                               'snmp-server version v2c enable'
                                               ])
                    if 'error' not in self.telnet.send_command_output:
                        logging.debug('通过telnet配置snmp成功')
                        self.telnet.logout()
                        self.snmp_enable = True

    def enableSSH(self):
        pass
        # ssh server enable
