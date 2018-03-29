#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import threading
import requests
from core.http_helper import ErrorTimeout
from core.http_helper import ErrorPassword
from plugin_loader import PluginLoader


class CrawlerFactory(object):
    """product specific module crawler"""
    printLock = threading.Lock()

    def __init__(self, addr, port, username, password, debug=False):
        self.try_username = username
        self.try_password = password
        self.addr = addr

        self.session = requests.session()
        self.router_info = dict()
        self.router_info['addr'] = addr
        self.router_info['port'] = port
        self.router_info['status'] = ''
        self.router_info['server'] = ''
        self.router_info['realm'] = ''
        self.router_info['username'] = username
        self.router_info['password'] = password
        self.router_info['firmware'] = ''
        self.router_info['hardware'] = ''
        self.router_info['dns'] = ''
        self.router_info['module'] = ''

        self.debug = debug

    def print_with_lock(self, str):
        self.printLock.acquire()
        print str
        self.printLock.release()

    def produce(self):
        plugin_loader = PluginLoader()
        try:
            router_module, server, realm, vendor = plugin_loader.load_plugin(self.router_info['addr'],
                                                                             self.router_info['port'], self.session)
        except ErrorTimeout, e:
            self.print_with_lock(self.addr + ': fail, connect timeout at module identification')
            self.router_info['status'] = 'offline'
            return self.router_info
        else:
            if server:
                self.router_info['server'] = server
            if realm:
                self.router_info['realm'] = realm

        if self.debug:
            self.print_with_lock("router module:")
            self.print_with_lock(router_module)

        if not router_module:
            self.print_with_lock(self.addr + ': fail, unknown module')
            self.router_info['status'] = 'unknown module'
            self.router_info['module'] = 'unknown'
            # crawler_module = __import__('unknown_module')
            # crawler = crawler_module.Crawler(self.router_info['addr'], self.router_info['port'],
            #                                  self.try_username, self.try_password, self.session, self.debug)
            if self.debug:
                self.print_with_lock(self.router_info)
            return self.router_info
        for crawler_name in router_module[1:]:
            if self.debug:
                self.print_with_lock(self.addr + ': try ' + crawler_name)
            crawler_module = __import__(crawler_name)
            crawler = crawler_module.Crawler(self.router_info['addr'], self.router_info['port'],
                                             self.try_username, self.try_password, self.session, self.debug)
            try:
                dns_info, firmware, hardware = crawler.get_info()
            # password error
            except ErrorPassword:
                self.print_with_lock(self.addr + ': fail, wrong password')
                self.router_info['status'] = 'wrong password'
                return self.router_info

            # connection timeout
            except ErrorTimeout:
                self.print_with_lock(self.addr + ': fail, connect timeout at get info')
                self.router_info['status'] = 'incomplete'
                return self.router_info
            else:
                if dns_info or firmware or hardware:
                    self.print_with_lock(self.addr + ': success')
                    self.router_info['status'] = 'success'
                    self.router_info['module'] = vendor + ':' + crawler_name
                    self.router_info['dns'] = dns_info
                    self.router_info['firmware'] = firmware
                    self.router_info['hardware'] = hardware
                    if self.debug:
                        print 'router info:\n', self.router_info
                        print '\n\n'
                    return self.router_info

        self.router_info['module'] = vendor + ':' + crawler_name
        if self.debug:
            print 'find nothing'
            print self.router_info
        return self.router_info


if __name__ == '__main__':
    crawler_factory = CrawlerFactory('192.168.0.1', 80, 'admin', 'admin', True)
    crawler_factory.produce()
