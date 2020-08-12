# -*- coding: UTF-8 -*-
import datetime
import logging
import logging.handlers
import os
# import re
import sys
import telnetlib
import time

current_dir = os.path.split(os.path.realpath(__file__))[0]
if current_dir not in sys.path:
    sys.path.append(current_dir)

# ########################  初始化logging模块  #########################
current_dir = os.getcwd()
log_file = os.path.join(current_dir, 'log', 'aotutest.log')

file_dir = os.path.split(log_file)[0]
if not os.path.isdir(file_dir):
    os.makedirs(file_dir)
# 初始化 文件日志
filelog_handler = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=10*1024*1024, backupCount=10, encoding='UTF-8')
filelog_formatter = logging.Formatter('%(asctime)s->%(message)s')
filelog_handler.setFormatter(filelog_formatter)
filelog_logger = logging.getLogger('filelog')
filelog_logger.addHandler(filelog_handler)
filelog_logger.setLevel(logging.DEBUG)
# 初始化 控制台日志
consolelog_handler = logging.StreamHandler()
consolelog_formatter = logging.Formatter('%(message)s')
consolelog_handler.setFormatter(consolelog_formatter)
consolelog_logger = logging.getLogger('consolelog')
consolelog_logger.addHandler(consolelog_handler)
consolelog_logger.setLevel(logging.DEBUG)


def option_negotiation_callback(sock, cmd, opt):
    '''
    telnet能力协商的回调函数，调整telnet会话的窗口的大小，避免分页，换行。

    这个telnet的回调函数不能放在DUT类内部实现，否则，telnet模块和DUT会相互引用，
    造成DUT类的__del__()函数，在结束时，不能正常调用！！！
    '''
    SGA_flag = None
    ECHO_flag = None
    if not SGA_flag and not ECHO_flag:
        sock.sendall(telnetlib.IAC + telnetlib.DO + telnetlib.SGA + telnetlib.IAC + telnetlib.DONT + telnetlib.ECHO)
    if cmd in (telnetlib.DO, telnetlib.DONT):
        if opt == telnetlib.NAWS:
            # 调整窗口的大小，避免分页，换行！
            sock.sendall(telnetlib.IAC + telnetlib.WILL + opt + telnetlib.IAC + telnetlib.SB
                         + telnetlib.NAWS + bytes([254])+bytes([254])+bytes([254])+bytes([254])
                         + telnetlib.IAC + telnetlib.SE)
        else:
            sock.sendall(telnetlib.IAC + telnetlib.WONT + opt)
    elif cmd in (telnetlib.WILL, telnetlib.WONT):
        if opt == telnetlib.SGA:
            SGA_flag = True
        elif opt == telnetlib.ECHO:
            ECHO_flag = True
            # sock.sendall(telnetlib.IAC + telnetlib.DO + telnetlib.opt)
        else:
            sock.sendall(telnetlib.IAC + telnetlib.DONT + opt)


