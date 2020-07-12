# -*- coding: UTF-8 -*-

import ipaddress
import logging


class ipTool(object):
    '''
    ip工具包
    '''

    def __init__(self):
        pass

    @staticmethod
    def is_ip_Valid(addr):
        """
        检查ip地址是否有效
        :param addr
        :return True or False
        """
        try:
            ipaddress.ip_address(addr)
            return True
        # except Exception as e:
        #     print(">>>ERROR: {}".format(e))
        except Exception:
            # logging.error("{} \n".format(addr), exc_info=True)
            logging.error("", exc_info=True)
            return False

    @staticmethod
    def network_hosts(networks):
        """
        输入要查询的网段，输出主机地址list（去除了基地址和广播地址），支持v6，networks支持字符串和列表输入。
        :param networks list: ['172.11.3.0/24', '172.11.4.0/24']
        :param networks str: '172.11.5.0/24, 172.11.6.0/24'
        :param networks str: '172.11.7.0/24'
        :return host_list
        """
        host_list = []
        try:
            if type(networks) is str:
                networks = networks.split(',')
            for n in networks:
                net = ipaddress.ip_network(n.strip())
                logging.debug('{!r}'.format(net))
                host_list += net.hosts()  # 去除基地址和广播地址
        except Exception:
            logging.error("", exc_info=True)
        return host_list

    @staticmethod
    def network_info(networks):
        """
        打印网段相关信息，支持v6，networks支持字符串和列表输入
        :param networks list: ['172.11.3.0/24', '172.11.4.0/24']
        :param networks str: '172.11.5.0/24, 172.11.6.0/24'
        :param networks str: '172.11.7.0/24'

        :print version, is_private, broadcast_address, compressed, \
            netmask, hostmask(反掩码), num_addresses, num_hosts
        """
        try:
            if type(networks) is str:
                networks = networks.split(',')
            for n in networks:
                net = ipaddress.ip_network(n.strip())
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
        except Exception:
            logging.error("", exc_info=True)

    @staticmethod
    def interface_info(addresses):
        """
        打印网关相关信息，支持v6，ip_addresses支持字符串和列表输入
        :param addresses list: ['172.11.3.6/24', '172.11.4.6/24']
        :param addresses str: '172.11.5.6/24, 172.11.6.6/24'
        :param addresses str: '172.11.7.6/24'

        :print network, ip, IP with prefixlen, netmask, hostmask(反掩码)
        """
        try:
            if type(addresses) is str:
                addresses = addresses.split(',')
            for ip in addresses:
                iface = ipaddress.ip_interface(ip.strip())
                print('{!r}'.format(iface))
                print('            network:', iface.network)
                print('                 ip:', iface.ip)
                print('  IP with prefixlen:', iface.with_prefixlen)
                print('            netmask:', iface.with_netmask)
                print('           hostmask:', iface.with_hostmask)
                print()
        except Exception:
            logging.error("", exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(levelname)s: %(message)s')
    ipTool.network_hosts(['172.11.3.0/24', '172.11.4.0/24'])
    # ipTool.network_hosts('172.11.5.0/24, 172.11.6./24')
    ipTool.network_hosts('172.11.7.0/255.255.255.0')
    # ipTool.is_ip_Valid('172.1.1.')
    ipTool.network_info('172.11.0.0/16, 10.85.1.0/24')
    ipTool.interface_info('172.11.6.1/16, 10.85.11.13/27')
