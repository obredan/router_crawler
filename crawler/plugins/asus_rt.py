#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import requests
from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout


class Crawler(BaseCrawler):
    """crawler for ASUS RT serial routers"""
    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.info_url = '/tcpipwan.asp'
        self.hardware_url = '/lang.js'
        self.firmware_url = '/state.js'
        self.res['dns1'] = 'name="dns1" class="input" size="18" maxlength="15" value=(.*?)>'
        self.res['dns2'] = 'name="dns2" class="input" size="18" maxlength="15" value=(.*?)>'
        self.res['firmware'] = 'showtext\(\$\("firmver"\), "([\d\.]+?)"\);'
        self.res['hardware'] = 'Web_Title="(.+?)"'

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
        r = self.connect_auth_with_headers(self.url, 2)

        if r.status_code == requests.codes.unauthorized:
            raise ErrorPassword

        url = self.url + self.info_url
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(url, 2)
        except ErrorTimeout, e:
            pass
        else:
            dns_pattern = re.compile(self.res['dns1'], re.I | re.S)
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info += dns_match.group(1) + ', '

            dns_pattern = re.compile(self.res['dns2'], re.I | re.S)
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info += dns_match.group(1)

        url = self.url + self.hardware_url
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(url, 2)
        except ErrorTimeout, e:
            pass
        else:
            hardware_pattern = re.compile(self.res['hardware'], re.I | re.S)
            hardware_match = hardware_pattern.search(r.content)
            if hardware_match:
                hardware = hardware_match.group(1)

        url = self.url + self.firmware_url
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(url, 2)
        except ErrorTimeout, e:
            pass
        else:
            firmware_pattern = re.compile(self.res['firmware'], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(1)

        return dns_info, firmware, hardware

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()