class BaseDUT(object):
    """
    基础DUT类，公共函数统一放置于此

    :param debug: 打开调试开关(不打印命令行回显)

    :param log_switch: log日志开关,记录命令行回显
    """
    CRLF = b'\n'

    def __init__(self, debug_enable=True, log_enable=True):
        self.logfilename = time.strftime('%Y.%m.%d.%H.%M.%S')+'.log'
        self.debug_enable = debug_enable
        self.log_enable = log_enable

    def setlogfilename(self, filename):
        '''修改log函数保存文件名的前缀'''
        self.logfilename = filename + '.log'

    @staticmethod
    def process_newline_foroam(szString):
        r'''
        把字符串中的\r\n统一转为\n，去掉--More--
        '''
        szString = szString.replace('\r\n', '\n')
        # 美化分页时的打印效果
        szString = szString.replace('\b \b', '')
        szString = szString.replace(' --More--', '')
        return szString

    def debug(self, szString, print_only=False, time_stamp=True):
        '''debug'''
        szString = BaseDUT.process_newline_foroam(szString)
        if self.debug_enable:
            consolelog_logger.debug(szString)
            filelog_logger.debug(szString)
        if not print_only:
            self.log(szString, time_stamp)

    def error(self, szString, exc_info=False, print_only=False, time_stamp=True):
        '''error'''
        szString = BaseDUT.process_newline_foroam(szString)
        if self.debug_enable:
            consolelog_logger.error(szString, exc_info=exc_info)
            filelog_logger.error(szString, exc_info=exc_info)
        if not print_only:
            self.log(szString, time_stamp)

    def log(self, szString, time_stamp=True):
        '''每次的日志文件名都不同，以脚本运行的时间命名日志文件名称 '''
        current_dir = os.getcwd()
        log_file = os.path.join(current_dir, 'log', self.logfilename)
        file_dir = os.path.split(log_file)[0]
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        if self.log_enable:
            with open(log_file, 'a') as f:
                datefmt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[0:-3]
                if time_stamp:
                    if '\n' in szString:
                        f.write(datefmt+': '+szString)
                    else:
                        f.write(datefmt+': '+szString+'\n')
                else:
                    if '\n' in szString:
                        f.write(szString)
                    else:
                        f.write(szString+'\n')

    def oam_print(self, szString, time_stamp=True):
        if self.log_enable:
            szString = BaseDUT.to_str(szString)
            szString = BaseDUT.process_newline_foroam(szString)
            print(szString)
            self.log(szString, time_stamp)

    @staticmethod
    def to_str(bytes_or_str):
        '''转为字符串'''
        if isinstance(bytes_or_str, bytes):
            value = bytes_or_str.decode('utf-8')
        else:
            value = bytes_or_str
        return value

    @staticmethod
    def to_bytes(bytes_or_str):
        '''转为字节码'''
        if isinstance(bytes_or_str, str):
            value = bytes_or_str.encode('utf-8')
        else:
            value = bytes_or_str
        return value

    @staticmethod
    def sleep(ms):
        '''time.sleep'''
        time.sleep(ms/1000.0)

    @staticmethod
    def timestamp():
        '''time.time'''
        return time.time()


