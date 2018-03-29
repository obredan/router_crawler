#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import threading


class BaseSetter(object):
    """Automatic change routers' dns settings"""
    printLock = threading.Lock()

    def __init__(self, addr, port, username, passwd, session, debug=False):
        self.addr = addr
        self.port = port
        self.username = username
        self.password = passwd
        self.session = session
        self.headers = dict()
        self.debug = debug

    def print_with_lock(self, str):
        self.printLock.acquire()
        print str
        self.printLock.release()

    def dns_set(self, dns):
        pass
