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
        self.info_url = '/Advanced_WAN_Content.asp'
        self.res['dns1'] = 'name="wan_dns1_x" value="(.+?)"'
        self.res['dns2'] = 'name="wan_dns2_x" value="(.+?)"'
        self.res['firmware'] = 'name="firmver" value="(.+?)">'
        self.res['hardware'] = 'RT-\S+'
        self.res['type'] = "wan_route_x = '(.+?)';"

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

        index_content = r.content
        type_pattern = re.compile(self.res['type'], re.I | re.S)
        type_match = type_pattern.search(index_content)

        if not type_match:
            return '', '', ''

        firmware_pattern = re.compile(self.res['firmware'], re.I | re.S)
        firmware_match = firmware_pattern.search(index_content)
        if firmware_match:
            firmware = firmware_match.group(1)

        hardware_pattern = re.compile(self.res['hardware'], re.I | re.S)
        hardware_match = hardware_pattern.search(index_content)
        if hardware_match:
            hardware = hardware_match.group(0)

        if type_match.group(1) == 'IP_Bridged':
            return 'AP', firmware, hardware

        dns_url = self.url + self.info_url
        self.headers['Referer'] = self.url
        try:
            r = self.connect_auth_with_headers(dns_url, 2)
        except ErrorTimeout, e:
            pass
        else:
            dns_pattern1 = re.compile(self.res['dns1'], re.I | re.S)
            dns_match1 = dns_pattern1.search(r.content)
            if dns_match1:
                dns_info = dns_match1.group(1)
            dns_pattern2 = re.compile(self.res['dns2'], re.I | re.S)
            dns_match2 = dns_pattern2.search(r.content)
            if dns_match2:
                dns_info += ',' + dns_match2.group(1)

            if dns_info == '':
                self.res['dns1'] = 'name="wan_dns1_x" value="(.+?)"'
                self.res['dns2'] = 'name="wan_dns2_x" value="(.+?)"'
                dns_pattern1 = re.compile(self.res['dns1'], re.I | re.S)
                dns_match1 = dns_pattern1.search(r.content)
                if dns_match1:
                    dns_info = dns_match1.group(1)
                dns_pattern2 = re.compile(self.res['dns2'], re.I | re.S)
                dns_match2 = dns_pattern2.search(r.content)
                if dns_match2:
                    dns_info += ',' + dns_match2.group(1)

        return dns_info, firmware, hardware

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    crawler = Crawler('192.168.0.1', 80, 'admin', 'admin', req.session, True)
    crawler.get_info()