class DUT(BaseDUT):
    """
    DUT class
    """
    def __init__(self,
                 host=None,
                 username='test',
                 password='test',
                 enable='enable',
                 password_enable='zxr10',
                 debug_enable=True,
                 log_enable=True):
        super().__init__(debug_enable, log_enable)
        self.host = host
        self.username = username
        self.password = password
        self.enable = enable
        self.password_enable = password_enable

        if self.host:
            logfilename = host.replace(':', '.') + '_' + time.strftime('%Y.%m.%d')
            self.setlogfilename(logfilename)

        self.tn = None
        self.login_fail_info = None

    def login(self, protocol='telnet', port=23, timeout=5, waittime=3):
        """
        登陆设备，支持telnet和ssh
        :return True or False
        """
        if self.host:
            if protocol == 'telnet':
                self.debug('Begin to telnet {}'.format(self.host))
                try:
                    self.tn = telnetlib.Telnet(self.host, port, timeout)
                # except socket.timeout as e:
                #     self.error("telnet {} failed({})".format(self.host, e))
                #     self.login_fail_info = e
                #     return False
                # except ConnectionResetError as e:
                #     #  [WinError 10054] 远程主机强迫关闭了一个现有的连接
                #     self.error("telnet {} failed({})".format(self.host, e))
                #     self.login_fail_info = e
                #     return False
                # except ConnectionRefusedError as e:
                #     #  [WinError 10061] 由于目标计算机积极拒绝，无法连接
                #     self.error("telnet {} failed({})".format(self.host, e))
                #     self.login_fail_info = e
                #     return False
                except Exception as e:
                    # self.error("telnet {} failed({})".format(self.host, e), True)
                    self.error("telnet {} failed: {}\n".format(self.host, e))
                    self.login_fail_info = e
                    return False

                # self.tn.set_option_negotiation_callback(option_negotiation_callback)

                tResult = self.tn.expect([b'sername:'], waittime)
                self.oam_print(tResult[2], time_stamp=False)
                self.tn.write(self.username.encode() + BaseDUT.CRLF)
                self.oam_print(self.tn.read_until(b'assword:'))
                self.tn.write(self.password.encode() + BaseDUT.CRLF)

                tResult = self.tn.expect([b'#', b'>', b'error'], waittime)
                if tResult[0] == -1:
                    # 未读取到
                    e = 'Don\'t find system prompt!'
                    self.error("telnet {} failed: {}".format(self.host, e), print_only=True)
                    self.login_fail_info = e
                    return False
                elif tResult[0] == 2:
                    e = 'Username or password error!'
                    self.error("telnet {} failed: {}".format(self.host, e), print_only=True)
                    self.login_fail_info = e
                    return False
                elif tResult[0] == 1:
                    self.oam_print(tResult[2])
                    self.tn.write(self.enable.encode() + BaseDUT.CRLF)
                    self.oam_print(self.tn.read_until(b'assword:'))
                    self.tn.write(self.password_enable.encode() + BaseDUT.CRLF)
                    tResult = self.tn.expect([b'#', b'Bad password'], waittime)
                    if tResult[0] == -1:
                        e = 'Don\'t find 特权模式 prompt!'
                        self.error("telnet {} failed: {}".format(self.host, e))
                        self.login_fail_info = e
                        return False
                    elif tResult[0] == 1:
                        e = 'Bad password!'
                        self.error("telnet {} failed: {}".format(self.host, e))
                        self.login_fail_info = e
                        return False
                    elif tResult[0] == 0:
                        self.oam_print(tResult[2])
                        self.debug("telnet {} successful".format(self.host), print_only=True)
                        return True
                elif tResult[0] == 0:
                    self.debug("telnet {} successful".format(self.host), print_only=True)
                    return True

            elif protocol == 'ssh':
                if port == 23:
                    port = 22
                self.sshlib = __import__('autosshlib')

                try:
                    self.debug('Begin to ssh {}'.format(self.host), print_only=True)
                    self.tn = self.sshlib.ssh(self.host, port, self.username, self.password, False, timeout)
                    tResult = self.tn.expect([b'#', b'>'], waittime)
                    if tResult[0] == -1:
                        # 未读取到
                        e = 'Don\'t find system prompt!'
                        self.error("ssh {} failed: {}".format(self.host, e), print_only=True)
                        self.login_fail_info = e
                        return False
                    elif tResult[0] == 1:
                        self.oam_print(tResult[2])
                        self.tn.write(self.enable.encode() + BaseDUT.CRLF)
                        self.oam_print(self.tn.read_until(b'assword:'))
                        self.tn.write(self.password_enable.encode() + BaseDUT.CRLF)
                        tResult = self.tn.expect([b'#', b'Bad password'], waittime)
                        if tResult[0] == -1:
                            e = 'Don\'t find 特权模式 prompt!'
                            self.error("ssh {} failed: {}".format(self.host, e))
                            self.login_fail_info = e
                            return False
                        elif tResult[0] == 1:
                            e = 'Bad password!'
                            self.error("ssh {} failed: {}".format(self.host, e))
                            self.login_fail_info = e
                            return False
                        elif tResult[0] == 0:
                            self.oam_print(tResult[2])
                            self.debug("ssh {} successful".format(self.host), print_only=True)
                            return True
                    elif tResult[0] == 0:
                        self.oam_print(tResult[2])
                        self.debug("ssh {} successful".format(self.host), print_only=True)
                        return True
                except Exception as e:
                    self.error("ssh {} failed: {}".format(self.host, e), print_only=True)
                    self.login_fail_info = e
                    return False

    def close(self):
        '''
        关闭当前DUT会话
        '''
        self.debug('The current DUT connection is closed !\r\n')
        self.oam_print('\n\n')
        self.tn.close()

    def __del__(self):
        self.close()

    def send(self, szCommand, delay=0, timeout=60):
        '''
        遇到错误就会停止，方便查看，主要用于配置设备。
        delay 函数执行后等待延迟时间ms
        '''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else:
            self.tn.write(szCommand+BaseDUT.CRLF)
        while True:
            # tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.', b'\r\n'], timeout)
            # self.oam_print(tResult[2])
            # if tResult[0] == 3 or tResult[0] == 4:
            #     continue
            tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.'], timeout)
            self.oam_print(tResult[2])
            if tResult[0] == 3:
                continue
            elif tResult[0] == 0:  # 这里如果出现打印里有# 怎么处理？
                break
            elif tResult[0] == 1:  # 处理more翻页
                self.tn.write(b' ')
                continue
            elif tResult[0] == 2:
                tResult = self.tn.expect([b'again', b'#'])
                if tResult[0] == 0:  # 提示again时
                    # 给3次重试的机会！
                    for retry in range(1, 4):
                        self.oam_print(tResult[2])
                        self.oam_print(self.tn.read_until(b'#'))
                        self.sleep(retry*500)
                        self.tn.write(szCommand+BaseDUT.CRLF)
                        tResult = self.tn.expect([b'again', b'#'])
                        if tResult[0] == 1:
                            self.oam_print(tResult[2])
                            break
                        elif retry == 3:
                            szResult = tResult[2] + self.tn.read_until(b'#')
                            self.oam_print(szResult)
                            sys.exit(0)
                    break
                elif tResult[0] == 1:
                    self.oam_print(tResult[2])
                    self.error('\r\n'+'%Error '+tResult[2].decode())
                    sys.exit(0)
        if (delay != 0):
            self.sleep(delay)

    def send2(self, szCommand, delay=0, timeout=60):
        '''遇到一般错误不会停止，继续执行'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else:
            self.tn.write(szCommand+BaseDUT.CRLF)
        while True:
            tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.', b'\r\n'], timeout)
            self.oam_print(tResult[2])
            if tResult[0] == 4 or tResult[0] == 3:
                continue
            # tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.'], timeout)
            # self.oam_print(tResult[2])
            # if tResult[0] == 3:
            #     continue
            elif tResult[0] == 0:
                break
            elif tResult[0] == 1:
                self.tn.write(b' ')
                continue
            elif tResult[0] == 2:
                tResult = self.tn.expect([b'again', b'#'])
                if tResult[0] == 0:
                    # 给3次重试的机会！
                    for retry in range(1, 4):
                        self.oam_print(tResult[2])
                        self.oam_print(self.tn.read_until(b'#'))
                        self.sleep(retry*500)
                        self.tn.write(szCommand+BaseDUT.CRLF)
                        tResult = self.tn.expect([b'again', b'#'])
                        if tResult[0] == 1:
                            self.oam_print(tResult[2])
                            break
                        elif retry == 3:
                            self.oam_print(tResult[2])
                            self.oam_print(self.tn.read_until(b'#'))
                    break
                else:
                    self.oam_print(tResult[2])
                    break
        if (delay != 0):
            self.sleep(delay)

    def send3(self, szCommand):
        '''只发送命令，不关心执行的结果,慎用!!'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else:
            self.tn.write(szCommand+BaseDUT.CRLF)
        # ssh 协议有流控，一直不读sockets，会使服务端不能继续发送内容
        self.sleep(15)
        self.oam_print(self.tn.read_eager())

    def rec2(self, szCommand, prompt='#', timeout=60):
        '''
        接收命令的返回结果，命令的回显和末尾的设备提示符已经删除！！
        '''
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        self.tn.write(szCommand+BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'], timeout)
        self.oam_print(tResult[2])
        szResult = b''
        while True:
            # tResult = self.tn.expect([prompt, b' --More--', b'\r\n'], timeout)
            tResult = self.tn.expect([prompt, b' --More--'], timeout)
            szResult = szResult + tResult[2]
            self.oam_print(tResult[2])
            if tResult[0] == 0:
                break
            elif tResult[0] == 1:
                self.tn.write(b' ')

        szResult = szResult.decode()
        szResult = szResult.replace('\b \b', '')
        szResult = szResult.replace(' --More--', '')
        if (szResult.rfind('\r\n') == -1):
            return ''
        else:
            szResult = szResult.rsplit('\r\n', 1)
            return BaseDUT.process_newline_foroam(szResult[0])

    def rec(self, szCommand, prompt='#', timeout=60):
        '''接收原始数据，开始的命令回显和末尾的设备提示符都没有删除'''
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        self.tn.write(szCommand+BaseDUT.CRLF)
        szResult = b''
        while True:
            tResult = self.tn.expect([prompt, b' --More--', b'\.\.'], timeout)
            szResult = szResult + tResult[2]
            self.oam_print(tResult[2])
            if tResult[0] == 0:
                break
            elif tResult[0] == 1:
                self.tn.write(b' ')

        szResult = szResult.decode()
        szResult = szResult.replace('\b \b', '')
        szResult = szResult.replace(' --More--', '')
        return BaseDUT.process_newline_foroam(szResult)

    def sendctrl(self, char, prompt='#'):
        '''目前仅支持字符C和字符X'''
        prompt = prompt.encode()
        if (char == 'c'):
            self.tn.write(b'\3')
            self.oam_print(self.tn.read_until(prompt))
        elif (char == 'x'):
            self.tn.write(b'\30')

    def sendexpect(self, szCommand, expect, timeout=60):
        '''
        下发命令行，抓到期望字段return True，
        可以用来处理改路由口、重启等需要用yes的
        '''
        send = szCommand.encode()
        expect = expect.encode()
        self.tn.write(send + BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'], timeout)
        self.oam_print(tResult[2])
        tResult = self.tn.expect([expect], timeout)
        self.oam_print(tResult[2])
        self.oam_print(self.tn.read_lazy())
        if tResult[0] == -1:
            return False
        else:
            return True

    def con_t(self):
        '''
        需要优化，识别多用户等
        '''
        self.sendctrl('c')
        self.sendctrl('c')
        self.send('configure terminal')

    # def exit_con_t(self):
    #     """
    #     从全局配置模式or其他模式 退出到特权模式
    #     """
    #     self.send('end')

    # def enter_config_terminal(self, multi_user=1, clear_vty=1):
    #     """
    #     进入全局配置模式，multi_user=1 配置多用户；
    #     如果clear_vty=1，尝试踢掉锁定用户(串口锁定踢不掉)

    #     :return True or False
    #     """
    #     # self.sendctrl('c')
    #     # self.sendctrl('c')
    #     self.send('end')
    #     i = 0
    #     while i <= 1:
    #         self.send('configure terminal')
    #         if 'Enter configuration commands' in self.send_command_output:
    #             logging.debug('进入全局配置模式成功')
    #             if multi_user == 1:
    #                 self.send('multi-user config')
    #             return True
    #         else:
    #             if clear_vty == 1:
    #                 if 'Locked from con' in self.send_command_output:
    #                     logging.error('进入全局配置模式失败(串口用户锁定)')
    #                     return False
    #                 else:
    #                     vty_id = re.search(r'Locked from vty(\d*)',
    #                                        self.send_command_output).group(1)
    #                     elf.send('clear line vty {}'.format(vty_id))
    #                     i += 1
    #             else:
    #                 logging.error('进入全局配置模式失败')
    #                 return False
    def WaitSynchronized(self):
        while True:
            self.send('show clock')
            szResult = self.rec('show synchronization | include MPU')
            if 'Slave' not in szResult:
                break
            if szResult.count('Master') * 2 != szResult.count('Synchronized'):
                self.sleep(5000)
            else:
                break
        return True

    def SaveConfig(self):
        self.sendctrl('c')
        self.send('write')
        self.WaitSynchronized()

    def reboot(self):
        self.sendctrl('c')
        self.sendexpect('reload system force', 'no')
        self.send3('yes')