# -*- coding: UTF-8 -*-

import time
import socket
import telnetlib
import re
import logging
import logtool
from iptool import ipTool


class TelnetClient(object):
    """
    telnetclient类

    attribute:

    self.login_fail_info: login失败信息

    self.send_command_output: send_command后获取回显

    method:

    login: 登陆设备

    logout: 退出登陆

    enter_config_terminal: 进入全局配置模式

    exit_config_terminal: 从全局配置模式or其他模式 退出到特权模式

    send_command: 单条命令行下发

    send_commands: 连续多条命令行下发
    """

    def __init__(self,
                 host,
                 username='test',
                 password='test',
                 enable='enable',
                 password_enable='zxr10',
                 port=23,
                 timeout=3):
        """
        self.login_fail_info: login失败信息

        self.send_command_output: send_command后获取回显
        """
        self.host = host
        self.username = username
        self.password = password
        self.enable = enable
        self.password_enable = password_enable
        self.port = port
        self.timeout = timeout

        self.client = telnetlib.Telnet()
        self.login_fail_info = None
        self.send_command_output = None

    def login(self):
        """
        登陆设备
        :return True or False，并记录self.login_fail_info
        """
        if ipTool.ping_test(self.host):
            try:
                # self.client.open(host, port=23)
                self.client = telnetlib.Telnet(
                    self.host, port=self.port, timeout=self.timeout)
            except socket.timeout as e:
                logging.error("telnet {} failed({})".format(self.host, e))
                self.login_fail_info = 'socket.timeout'
                return False
            except ConnectionResetError as e:
                #  [WinError 10054] 远程主机强迫关闭了一个现有的连接
                logging.error("telnet {} failed({})".format(self.host, e))
                self.login_fail_info = e
                return False
            except ConnectionResetError as e:
                #  [WinError 10061] 由于目标计算机积极拒绝，无法连接
                logging.error("telnet {} failed({})".format(self.host, e))
                self.login_fail_info = e
                return False
            except Exception as e:
                logging.error("telnet {} {}".format(self.host, e),
                              exc_info=True)
                self.login_fail_info = e
                return False

            self.client.read_until(b'Username:', timeout=10)
            self.client.write(self.username.encode('utf-8') + b'\n')

            self.client.read_until(b'Password:', timeout=10)
            self.client.write(self.password.encode('utf-8') + b'\n')

            # 延时两秒再收取返回结果，给服务端足够响应时间
            time.sleep(1)
            # 获取登录结果
            # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
            login_result = self.client.read_very_eager().decode('utf-8')
            if "Login at" in login_result:
                self.client.read_until(b'>', timeout=1)
                self.client.write(self.enable.encode('utf-8') + b"\n")
                self.client.read_until(b'Password:', timeout=1)
                self.client.write(self.password_enable.encode('utf-8') + b"\n")
                login_result = self.client.read_very_eager().decode('utf-8')
                time.sleep(1)
                if "#" in login_result:
                    logging.debug("login {} successful".format(self.host))
                    self.login_fail_info = None
                    return True
                elif "Bad password" in login_result:
                    logging.error(
                        "login {} failed: 特权模式密码错误".format(self.host))
                    self.login_fail_info = '特权模式密码错误'
                    self.logout()
                    return False
                else:
                    logging.error("login {} failed(特权模式): {}".format(
                        self.host, login_result))
                    self.login_fail_info = login_result
                    self.logout()
                    return False
            elif 'error' in login_result:
                logging.error(
                    "login {} failed: Username or password error".format(self.host))
                self.login_fail_info = 'Username or password error'
                self.logout()
                return False
            else:
                logging.error("login {} failed(用户模式): {}".format(
                    self.host, login_result))
                self.login_fail_info = login_result
                self.logout()
                return False
        else:
            self.login_fail_info = "offline"
            return False

    def logout(self):
        """
        退出登陆
        """
        # self.client.write(b"end\n")
        # self.client.write(b"exit\n")
        self.client.close()

    def enter_config_terminal(self, multi_user=1, clear_vty=1):
        """
        进入全局配置模式，multi_user=1 配置多用户；
        如果clear_vty=1，尝试踢掉锁定用户(串口锁定踢不掉)

        :return True or False
        """
        i = 0
        while i <= 1:
            self.send_command('config terminal')
            if 'Enter configuration commands' in self.send_command_output:
                logging.debug('进入全局配置模式成功')
                if multi_user == 1:
                    self.send_command('multi-user config')
                return True
            else:
                if clear_vty == 1:
                    if 'Locked from con' in self.send_command_output:
                        logging.error('进入全局配置模式失败(串口用户锁定)')
                        return False
                    else:
                        vty_id = re.search(r'Locked from vty(\d*)',
                                           self.send_command_output).group(1)
                        self.send_command('clear line vty {}'.format(vty_id))
                        i += 1
                else:
                    logging.error('进入全局配置模式失败')
                    return False

    def exit_config_terminal(self):
        """
        从全局配置模式or其他模式 退出到特权模式
        """
        self.send_command('end')

    def send_command(self, command, time_sleep=1):
        """
        单条命令行下发
        :param command str: 命令行
        :param time_sleep int: 命令行下发后等待回显时间

        :回显信息 self.send_command_output
        """
        result_list = []
        self.client.write(command.encode('utf-8') + b'\n')
        time.sleep(time_sleep)
        while (True):
            command_result = self.client.read_very_eager().decode('utf-8')
            result_list.append(command_result)
            if '--More--' in command_result.strip():
                self.client.write(b" ")
                time.sleep(0.5)
            else:
                break
        self.send_command_output = "\n".join(result_list)
        logging.debug(self.send_command_output)

    def send_commands(self, commands):
        """
        多条命令行下发
        :param commands list: [command1,command2]

        :回显信息 self.send_command_output
        """
        result_list = []
        if type(commands) is str:
            commands = commands.split(',')
        for command in commands:
            self.send_command(command)
            result_list.append(self.send_command_output)
        self.send_command_output = "\n".join(result_list)


if __name__ == '__main__':
    host = '172.11.3.100'
    command1 = 'show version'
    command2 = 'show board-info'
    commands = ['show board-info', 'show hostname']
    dut = TelnetClient(host)
    # login to the host, success:return true, fail: return false
    if dut.login():
        if dut.enter_config_terminal():
            dut.send_command(command1)
            print(dut.send_command_output)
        dut.send_commands(commands)
        print(dut.send_command_output)
        dut.logout()
