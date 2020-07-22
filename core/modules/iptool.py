# -*- coding: UTF-8 -*-

import ipaddress
import logging
import platform
import subprocess
# from logtool import log_error
import logtool


class ipTool(object):
    """
    ip工具包

    is_ip_Valid(addr): 检查ip地址是否有效

    network_num_hosts(nets): 获取网段主机地址列表

    network_info(net): 打印网段相关信息，支持v6

    network_info(net): 打印网段相关信息，支持v6

    ip_in_network(addr, net): 检查ip地址是否在网段内

    ping_test(addr): ping测试
    """

    def __init__(self):
        pass

    @staticmethod
    def is_ip_Valid(addr):
        """
        检查ip地址是否有效
        :param addr str: '172.11.1.1'
        :return True or False
        """
        try:
            ipaddress.ip_address(addr)
            logging.debug("'{}' is a valid address".format(addr))
            return True
        except ValueError as e:
            logging.error('ValueError:{}'.format(e))
        except Exception as e:
            logging.error(e, exc_info=True)
            return False

    @staticmethod
    def network_num_hosts(nets):
        """
        获取网段主机地址列表（去除了基地址和广播地址），支持v6，nets支持字符串和列表输入。
        :param nets list: ['172.11.3.0/24', '172.11.4.0/24']
        :param nets str: '172.11.5.0/24,172.11.6.0/24'
        :param nets str: '172.11.7.0/24'
        :return host_list
        """
        host_list = []
        if type(nets) is str:
            nets = nets.split(',')
        for n in nets:
            try:
                net = ipaddress.ip_network(n.strip())
                logging.debug('{!r} num hosts: {}'.format(net,
                                                          net.num_addresses-2))
                host_list += net.hosts()  # 去除基地址和广播地址
            except ValueError as e:
                logging.error('ValueError:{}'.format(e))
            except Exception as e:
                logging.error(e, exc_info=True)
        logging.debug('total hosts: {}'.format(len(host_list)))
        return host_list

    @staticmethod
    def network_info(net):
        """
        打印网段相关信息，支持v6
        :param net str: '172.11.7.0/24'

        :print version, is_private, broadcast_address, compressed, \
            netmask, hostmask(反掩码), num_addresses, num_hosts
        """
        try:
            net = ipaddress.ip_network(net.strip())
            print('{!r}'.format(net))
            print('        version:', net.version)
            print('     is private:', net.is_private)
            print('      broadcast:', net.broadcast_address)
            print('     compressed:', net.compressed)
            print('   with netmask:', net.with_netmask)
            print('  with hostmask:', net.with_hostmask)
            print('  num addresses:', net.num_addresses)
            print('      num hosts:', net.num_addresses-2)
            print()
        except ValueError as e:
            logging.error('ValueError:{}'.format(e))
        except Exception as e:
            logging.error(e, exc_info=True)

    @staticmethod
    def interface_info(addr):
        """
        打印网关相关信息，支持v6
        :param addrs str: '172.11.7.6/24'

        :print network, ip, IP with prefixlen, netmask, hostmask(反掩码)
        """
        try:
            iface = ipaddress.ip_interface(addr.strip())
            print('{!r}'.format(iface))
            print('            network:', iface.network)
            print('                 ip:', iface.ip)
            print('  IP with prefixlen:', iface.with_prefixlen)
            print('            netmask:', iface.with_netmask)
            print('           hostmask:', iface.with_hostmask)
            print()
        except ValueError as e:
            logging.error('ValueError:{}'.format(e))
        except Exception as e:
            logging.error(e, exc_info=True)

    @staticmethod
    def ip_in_network(addr, net):
        """
        检查ip地址是否在网段内
        :param addr str: '172.11.1.1'
        :param net str: '172.11.1.0/24'
        :return True or False
        """
        try:
            ip = ipaddress.ip_address(addr)
            net = ipaddress.ip_network(net)
        except ValueError as e:
            logging.error('ValueError:{}'.format(e))
        except Exception as e:
            logging.error(e, exc_info=True)
        else:
            if ip in net:
                logging.debug('{} is on {}'.format(ip, net))
                return True
            else:
                logging.debug('{} is not on {}'.format(ip, net))
                return False

    @staticmethod
    def ping_test(addr):
        """
        ping测试
        :param addr str: ip地址
        :return True or False
        """
        if ipTool.is_ip_Valid(addr):
            logging.debug('ping {}'.format(addr))
            if platform.system() == "Windows":
                cmd = 'ping -w 100 -n %d %s' % (1, addr)
                p = subprocess.Popen(args=cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                (stdoutput, erroutput) = p.communicate()
                output = stdoutput.decode('gbk')
                ttl = output.find("TTL=")
            else:
                cmd = 'ping -W 100 -c %d %s' % (1, addr)
                p = subprocess.Popen(args=cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
                (stdoutput, erroutput) = p.communicate()
                output = stdoutput.decode()
                ttl = output.find("ttl=")
            if ttl >= 0:
                logging.debug("{} is online".format(addr))
                return True
            else:
                logging.debug("{} is not online".format(addr))
                return False


if __name__ == '__main__':
    ipTool.is_ip_Valid('172.1.1.0')
    ipTool.is_ip_Valid('172.1.1.0/24')
    ipTool.network_num_hosts(['172.11.3.0/24', '172.11.4.0/24'])
    ipTool.network_num_hosts('172.11.5.0/24, 172.11.6./24')
    ipTool.network_num_hosts('172.11.7.0/255.255.255.0')
    ipTool.network_info('172.11.0.0/16')
    ipTool.interface_info('172.11.6.1/16')
    ipTool.ip_in_network('172.11.1.2', '172.11.1.0/24')
    ipTool.ping_test('172.11.1.1')
