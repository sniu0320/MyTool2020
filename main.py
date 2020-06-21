# -*- coding: UTF-8 -*-

import os
import sys
from moduls.class_TelentClinet import TelnetClient
# from moduls.class_Logger import MyLogger
# logging = MyLogger('root')
import logging.config
logging.config.fileConfig(fname='conf/logging_config.ini')

class Menu:
    '''Display a menu and respond to choices when run'''

    def __init__(self):
        self.choices = {
            "1": self.run_one,
            "6": self.quit,
        }

    def display_menu(self):
        print("""
        Tools Menu(2020):
            轮询工具：
                1.test
            日志处理：
                XX
            运维工具：
                XX
            6.Quit
        """)

    def run(self):
        '''Display the menu and respond to choices'''
        try:
            while True:
                self.display_menu()
                choice = input("Enter an option: ")
                action = self.choices.get(choice)
                if action:
                    action()
                else:
                    print("{} is not a valid choice.".format(choice))
        except KeyboardInterrupt:
            print("\nThank you for using this tool.")
        finally:
            pass

    def run_one(self):
        host = '172.11.3.100'
        command1 = 'show version'
        command2 = 'show board-info'
        telnet_client = TelnetClient()
        print("we are try to telnet to %s" %(host))
        # login to the host, success:return true, fail: return false
        if telnet_client.login_host(host):
            telnet_client.input_command(command1)
            telnet_client.input_command(command2)
            telnet_client.logout()

    def quit(self):
        print("Thank you for using this tool.")
        sys.exit(0)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]%(message)s',)
    Menu().run()