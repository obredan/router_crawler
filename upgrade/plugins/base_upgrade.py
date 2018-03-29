#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import threading


class BaseUpgrader(object):
    """Automatic update router's firmware"""
    printLock = threading.Lock()

    def __init__(self, addr, port, username, passwd, session, firmware, debug=False):
        self.addr = addr
        self.port = port
        self.username = username
        self.password = passwd
        self.session = session
        self.firmware = firmware
        self.headers = dict()
        self.debug = debug

    def print_with_lock(self, str):
        self.printLock.acquire()
        print str
        self.printLock.release()

    def upgrade(self):
        pass
