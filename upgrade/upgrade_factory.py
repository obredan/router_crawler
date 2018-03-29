#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import requests


class UpgradeFactory(object):
    """produce specific type firmware upgrade plugins"""
    def __init__(self, addr, port, username, password, plugin, firmware, debug=False):
        self.username = username
        self.password = password
        self.session = requests.session()

        self.addr = addr
        self.port = port
        self.type = plugin
        self.firmware = firmware
        self.debug = debug

    def produce(self):
        upgrade_module = __import__(self.type)
        upgrader = upgrade_module.Upgrader(self.addr, self.port, self.username,
                                           self.password, self.session, self.firmware, self.debug)
        upgrader.upgrade()


