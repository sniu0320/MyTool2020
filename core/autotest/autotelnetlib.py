# -*- coding: UTF-8 -*-
import datetime
import logging
import logging.handlers
import os
import re
import sys
import telnetlib
import time

# ########################  初始化日志模块  #########################
current_dir = os.getcwd()
log_file = os.path.join(current_dir, 'log', 'aotutest.log')
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

# ############################# 全局变量 ##############################

basemac = '00:22:22:22:22:22'
ip_firstbyte = 10

# 1 : 所有接口共用一个mac地址；2 : 每个接口mac地址不同
mactype = 2

txtfilename = 'config_'+time.strftime('%Y.%m.%d.%H.%M.%S')+'.txt'
txtfileobj = None
# ############################# 全局函数 ##############################


def txt(szCommand):
    '''把命令写入文本文件'''
    global txtfileobj
    if not txtfileobj:
        # 创建文件
        txtfileobj = open(txtfilename, 'a')
    txtfileobj.write(szCommand+'\n')


def setTxtFileName(filename):
    global txtfileobj
    global txtfilename
    if txtfileobj:
        txtfileobj.close()
        txtfileobj = None
    txtfilename = filename


def sleep(ms):
    '''time.sleep'''
    time.sleep(ms/1000.0)


def timestamp():
    '''return time.time'''
    return time.time()


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


def miboid2char(oid):
    '''
    把mib的oid值转为字符串：
    例子：oid = 120.103.101.105.45.48.47.49.48.47.48.47.49.49.58.51
    转换后是：xgei-0/10/0/11:3
    '''
    ascii_list = oid.split('.')
    szString = ''
    for ascii in ascii_list:
        szString += chr(int(ascii))
    return szString


