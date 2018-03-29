#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import requests
from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout

class Crawler(BaseCrawler):
    """crawler for D-Link DCS serial camera"""
    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.info_url = '/stsdev.htm'
        self.res['dns'] = 'DNS</TD><TD>(.+?)</TD>.+?DNS</TD><TD>(.+?)</TD></TR>'
        self.res['firmware'] = '[\d\.]+ \(.+?\)'
        self.res['hardware'] = 'DCS-\d+'

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
            dns_pattern = re.compile(self.res['dns'], re.I | re.S)
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info = dns_match.group(1) + ', ' + dns_match.group(2)

            firmware_pattern = re.compile(self.res['firmware'], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(0)

            hardware_pattern = re.compile(self.res['hardware'], re.I | re.S)
            hardware_match = hardware_pattern.search(r.content)
            if hardware_match:
                hardware = hardware_match.group(0)

        return dns_info, firmware, hardware

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()
