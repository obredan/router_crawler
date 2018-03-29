#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'
import threading
import requests
import re


class DnsSetFactory(object):
    """produce sepcifical type dns setter"""
    printLock = threading.Lock()

    def print_with_lock(self, str):
        self.printLock.acquire()
        print str
        self.printLock.release()

    def __init__(self, addr, port, username, password, original_dns, plugin, dns, debug=False):
        self.username = username
        self.password = password
        self.session = requests.session()

        self.addr = addr
        self.port = port
        self.plugin = plugin
        self.original_dns = original_dns
        self.dns = dns
        self.debug = debug

    def produce(self):
        dns_1st_re = '\d+\.\d+\.\d+\.\d+'
        original_dns_match = re.compile(dns_1st_re).search(self.original_dns)
        # match router's original 1st dns, and remain it as the 2rd dns
        if original_dns_match:
            self.original_dns = original_dns_match.group(0)
        else:
            self.print_with_lock(self.addr + ': fail, find no original dns')
            return
        dns = [self.dns, self.original_dns]
        try:
            dns_set_module = __import__(self.plugin)
        except ImportError:
            print 'no plugin nameed ' + self.plugin
            return
        setter = dns_set_module.DnsSetter(self.addr, self.port, self.username, self.password, self.session,
                                          self.debug)
        setter.dns_set(dns)


if __name__ == '__main__':
    """Test DNS setter factory"""
    test = DnsSetFactory('192.168.1.1', 80, 'admin', 'admin', 'tp_link_wr', ['202.120.2.101', '202.121.2.101'])
    test.produce()