# ########################### 定义类 #################################
class BaseDUT(object):
    """基础DUT类，公共函数统一放置于此"""

    CRLF = b'\r'

    # ----------------------------------------------------------------------
    def __init__(self, debug=True, log_switch=True):
        """Constructor"""
        self.logfilename = time.strftime('%Y.%m.%d.%H.%M.%S')+'.log'
        self.debug = debug
        self.log_switch = log_switch

    def shell_print(self, szString, end_flag=''):
        if self.debug:
            szString = BaseDUT.to_str(szString)
            szString = BaseDUT.process_newline_forshell(szString)
            # end -- 用来设定以什么结尾。默认值是换行符 \n，我们可以换成其他字符串
            # flush -- 输出是否被缓存通常决定于 file，但如果 flush 关键字参数为 True，流会被强制刷新。
            # 比如打点:Loading..........
            # print("Loading",end = "")
            # for i in range(20):
            #     print(".",end = '',flush = True)
            #     time.sleep(0.5)
            print(szString, end=end_flag, flush=True)

    def oam_print(self, szString, end_flag=''):
        if self.debug:
            szString = BaseDUT.to_str(szString)
            szString = BaseDUT.process_newline_foroam(szString)
            print(szString, end=end_flag, flush=True)

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

    @staticmethod
    def process_newline_forshell(szString):
        r'''把字符串中的\r\n统一转为\n'''
        szString = szString.replace('\r\n', '\n')
        return szString

    def logger(self, szString):
        '''文件日志'''
        szString = BaseDUT.process_newline_forshell(szString)
        filelog_logger.info(szString)

    def conlogger(self, szString):
        '''控制台日志,支持多线程'''
        if self.log_switch:
            szString = BaseDUT.process_newline_forshell(szString)
            consolelog_logger.info(szString)

    def logecho(self, szString):
        '''文件和控制台都打印'''
        self.logger(szString)
        self.conlogger(szString)

    def log(self, szString):
        '''每次的日志文件名都不同，以脚本运行的时间命名日志文件名称 '''
        with open(self.logfilename, 'a') as f:
            datefmt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[0:-3]
            szString = BaseDUT.process_newline_forshell(szString)
            f.write(datefmt+'->'+szString + '\n')

    def setlogfilename(self, szString):
        '''修改log函数保存文件名的前缀'''
        self.logfilename = szString + '_' + time.strftime('%Y.%m.%d.%H.%M.%S')+'.log'

    @staticmethod
    def sleep(ms):
        '''time.sleep'''
        time.sleep(ms/1000.0)

    @staticmethod
    def timestamp():
        '''time.time'''
        return time.time()

    @staticmethod
    def dec2hex(num):
        '''将10进制整数转换成16进制,并去掉前边的0x'''
        num_temp = hex(num)
        return num_temp[2:]

    @staticmethod
    def getrowcnt(szString):
        '''return szString行数'''
        if (szString == ''):
            return 0
        else:
            szString_temp = szString.split('\n')
            return len(szString_temp)

    @staticmethod
    def listfind(szString, list):
        '''
        在list中 查找是否存在szString:
        如果存在return list index,
        如果找不到 return None.
        '''
        index = 0
        while index < len(list):
            if szString in list[index]:
                return index
            index = index + 1
        return None

    @staticmethod
    def getrow(szString, row):
        '''return 指定的某行的字符串'''
        if (szString == ''):
            return 0
        else:
            szString_temp = szString.split('\n')
            return szString_temp[row]

    @staticmethod
    def getstring(szString, row, column):
        '''return 指定的某行某列的字符串'''
        if (szString == ''):
            return ''
        else:
            szString_temp = szString.split('\n')
            szString_temp = szString_temp[row]
            szString_temp = szString_temp.split()
            return szString_temp[column]

    @staticmethod
    def getcolumn(szString, column):
        '''return szString 某列字符串的一个列表'''
        columnlist = []
        if (szString == ''):
            return columnlist
        else:
            for row in range(0, BaseDUT.getrowcnt(szString)):
                columnlist.append(BaseDUT.getstring(szString, row, column))
            return columnlist

    @staticmethod
    def readportlist(filename='portlist.py'):
        '''读取文件，返回一个端口列表，’#‘行会被识别为注释，丢弃'''
        with open(filename, 'r') as f:
            portlist = f.readlines()
            for index in range(0, len(portlist)):
                portlist[index] = portlist[index].strip()
                # 支持注释功能
                if '#' in portlist[index]:
                    portlist[index] = ''
            while '' in portlist:
                portlist.remove('')
        return portlist

    @staticmethod
    def readtxt(filename):
        '''
        读取一个文本文件，返回列表，每行数据作为一个元素，
        ’#‘行会被识别为注释，丢弃
        '''
        with open(filename, 'r') as f:
            szlist = f.readlines()
            for index in range(0, len(szlist)):
                szlist[index] = szlist[index].strip()
                # 支持注释功能
                if '#' in szlist[index]:
                    szlist[index] = ''
            while '' in szlist:
                szlist.remove('')
        return szlist

    @staticmethod
    def readtxt_raw(filename):
        '''读取一个文本文件，返回列表，每行数据作为一个元素'''
        with open(filename, 'r') as f:
            szlist = f.readlines()
        return szlist

    @staticmethod
    def readtxt_all(filename):
        '''读取一个文本文件，返回str'''
        with open(filename, 'r') as f:
            temp = f.read()
        return temp

    @staticmethod
    def nextipv4addr(startipv4addr, step, netmask=24):
        '''根据起始ip地址，步长，掩码，计算ip地址'''
        szipv4addrlist = startipv4addr.split('.')
        intValue = int(szipv4addrlist[0])*256*256*256 + int(szipv4addrlist[1])*256*256 + int(szipv4addrlist[2])*256 + int(szipv4addrlist[3])
        stepValue = step << (32 - netmask)
        intValue_new = intValue + stepValue
        if intValue_new > 4294967295:
            raise Exception('Value Error', 'exceed the max value !!')
        ipv4addr1 = intValue_new / 16777216
        temp = intValue_new % 16777216
        ipv4addr2 = temp / 65536
        ipv4addr3 = (temp % 65536) / 256
        ipv4addr4 = intValue_new % 256
        return str(ipv4addr1)+'.'+str(ipv4addr2)+'.'+str(ipv4addr3)+'.'+str(ipv4addr4)

    @staticmethod
    def nextipv6addr(startipv6addr, step, netmask=48):
        '''根据起始ip地址，步长，掩码，计算ip地址'''
        szipv6addrlist = startipv6addr.split(':')
        length = len(szipv6addrlist)
        if startipv6addr.startswith('::'):
            szipv6addrlist.remove('')
            szipv6addrlist[0] = ('0:'*(10-length))[:-1]
        elif startipv6addr.endswith('::'):
            szipv6addrlist.remove('')
            szipv6addrlist[-1] = ('0:'*(10-length))[:-1]
        elif length < 8:
            for index in range(length) :
                if szipv6addrlist[index] == '':
                    szipv6addrlist[index] = ('0:'*(9-length))[:-1]
                    break

        startipv6addr = ':'.join(szipv6addrlist)
        szipv6addrlist = startipv6addr.split(':')
        for index in range(8):
            szipv6addrlist[index] = int(szipv6addrlist[index],16)
        index = (netmask / 16) - 1
        szipv6addrlist[index] = szipv6addrlist[index] + step
        while index > -1:
            if szipv6addrlist[index] > 65535:
                szipv6addrlist[index-1] = szipv6addrlist[index-1] + (szipv6addrlist[index] / 65536)
                szipv6addrlist[index] = szipv6addrlist[index] % 65536
                index = index - 1
            else:
                break
        for index in range(8):
            szipv6addrlist[index] = hex(szipv6addrlist[index])[2:]
        szResult = ':'.join(szipv6addrlist)

        if szResult.startswith('0:0:'):
            return re.sub(r'(0:){2,}', '::', szResult, count=1)
        else:
            szResult = re.sub(r'(:0){2,}', ':', szResult, count=1)
            if szResult.endswith(':'):
                return szResult + ':'
            return szResult

    @staticmethod
    def mac_address_400g(port):
        '''计算400G版本端口的mac地址'''
        shelf, slot, np, portid = port.split('-')[1].split('/')
        if (mactype == 1):
            delta = 0
        elif (mactype == 2):
            delta = int(shelf)*720 + int(slot)*40 + int(np)*10 + int(portid) + 256
        basemac_temp = basemac.split(':')[::-1]
        for i in range(0, 5):
            basemac_temp[i] = '0x' + basemac_temp[i]
            mac = eval(basemac_temp[i]) + delta
            if (mac > 255):
                basemac_temp[i] = '%02x' % (mac % 256)
                delta = mac/256
            else:
                basemac_temp[i] = '%02x' % mac
                break
        basemac_temp = basemac_temp[::-1]
        return basemac_temp[0]+basemac_temp[1]+'.'+basemac_temp[2]+basemac_temp[3]+'.'+basemac_temp[4]+basemac_temp[5]

    @staticmethod
    def mac_address_1t(port):
        shelf, slot, np, portid, portid2 = BaseDUT.portdecode(port)
        if (mactype == 1):
            delta = 0
        elif (mactype == 2):
            if (portid2 == '0'):
                delta = int(shelf)*1728 + int(slot)*192 + int(np)*48 + int(portid) + 256
            else:
                delta = int(shelf)*1728 + int(slot)*192 + int(np)*48 + int(portid)*256 + int(portid2) + 256
        basemac_temp = basemac.split(':')[::-1]
        for i in range(0,5):
            basemac_temp[i] = '0x' + basemac_temp[i]
            mac = eval(basemac_temp[i]) + delta
            if (mac > 255):
                basemac_temp[i] = '%02x' % (mac % 256)
                delta = mac/256
            else:
                basemac_temp[i] = '%02x' % mac
                break
        basemac_temp = basemac_temp[::-1]
        return basemac_temp[0]+basemac_temp[1]+'.'+basemac_temp[2]+basemac_temp[3]+'.'+basemac_temp[4]+basemac_temp[5]

    @staticmethod
    def portdecodetostr(port):
        '''端口解析为字符串，用于snake流量配置vrf时，用作RD，防止RD冲突'''
        shelf, slot, np, portid = port.split('-')[1].split('/')
        # 对4.00.10扇出口的支持
        portid = portid.replace(':', '')
        return '1'+shelf+slot+np+portid

    @staticmethod
    def portdecode(port):
        '''解析端口的shelf slot np portid等信息，支持1分4'''
        portid2 = '0'
        shelf, slot, np, portid = port.split('-')[1].split('/')
        if (':' in portid):
            portid, portid2 = portid.split(':')
        return (shelf, slot, np, portid, portid2)

    @staticmethod
    def shelf_slot_decode(board):
        '''解析单板的shelf slot信息'''
        shelf, slot, cpu = board.split('-')[1].split('/')
        return (shelf, slot)

    @staticmethod
    def ipv4_addr(port, subcardportnum):
        '''返回端口标准v4地址'''
        shelf, slot, subcard, portid = port.split('-')[1].split('/')
        return str(ip_firstbyte+int(shelf)) + '.' + slot + '.' + str(int(subcard)*subcardportnum+int(portid)) + '.1'

    @staticmethod
    def ipv6_addr(port, subcardportnum):
        '''返回端口标准v6地址'''
        shelf, slot, subcard, portid = port.split('-')[1].split('/')
        return str(ip_firstbyte+int(shelf)) + ':' + slot + ':' + hex(int(subcard)*subcardportnum+int(portid))[2:] + '::1'

    # @staticmethod
    # def ipv4_addr_v4(port):
    #     '''已废弃。原先扇出口地址配置'''
    #     shelf, slot, np, portid, portid2 = BaseDUT.portdecode(port)
    #     return str(ip_firstbyte+int(shelf))+'.'+ slot + '.'+ str(int(np)*48+int(portid)*4 +int(	portid2))+'.1'

    # @staticmethod
    # def ipv6_addr_v4(port):
    #     '''已废弃。原先扇出口地址配置'''
    #     shelf, slot, np, portid, portid2 = BaseDUT.portdecode(port)
    #     return str(ip_firstbyte+int(shelf))+':'+ slot + ':'+ str(int(np)*48+int(portid)*4 + int(portid2))+'::1'

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


