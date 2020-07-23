# -*- coding: UTF-8 -*-

import time
import socket
import telnetlib
import logging
import logtool


class TelnetClient():
    """
    telnetclient类

    login_host: 登陆设备
    """

    def __int__(self):
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
        return true or false
        """
        try:
            # self.tn.open(host, port=23)
            self.tn = telnetlib.Telnet(host, port=port, timeout=timeout)
        except socket.timeout as e:
            logging.error("telnet {} {}".format(host, e))
            return False
        except ConnectionResetError as e:
            logging.error("telnet {} ConnectionResetError {}".format(host, e))
        except Exception as e:
            logging.error("telnet {} {}".format(host, e),
                          exc_info=True)  # 输出Traceback信息
            # logging.exception('Error') #输出Traceback信息,同上
            return False

        self.tn.read_until(b'Username:', timeout=10)
        self.tn.write(username.encode('utf-8') + b'\n')

        self.tn.read_until(b'Password:', timeout=10)
        self.tn.write(password.encode('utf-8') + b'\n')

        # 延时两秒再收取返回结果，给服务端足够响应时间
        time.sleep(2)
        # 获取登录结果
        # read_very_eager()获取到的是的是上次获取之后本次获取之前的所有输出
        command_result = self.tn.read_very_eager().decode('utf-8')
        if "Login at" in command_result:
            logging.debug("login to {} successfully".format(host))
            self.tn.read_until(b'>', timeout=1)
            self.tn.write(enable.encode('utf-8') + b"\n")
            self.tn.read_until(b'Password:', timeout=1)
            self.tn.write(password_enable.encode('utf-8') + b"\n")
            # self.tn.write(b"ter len 0\n")
            return True
        elif 'error' in command_result:
            print(command_result)
            logging.debug("密码错误")
        else:
            logging.debug("login to host:%s failed" % host)
            return False

    def input_command(self, command):
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

    def logout(self):
        self.tn.write(b"end\n")
        self.tn.write(b"exit\n")  # self.tn.close()


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
