# -*- coding: UTF-8 -*-

from core.autotest import autotest
import time

t = autotest.DUT(host='47.105.177.235', username='root', password='tt')
if t.login('ssh'):
    t.rec('dir')
    time.sleep(3)
    t.rec('cd GateOne-master')
    time.sleep(3)
    t.rec('ls')
