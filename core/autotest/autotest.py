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

    def debug(self, szString):
        '''debug'''
        szString = BaseDUT.process_newline_foroam(szString)
        if self.debug_enable:
            consolelog_logger.debug(szString)
            filelog_logger.debug(szString)
        self.log(szString)

    def error(self, szString, exc_info=False):
        '''error'''
        szString = BaseDUT.process_newline_foroam(szString)
        if self.debug_enable:
            consolelog_logger.error(szString, exc_info=exc_info)
            filelog_logger.error(szString, exc_info=exc_info)
        self.log(szString)

    def log(self, szString):
        '''每次的日志文件名都不同，以脚本运行的时间命名日志文件名称 '''
        current_dir = os.getcwd()
        log_file = os.path.join(current_dir, 'log', self.logfilename)
        file_dir = os.path.split(log_file)[0]
        if not os.path.isdir(file_dir):
            os.makedirs(file_dir)

        if self.log_enable:
            with open(log_file, 'a') as f:
                datefmt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[0:-3]
                # szString = BaseDUT.process_newline_foroam(szString)
                f.write(datefmt+': '+szString + '\n')

    def oam_print(self, szString, end_flag=''):
        if self.log_enable:
            szString = BaseDUT.to_str(szString)
            szString = BaseDUT.process_newline_foroam(szString)
            # print(szString, end=end_flag, flush=True)
            print(szString)
            self.log(szString)

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
            self.debug('Begin to connect the DUT!')
            if protocol == 'telnet':
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
                    self.error("telnet {} failed: {}".format(self.host, e))
                    self.login_fail_info = e
                    return False

                self.tn.set_option_negotiation_callback(option_negotiation_callback)

                tResult = self.tn.expect([b'sername:'], waittime)
                self.oam_print(tResult[2])
                self.tn.write(self.username.encode() + BaseDUT.CRLF)
                self.oam_print(self.tn.read_until(b'assword:'))
                self.tn.write(self.password.encode() + BaseDUT.CRLF)

                tResult = self.tn.expect([b'#', b'>', b'error'], waittime)
                if tResult[0] == -1:
                    # 未读取到
                    e = 'Don\'t find system prompt!'
                    self.error("telnet {} failed: {}".format(self.host, e))
                    self.login_fail_info = e
                    return False
                elif tResult[0] == 2:
                    e = 'Username or password error!'
                    self.error("telnet {} failed: {}".format(self.host, e))
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
                        self.debug("telnet {} successful".format(self.host))
                        return True
                elif tResult[0] == 0:
                    self.debug("telnet {} successful".format(self.host))
                    return True

            elif protocol == 'ssh':
                if port == 23:
                    port = 22
                self.sshlib = __import__('autosshlib')

                try:
                    self.tn = self.sshlib.ssh(self.host, port, self.username, self.password, False, timeout)
                    tResult = self.tn.expect([b'#', b'>'], waittime)
                    if tResult[0] == -1:
                        # 未读取到
                        e = 'Don\'t find system prompt!'
                        self.error("ssh {} failed: {}".format(self.host, e))
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
                            self.debug("ssh {} successful".format(self.host))
                            return True
                    elif tResult[0] == 0:
                        self.debug("ssh {} successful".format(self.host))
                        return True
                except Exception as e:
                    self.error("ssh {} failed: {}".format(self.host, e))
                    self.login_fail_info = e
                    return False

    def close(self):
        '''
        关闭当前DUT会话
        '''
        self.debug('\nThe current DUT connection is closed !\n')
        self.tn.close()

    def __del__(self):
        # 脚本运行结束时，在屏幕上打印2个空行，便于好看
        self.close()
        self.oam_print('\n\n')

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
            # tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.', b'\r\n'], timeout)
            # self.oam_print(tResult[2])
            # if tResult[0] == 4 or tResult[0] == 3:
            #     continue
            tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.'], timeout)
            self.oam_print(tResult[2])
            if tResult[0] == 3:
                continue
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

    def rec(self, szCommand, prompt='#', timeout=60):
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
            tResult = self.tn.expect([prompt, b' --More--', b'\r\n'], timeout)
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

    def rec2(self, szCommand, prompt='#', timeout=60):
        '''接收原始数据，开始的命令回显和末尾的设备提示符都没有删除'''
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        self.tn.write(szCommand+BaseDUT.CRLF)
        szResult = b''
        while True:
            tResult = self.tn.expect([prompt, b' --More--', b'\r\n'], timeout)
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
