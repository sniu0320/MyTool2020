
import logging
from moduls.class_TelentClinet import TelnetClient

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[%(funcName)s line:%(lineno)d] - %(levelname)s: %(message)s')

host = '172.11.3.100'
command1 = 'show version'
command2 = 'show board-info'
telnet_client = TelnetClient()
print("we are try to telnet to %s" %(host))
# login to the host, success:return true, fail: return false
if telnet_client.login_host(host):
    telnet_client.input_command('command1')
    telnet_client.input_command('command2')
    telnet_client.logout()