class DUT(BaseDUT):
    '''
    利用python自带的telnet库实现此类
    '''
    def __init__(self,
                 host=None,
                 port=23,
                 username='who',
                 password='who',
                 password_enable='zxr10',
                 protocol='telnet',
                 timeout=5,
                 waittime=3,
                 compress=False,
                 debug=True,
                 log_switch=True):
        super().__init__(debug, log_switch)
        self.host = host
        self.port = port
        self.username = username.encode()
        self.password = password.encode()
        self.password_enable = password_enable.encode()
        self.protocol = protocol
        self.timeout = timeout  # login timeout
        self.waittime = waittime
        self.compress = compress
        # 干啥用呢？
        self.sendwithlogfilename = 'sendwithlog_'+time.strftime('%Y.%m.%d.%H.%M.%S')+'.txt'
        self.sendwithlogfileobj = None

        if self.host:
            # 这里可以增加ping测试 todo
            self.conlogger('Begin to connect the DUT !')
            if protocol == 'telnet':
                try:
                    self.tn = telnetlib.Telnet(self.host, self.port, self.timeout)
                except Exception as e:
                    self.conlogger(self.host+' connect failed !')
                    raise e
                self.tn.set_option_negotiation_callback(option_negotiation_callback)

                tResult = self.tn.expect([b'sername:', b'\(none\) login:'], self.waittime)
                if tResult[0] == 1 :
                    self.conlogger('login prompt is : (none) login ! it is sys mode !')
                    raise Exception('sysmode Error', 'it is sys mode !')
                elif tResult[0] == -1 :
                    self.conlogger('Don\'t find login prompt !! maybe it is timeout !')
                    raise Exception('Login Error', 'Don\'t find login prompt!! maybe it is timeout !')
                self.oam_print(tResult[2])
                self.tn.write(self.username + BaseDUT.CRLF)
                self.oam_print(self.tn.read_until(b'assword:'))
                self.tn.write(self.password + BaseDUT.CRLF)
                tResult = self.tn.expect([b'#', b'>', b' \$ ', b'~ # '], self.waittime)
                if tResult[0] == -1:
                    self.conlogger('Don\'t find system prompt !! maybe the password is wrong !!')
                    raise Exception('password Error', 'Don\'t find system prompt !!')
                self.oam_print(tResult[2])
                self.tn.write('enable'.encode() + BaseDUT.CRLF)
                self.oam_print(self.tn.read_until(b'assword:'))
                self.tn.write(self.password_enable + BaseDUT.CRLF)

            elif protocol == 'ssh':
                if self.port == 23:
                    self.port = 22
                self.sshlib = __import__('autosshlib')

                try:
                    self.tn = self.sshlib.ssh(self.host, self.port, self.username, self.password, self.compress, self.timeout)
                    tResult = self.tn.expect([b'#', b'>', b' \$ ', b'~ # '], self.waittime)
                    self.oam_print(tResult[2])
                    self.tn.write('enable'.encode() + BaseDUT.CRLF)
                    self.oam_print(self.tn.read_until(b'assword:'))
                    self.tn.write(self.password_enable + BaseDUT.CRLF)
                except Exception as e:
                    self.conlogger(self.host+' connect failed !!')
                    raise e
 
    def send(self,szCommand,delay = 0, timeout = 60):
        '''遇到错误就会停止，方便查看，主要用于配置设备'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        while True :
            tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.', b'\r\n'],timeout)
            self.oam_print(tResult[2])
            if tResult[0] == 3 or tResult[0] == 4 :
                continue
            elif tResult[0] == 0 :
                break
            elif tResult[0] == 1 :
                self.tn.write(b' ')
                continue
            elif tResult[0] == 2 :
                tResult = self.tn.expect([b'again', b'#'])
                if tResult[0] == 0 :
                    #给100次重试的机会！
                    for retry in range(1,101):
                        self.oam_print(tResult[2])
                        self.oam_print(self.tn.read_until(b'#'))
                        self.sleep(retry*500)
                        self.tn.write(szCommand+BaseDUT.CRLF)
                        tResult = self.tn.expect([b'again', b'#'])
                        if tResult[0] == 1 :
                            self.oam_print(tResult[2])
                            break
                        elif retry == 100 :
                            szResult = tResult[2] + self.tn.read_until(b'#')
                            self.oam_print(szResult)
                            self.logger('\n'+szResult.decode())
                            sys.exit(0)
                    break
                elif tResult[0] == 1 :
                    self.oam_print(tResult[2])
                    self.logger('\r\n'+'%Error '+tResult[2].decode())
                    sys.exit(0)
        if (delay != 0):
            self.sleep(delay)
 
    def send2(self,szCommand,delay = 0, timeout = 60):
        '''遇到一般错误不会停止，继续执行'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        while True :
            tResult = self.tn.expect([b'#', b'--More--', b'%Error ', b'\.\.', b'\r\n'],timeout)
            self.oam_print(tResult[2])
            if tResult[0] == 4 or tResult[0] == 3 :
                continue
            elif tResult[0] == 0 :
                break
            elif tResult[0] == 1 :
                self.tn.write(b' ')
                continue
            elif tResult[0] == 2 :
                tResult = self.tn.expect([b'again', b'#'])
                if tResult[0] == 0 :
                    #给100次重试的机会！
                    for retry in range(1,101):
                        self.oam_print(tResult[2])
                        self.oam_print(self.tn.read_until(b'#'))
                        self.sleep(retry*500)
                        self.tn.write(szCommand+BaseDUT.CRLF)
                        tResult = self.tn.expect([b'again', b'#'])
                        if tResult[0] == 1 :
                            self.oam_print(tResult[2])
                            break
                        elif retry == 100 :
                            self.oam_print(tResult[2])
                            self.oam_print(self.tn.read_until(b'#'))
                    break
                else :
                    self.oam_print(tResult[2])
                    break
        if (delay != 0):
            self.sleep(delay)
 
    def send3(self,szCommand):
        '''只发送命令，不关心执行的结果,慎用!!'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        #ssh 协议有流控，一直不读sockets，会使服务端不能继续发送内容
        self.sleep(15)
        self.oam_print(self.tn.read_eager())
        
    def sendwithoutwait(self,szCommand):
        '''只发送命令，不关心执行的结果,慎用!!'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
                            
    def sendexpect(self,send,expect,timeout = 60):
        send = send.encode()
        expect = expect.encode()
        self.tn.write(send + BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'],timeout)
        self.oam_print(tResult[2])
        tResult = self.tn.expect([expect],timeout)
        self.oam_print(tResult[2])
        self.oam_print(self.tn.read_lazy())
        if tResult[0] == -1 :
            return False
        else :
            return True
 
    def sendctrl(self,char,prompt = '#'):
        '''目前仅支持字符C和字符X'''
        prompt = prompt.encode()
        if (char == 'c'):
            self.tn.write(b'\3')
            self.oam_print(self.tn.read_until(prompt))
        elif (char == 'x'):
            self.tn.write(b'\30')
            
    def sendwithlog(self,szCommand):
        '''发送命令的同时，把命令写入文本文件'''
        self.send(szCommand.encode())
        if not self.sendwithlogfileobj :
            self.sendwithlogfileobj = open(self.sendwithlogfilename,'a')
        self.sendwithlogfileobj.write(szCommand+'\n')
 
    def con_t(self):
        self.sendctrl('c')
        self.sendctrl('c')
        self.send('configure terminal')
        
    def rec(self,szCommand, prompt = '#', timeout = 60):
        '''
        接收命令的返回结果，命令的回显和末尾的设备提示符已经删除！！
        '''
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        
        self.tn.write(szCommand+BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'],timeout)
        self.oam_print(tResult[2])
        szResult = b''
        while True:
            tResult = self.tn.expect([prompt, b' --More--', b'\r\n'],timeout)
            szResult = szResult + tResult[2]
            self.oam_print(tResult[2])	
            if tResult[0] == 0 :
                break
            elif tResult[0] == 1 :
                self.tn.write(b' ')
 
        szResult = szResult.decode()
        szResult = szResult.replace('\b \b','')
        szResult = szResult.replace(' --More--','')
        if (szResult.rfind('\r\n') == -1):
            return ''
        else:
            szResult = szResult.rsplit('\r\n',1)
            return BaseDUT.process_newline_forshell(szResult[0])
        
    def rec2(self,szCommand, prompt = '#', timeout = 60):
        '''接收原始数据，开始的命令回显和末尾的设备提示符都没有删除'''
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        self.tn.write(szCommand+BaseDUT.CRLF)
        szResult = b''
        while True:
            tResult = self.tn.expect([prompt, b' --More--', b'\r\n'],timeout)
            szResult = szResult + tResult[2]
            self.oam_print(tResult[2])	
            if tResult[0] == 0 :
                break
            elif tResult[0] == 1 :
                self.tn.write(b' ')
 
        szResult = szResult.decode()
        
        szResult = szResult.replace('\b \b','')
        szResult = szResult.replace(' --More--','')
        return BaseDUT.process_newline_forshell(szResult)
    
    def rec_raw(self,szCommand, prompt = '#', timeout = 60):
        self.rec2(szCommand, prompt, timeout)
        
    def reconnect(self, retry_cnt = 1000):
        '''重新连接设备'''
        for retry in range(0, retry_cnt):
            try:
                self.oam_print('Begin to reconnect the DUT !\n')
                if self.protocol == 'telnet':
                    self.tn = telnetlib.Telnet(self.host,self.port)
                    tResult = self.tn.expect([b'sername:', b'login:'])
                    self.oam_print(tResult[2])
                    self.tn.write(self.username + BaseDUT.CRLF)
                    self.oam_print(self.tn.read_until(b'assword:'))
                    self.tn.write(self.password + BaseDUT.CRLF)
                    tResult = self.tn.expect([b'#', b'>', b' \$ ', b'~ # '])
                    self.oam_print(tResult[2])
                elif self.protocol == 'ssh':
                    self.tn = self.sshlib.ssh(self.host, self.port, self.username, self.password, self.compress, self.timeout)
                    tResult = self.tn.expect([b'#', b'>', b' \$ ', b'~ # '],2)
                    self.oam_print(tResult[2])
                break
            except:
                self.oam_print('reconnect failed !\n')
                self.sleep(30000)
                continue
            
    def isSynchronized(self):
        szResult = self.rec('show synchronization | include MPU')
        if szResult.count('Master') * 2 != szResult.count('Synchronized'):
            self.conlogger('系统当前不是Synchronized状态！')		
            return False
        return True
    
    def WaitSynchronized(self):
        while True :
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
        
    def redundancyswitch(self,le='sc',interval=10,switch_cnt=10,config_check=True,ospf_check=True,
                         isis_check=True,bgp_check=True,ldp_check=True,pim_check=True,retry_cnt=1200):
        self.logecho('\n============================== RESTART ==============================')
        self.logecho('系统开始主备倒换测试，当前倒换的逻辑实体是:' + le)
        #用ctrl c 确保在特权模式下
        self.sendctrl('c')
        self.logecho('开始判断系统倒换前的同步状态')
        
        #给 retry_cnt 次判断同步的机会
        for retry in range(0,retry_cnt):
            if not self.isSynchronized() :
                self.conlogger('系统当前不是Synchronized状态，不能进行主备倒换！')
                self.conlogger('30秒后，重新进行一次主备同步状态判断')
                if retry == retry_cnt - 1 :
                    self.logecho('%d 次机会用完了，依然未同步，倒换测试失败！' %retry_cnt)
                    self.logger(self.rec('show synchronization | include MPU'))
                    return False
                else :
                    self.close()
                    self.sleep(30000)
                    self.reconnect()
                    continue
            else :
                break
        self.logecho('系统处于Synchronized状态，具备倒换的条件，可以开始倒换了！')
        if (config_check == True):
            self.logecho('开始获取倒换前，系统的配置文件！')
            running_config_old = self.rec('sho running-config')
        self.logecho('开始清除系统告警日志！')
        self.send('clear logging')
        self.logecho('倒换测试正式开始！')
        
        for i in range(1,switch_cnt+1):
            self.logecho('开始第 %d 次倒换，当前倒换的逻辑实体是：%s' % (i, le))
            self.logger('倒换前 主备状态如下：\n' + self.rec('show synchronization | include MPU'))
            if (le == 'sc' or le == 'rp-router'):
                self.sendexpect('redundancy switch '+le+' grace',':')
            elif (le == 'mpls'):
                self.sendexpect('redundancy switch '+le,':')
            self.send3('yes')
            self.close()
            _begintime = self.timestamp()
            self.logecho('%d 分钟后，会重新登陆设备，请耐心等待！' % interval)
            self.sleep(interval*60*1000)
            self.reconnect()
            if (config_check == True):
                self.logecho('开始获取倒换后，系统的配置文件！')
                running_config_new = self.rec('sho running-config')
                if (running_config_new != running_config_old):
                    self.logecho('系统倒换前后的配置不一致，请用比较软件比较保存在脚本目录的配置文件！')
                    with open('running_config_new.txt','w') as f:
                        f.write(running_config_new)
                    with open('running_config_old.txt','w') as f:
                        f.write(running_config_old)
                    return False
            #判断系统同步状态
            self.logecho('开始判断倒换后，系统的主备同步状态！')
 
            #给 retry_cnt 次判断同步的机会
            for retry in range(0,retry_cnt):
                if not self.isSynchronized() :
                    self.conlogger('倒换后，系统不是Synchronized状态！')
                    self.conlogger('30秒后，重新进行一次主备同步状态判断')
                    if retry == retry_cnt - 1 :
                        self.logecho('%d 次机会用完了，依然未同步，倒换测试失败！' % retry_cnt)
                        self.logger(self.rec('show synchronization | include MPU'))
                        return False
                    else :
                        self.close()
                        self.sleep(30000)
                        self.reconnect()
                        continue
                else :
                    self.logecho('倒换后，系统是Synchronized状态！')
                    break
                
            #计算倒换后同步所消耗的时间
            _endtime = self.timestamp()
            #unit: min
            _syn_time = (_endtime - _begintime) / 60
            self.logecho('主备倒换后，同步时间为：%f 分钟'% _syn_time)
            
            #判断路由是否发生震荡
            self.logecho('开始判断倒换过程中，系统的路由协议震荡情况！')
            if (ospf_check == True):
                szResult = self.rec('show logging alarm typeid ospf | include [Dd][Oo][Ww][Nn]')
                if ( szResult != ''):
                    self.logecho('倒换过程中，ospf协议出现震荡！')
                    self.logger('\n'+szResult)
                    return False
            if (isis_check == True):
                szResult = self.rec('show logging alarm typeid isis | include [Dd][Oo][Ww][Nn]')
                if ( szResult != ''):
                    self.logecho('倒换过程中，isis协议出现震荡！')
                    self.logger('\n'+szResult)
                    return False
            if (bgp_check == True):
                szResult = self.rec('show logging alarm typeid bgp | include [Dd][Oo][Ww][Nn]')
                if ( szResult != ''):
                    self.logecho('倒换过程中，bgp协议出现震荡！')
                    self.logger('\n'+szResult)
                    return False
            if (ldp_check == True):
                szResult = self.rec('show logging alarm typeid ldp | include [Dd][Oo][Ww][Nn]')
                if ( szResult != ''):
                    self.logecho('倒换过程中，ldp协议出现震荡！')
                    self.logger('\n'+szResult)
                    return False
            if (pim_check == True):
                szResult = self.rec('show logging alarm typeid pim | include [Dd][Oo][Ww][Nn]')
                if ( szResult != ''):
                    self.logecho('倒换过程中，pim协议出现震荡！')
                    self.logger('\n'+szResult)
                    return False
            self.logecho('第 %d 次倒换顺利结束，当前倒换的逻辑实体是：%s' % (i, le))
        self.logecho('%d 次倒换全部顺利结束，当前倒换的逻辑实体是：%s' % (switch_cnt, le))
        return True
    
    def migratele(self, mpu, le = 'sc'):
        self.sendctrl('c')
        self.send('con t')
        self.send('placement le %s' % le)
        temp = self.rec('locate-set slave %s' % mpu)
        if 'Incomplete command' in  temp :
            self.sendexpect('locate-set slave %s force' % mpu, 'no')
            self.send('yes')
        self.sendctrl('c')
    
    def close(self):
        '''
        关闭当前DUT会话
        '''
        self.conlogger('\nThe current DUT connection is closed !\n')
        self.tn.close()
 
    def __del__(self):
        if self.sendwithlogfileobj :
            self.sendwithlogfileobj.close()
            
        #脚本运行结束时，在屏幕上打印2个空行，便于好看
        self.oam_print('\n\n')
        
        # self.conlogger('按任意键退出！！！')
        # input()
 
class ushell(BaseDUT):
    '''
    登陆系统的ushell,执行调试函数
    '''
    def __init__(self,mng_ipaddr,board_ipaddr,timeout=5, waittime = 10, debug=True, log_switch = True):
        super().__init__(debug, log_switch)
        self.mng_ipaddr = mng_ipaddr
        self.board_ipaddr = board_ipaddr
        self.timeout = timeout
        self.waittime = waittime
        #self.debug = debug
        self.username = b'zte'
        self.password = b'zte'
        self.shell_print('Begin to connect the ushell !\n')
        #开始登陆 主控板
        try :
            self.tn = telnetlib.Telnet(self.mng_ipaddr,23,self.timeout)
        except :
            self.conlogger('Establish to the mng_ipaddr is failed!(%s--%s)'%(self.mng_ipaddr,self.board_ipaddr))
            raise Exception('Establish failed', '%s--%s'%(self.mng_ipaddr,self.board_ipaddr))
        tResult = self.tn.expect([b'login:'],self.waittime)
        if tResult[0] == -1 :
            self.conlogger('Don\'t find login prompt !! maybe it is oam mode !')
            raise Exception('Login Error', 'Don\'t find login prompt!!')
        self.shell_print(tResult[2])
        self.tn.write(self.username + BaseDUT.CRLF)
        self.shell_print(self.tn.read_until(b'assword:'))
        self.tn.write(self.password + BaseDUT.CRLF)
        tResult = self.tn.expect([b'~ \$ '],self.waittime)
        if tResult[0] == -1 :
            self.logecho('Don\'t find system prompt !! maybe the password is wrong !!')
            raise Exception('Login Error', 'Don\'t find system prompt!!')
        self.shell_print(tResult[2])
        #开始登陆 普通板卡
        cmd = 'telnet %s 10000\r'% self.board_ipaddr
        self.tn.write(cmd.encode())
        tResult = self.tn.expect([b'login:'], self.waittime)
        self.shell_print(tResult[2])
        if tResult[0] == -1 :
            self.logecho('The Board:%s--%s is offline!'%(self.mng_ipaddr,self.board_ipaddr))
            raise Exception('Board offline!',self.board_ipaddr)
        self.tn.write(self.username + BaseDUT.CRLF)
        self.shell_print(self.tn.read_until(b'assword:'))
        self.tn.write(self.password + BaseDUT.CRLF)
        self.tn.write(BaseDUT.CRLF)
        tResult = self.tn.expect([b'#'], self.waittime)
        self.shell_print(tResult[2])
                    
    def send(self,szCommand,delay = 0):
        szCommand = szCommand.encode()
        crlf_cnt = 0
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        
        while True :
            if crlf_cnt > 2 :
                timeout = 2
            else :
                timeout = 60
            tResult = self.tn.expect([b'.*#', b'end  time.*ms', b'\r\n'],timeout)
            self.shell_print(tResult[2])
            if tResult[0] == 2 :
                crlf_cnt = crlf_cnt + 1
                continue
            elif tResult[0] == 0 :
                break
            elif tResult[0] == 1 :
                self.tn.write(BaseDUT.CRLF)
                self.shell_print(self.tn.read_until(b'#'))
                break
            else :
                break
            
        if (delay != 0):
            self.sleep(delay)
 
    def send2(self,szCommand,delay = 0):
        '''只发送命令，不关心执行的结果,慎用!!'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        if (delay != 0):
            self.sleep(delay)
 
    def sendexpect(self,send,expect,timeout = 10):
        send = send.encode()
        expect = expect.encode()
        self.tn.write(send + BaseDUT.CRLF)
        tResult = self.tn.expect([expect],timeout)
        self.shell_print(tResult[2])
        self.shell_print(self.tn.read_lazy())
        if tResult[0] == 0 :
            return True
        else :
            return False
            
    def rec(self,szCommand, prompt = '', timeout = 10):
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        
        self.tn.write(szCommand+BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'],timeout)
        self.shell_print(tResult[2])
        if prompt == b'':
            tResult = self.tn.expect([b'#', b'end  time.*ms'],timeout)
        else :
            tResult = self.tn.expect([prompt],timeout)
        self.shell_print(tResult[2])
        if tResult[0] == 1 :
            self.tn.write(BaseDUT.CRLF)
            self.shell_print(self.tn.read_until(b'#'))
        szResult = tResult[2].decode()
        return BaseDUT.process_newline_forshell(szResult)
    
    def rec_raw(self,szCommand, timeout = 10):
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)		
        tResult = self.tn.expect([b'#', b'end  time.*ms'],timeout)
        self.shell_print(tResult[2])
        if tResult[0] == 1 :
            self.tn.write(BaseDUT.CRLF)
            self.shell_print(self.tn.read_until(b'#'))
        szResult = tResult[2].decode()
        return BaseDUT.process_newline_forshell(szResult)	
 
    def close(self):
        self.shell_print('\nThe current ushell connection is closed !\n')
        self.tn.close()
        
class shell(BaseDUT):
    '''
    登陆系统的linux BSP shell(不带10000号端口),执行调试函数
    '''
    def __init__(self,mng_ipaddr,board_ipaddr,timeout= 5, waittime = 10, debug=True, log_switch = True):
        super().__init__(debug, log_switch)
        self.mng_ipaddr = mng_ipaddr
        self.board_ipaddr = board_ipaddr
        self.timeout = timeout
        self.waittime = waittime
        #self.debug = debug
        self.username = b'zte'
        self.password = b'zte'
        self.shell_print('Begin to connect the linux BSP shell !\n')
        #开始登陆主控板
        try :
            self.tn = telnetlib.Telnet(self.mng_ipaddr,23,self.timeout)
        except :
            self.conlogger('Establish to the mng_ipaddr is failed!(%s--%s)'%(self.mng_ipaddr,self.board_ipaddr))
            raise Exception('Establish failed', '%s--%s'%(self.mng_ipaddr,self.board_ipaddr))
        tResult = self.tn.expect([b'login:'],self.waittime)
        if tResult[0] == -1 :
            self.conlogger('Don\'t find login prompt !! maybe it is oam mode !')
            raise Exception('Login Error', 'Don\'t find login prompt!!')
        self.shell_print(tResult[2])
        self.tn.write(self.username + BaseDUT.CRLF)
        self.shell_print(self.tn.read_until(b'assword:'))
        self.tn.write(self.password + BaseDUT.CRLF)
        tResult = self.tn.expect([b'~ \$ '],self.waittime)
        if tResult[0] == -1 :
            self.conlogger('Don\'t find system prompt !! maybe the password is wrong !!')
            raise Exception('Login Error', 'Don\'t find system prompt!!')
        self.shell_print(tResult[2])
        #开始登陆板卡linux BSP shell
        cmd = 'telnet %s\r'% self.board_ipaddr
        self.tn.write(cmd.encode())
        tResult = self.tn.expect([b'login:'],self.waittime)
        self.shell_print(tResult[2])
        if tResult[0] == -1 :
            self.conlogger('the board:%s--%s is offline!'%(self.mng_ipaddr,self.board_ipaddr))
            raise Exception('Board offline!',self.board_ipaddr)
        self.tn.write(self.username + BaseDUT.CRLF)
        self.shell_print(self.tn.read_until(b'assword:'))
        self.tn.write(self.password + BaseDUT.CRLF)
        tResult = self.tn.expect([b'~ \$ '], self.waittime)
        self.shell_print(tResult[2])
        #需要root权限，否则可能部分操作无法执行
        self.tn.write(b'su' + BaseDUT.CRLF)
        
        tResult = self.tn.expect([b'~ \# '], self.waittime)
        self.shell_print(tResult[2])
                    
    def send(self,szCommand,prompt = ' # ' , delay = 0):
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        crlf_cnt = 0
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        
        while True :
            if crlf_cnt > 2 :
                timeout = 2
            else :
                timeout = 60
            tResult = self.tn.expect([prompt,b'\r\n'],timeout)
            self.shell_print(tResult[2])
            if tResult[0] == 1 :
                crlf_cnt = crlf_cnt + 1
                continue
            elif tResult[0] == 0 :
                break
            else :
                break
        if (delay != 0):
            self.sleep(delay)
 
    def send2(self,szCommand,delay = 0):
        '''只发送命令，不关心执行的结果,慎用!!'''
        szCommand = szCommand.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        if (delay != 0):
            self.sleep(delay)
 
    def sendexpect(self,send,expect,timeout = 10):
        send = send.encode()
        expect = expect.encode()
        self.tn.write(send + BaseDUT.CRLF)
        tResult = self.tn.expect([expect],timeout)
        self.shell_print(tResult[2])
        self.shell_print(self.tn.read_lazy())
        if tResult[0] == 0 :
            return True
        else :
            return False
            
    def rec(self,szCommand , prompt = ' # ', timeout = 10):
        szCommand = szCommand.encode()
        self.tn.write(szCommand+BaseDUT.CRLF)
        tResult = self.tn.expect([b'\r\n'],timeout)
        self.shell_print(tResult[2])
        tResult = self.tn.expect([prompt],timeout)
        self.shell_print(tResult[2])
        
        szResult = tResult[2].decode()
        
        if (szResult.rfind('\r\n') == -1):
            return ''
        else:
            szResult = szResult.rsplit('\r\n',1)
            return BaseDUT.process_newline_forshell(szResult[0])
            
    def rec_raw(self,szCommand , prompt = ' # ', timeout = 10):
        szCommand = szCommand.encode()
        prompt = prompt.encode()
        if (szCommand == b' ' or szCommand == b'\r'):
            self.tn.write(szCommand)
        else :
            self.tn.write(szCommand+BaseDUT.CRLF)
        tResult = self.tn.expect([prompt],timeout)
        self.shell_print(tResult[2])
        szResult = tResult[2].decode()
        return BaseDUT.process_newline_forshell(szResult)
 
    def close(self):
        self.shell_print('\nThe current linux BSP shell connection is closed !\n')
        self.tn.close()
 
class txtFile(BaseDUT):
    '''
    txt文本类，直接打开文本文件，写入命令
    '''
    def __init__(self,path=None,filename=None,mode='w', debug = True):
        super().__init__(debug)
        self.filename = filename
        self.mode = mode
        if path == None:
            self.path = os.path.split(os.path.realpath(__file__))[0]
        else :
            self.path = path
            #import os
            if not os.path.exists(self.path) :
                os.makedirs(self.path.encode("gb2312"))
 
    def setfilename(self,filename):
        self.filename = self.path+'\\' + filename
        self.file=open(self.filename,self.mode)
        
    def write(self,cmd):
        self.file.write(cmd+'\n')
        
    def close(self):
        self.file.close()
