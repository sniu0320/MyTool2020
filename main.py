# -*- coding: UTF-8 -*-

import os
import sys
import logging
import logging.handlers


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
        pass

    def quit(self):
        print("Thank you for using this tool.")
        sys.exit(0)

if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]%(message)s',)
    Menu().run()