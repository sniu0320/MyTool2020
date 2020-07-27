# -*- coding: UTF-8 -*-

import random
import threading
import autotelnetlib as my
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)
###################################ç###

mng_ipaddr = '192.166.4.10'
# mng_ipaddr = '192.166.26.2'

######################################


######################################


def main():
    for cnt in range(0, 5):
        t = threading.Thread(target=ssh_test, args=())
        t.start()


def ssh_test():
    while 1:
        my.sleep(random.randint(200, 5000))
        try:
            t = my.DUT(mng_ipaddr, username='who',
                       password='who', protocol='ssh')
            t.send('show fan')
            t.close()
        except:
            print('ssh login is failed !!')
            continue


# ================================
main()
