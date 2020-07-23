# -*- coding: UTF-8 -*-

import time
import socket
import telnetlib
import re
import logging
import logtool


class TelnetClient():
    """
    telnetclient类:
    __init__: self.login_fail_info = None

    login: 登陆设备

    logout: 退出登陆

    enter_config_terminal: 从特权模式进入全局配置模式

    exit_config_terminal: 从全局配置模式or其他模式 退出到特权模式

    send_command: 命令行下发

    """

    def __int__(self):
        """
        :return self.tn = telnetlib.Telnet()
        :self.login_fail_info = None
        """
        self.tn = telnetlib.Telnet()
        self.login_fail_info = None

    def login(self,
              host,
              username='test',
              password='test',
              enable='enable',
              password_enable='zxr10',
              port=23,
              timeout=3):
        """
        登陆设备
        :return True or False，并记录self.login_fail_info
        """
        try:
            # self.tn.open(host, port=23)
            self.tn = telnetlib.Telnet(host, port=port, timeout=timeout)
        except socket.timeout as e:
            logging.error("telnet {} {}".format(host, e))
            self.login_fail_info = 'socket.timeout'
            return False
        except ConnectionResetError as e:
            logging.error("telnet {} ConnectionResetError {}".format(host, e))
            self.login_fail_info = 'ConnectionResetError'
            return False
        except Exception as e:
            logging.error("telnet {} {}".format(host, e),
                          exc_info=True)
            self.login_fail_info = e
            return False

        self.tn.read_until(b'Username:', timeout=10)
        self.tn.write(username.encode('utf-8') + b'\n')

        self.tn.read_until(b'Password:', timeout=10)
        self.tn.write(password.encode('utf-8') + b'\n')

        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        login_result = self.tn.read_very_eager().decode('utf-8')
        if "Login at" in login_result:
            self.tn.read_until(b'>', timeout=1)
            self.tn.write(enable.encode('utf-8') + b"\n")
            self.tn.read_until(b'Password:', timeout=1)
            self.tn.write(password_enable.encode('utf-8') + b"\n")
            login_result = self.tn.read_very_eager().decode('utf-8')
            if "#" in login_result:
                logging.debug("login {} successful".format(host))
                return True
            elif "Bad password" in login_result:
                logging.error("login {} failed: 特权模式密码错误".format(host))
                self.login_fail_info = '特权模式密码错误'
                self.logout()
                return False
            else:
                logging.error("login {} failed: {}".format(host, login_result))
                self.login_fail_info = login_result
                self.logout()
                return False
        elif 'error' in login_result:
            logging.error("login {} failed: Username or password \
                          error ".format(host))
            self.login_fail_info = 'Username or password error'
            self.logout()
            return False
        else:
            logging.error("login {} failed: {}".format(host, login_result))
            self.login_fail_info = login_result
            self.logout()
            return False

    def logout(self):
        """
        退出登陆
        """
        # self.tn.write(b"end\n")
        # self.tn.write(b"exit\n")
        self.tn.close()

    def enter_config_terminal(self, clear_vty=True):
        """
        从特权模式进入全局配置模式
        """
        result = self.send_command('config terminal')
        if 'Enter configuration commands' in result:
            logging.debug('从特权模式进入全局配置模式成功')
            self.send_command('multi-user config')
        else:
            logging.debug('从特权模式进入全局配置模式失败')
            if clear_vty:
                logging.debug('尝试踢同用户')  # 这里写的应该不对，这有2个用户在吧？
                result = self.send_command('who')
                vty_id = re.search(r'vty (.*) test', result).group(1).strip()
                print(vty_id)
                self.send_command('clear vty {}'.format(vty_id))

    def exit_config_terminal(self):
        """
        从全局配置模式or其他模式 退出到特权模式
        """
        self.send_command('end')

    def send_command(self, command):
        """
        命令行下发
        :return result_str
        """
        result_list = []
        self.tn.write(command.encode('utf-8') + b'\n')
        time.sleep(2)
        while (True):
            command_result = self.tn.read_very_eager().decode('utf-8')
            result_list.append(command_result)
            if '--More--' in command_result.strip():
                self.tn.write(b" ")
                time.sleep(0.5)
            else:
                break
        result_str = "\n".join(result_list)
        return result_str



if __name__ == '__main__':
    host = '172.11.3.100'
    command1 = 'show version'
    command2 = 'show board-info'
    telnet_client = TelnetClient()
    # login to the host, success:return true, fail: return false
    if telnet_client.login(host):
        telnet_client.input_command(command1)
        telnet_client.input_command(command2)
        telnet_client.logout()
