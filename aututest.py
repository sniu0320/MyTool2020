# -*- coding: UTF-8 -*-

from core.autotest import autotest

t = autotest.DUT(host='172.11.1.1')
if t.login('ssh'):
    pass
