#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import requests
from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout


class Crawler(BaseCrawler):
    """crawler for Netgear JWNR serial routers"""
    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.info_url = '/RST_status.htm'
        self.res['dns1'] = 'var info_get_dns1="(.+?)";'
        self.res['dns2'] = 'var info_get_dns2="(.+?)";'
        self.res['firmware'] = '<TD nowrap>V([\d\._]+?)</TD>'
        self.res['hardware'] = "var product_id='(.+?)';"

        self.headers = {
            b'User-Agent': b'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            b'Accept-Language': b'en-US',
            b'Referer': '',
                        }
        self.url = 'http://' + self.addr + ':' + str(port)

    def get_info(self):
        dns_info = ''
        firmware = ''
        hardware = ''
        r = self.connect_auth_with_headers(self.url, 1)

        if r.status_code == requests.codes.unauthorized:
            raise ErrorPassword

        info_url = self.url + self.info_url
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(info_url, 1)
        except ErrorTimeout:
            pass
        else:
            dns_pattern1 = re.compile(self.res['dns1'], re.I | re.S)
            dns_match1 = dns_pattern1.search(r.content)
            if dns_match1:
                dns_info += dns_match1.group(1) + ' '
            dns_pattern2 = re.compile(self.res['dns2'], re.I | re.S)
            dns_match2 = dns_pattern2.search(r.content)
            if dns_match2:
                dns_info += dns_match2.group(1)

            firmware_pattern = re.compile(self.res['firmware'], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(1)

            hardware_pattern = re.compile(self.res['hardware'], re.I | re.S)
            hardware_match = hardware_pattern.search(r.content)
            if hardware_match:
                hardware = hardware_match.group(1)
        return dns_info, firmware, hardware

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()
