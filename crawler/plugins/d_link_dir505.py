#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import base64
import re
from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout


class Crawler(BaseCrawler):
    """crawler for D-Link DIR-505 router"""
    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.res['dns'] = ['<wan_dns>(.+?)</wan_dns>', 1]
        self.res['firmware'] = ['<fw_ver>(.+?)</fw_ver>', 1]
        self.res['hardware'] = ['<hw_ver>(.+?)</hw_ver>', 1]

        self.url = 'http://' + self.addr + ':' + str(self.port)

    def get_info(self):
        dns_info = ''
        firmware = ''
        hardware = ''

        username = base64.b64encode(self.username).replace('=', 'A')
        password = base64.b64encode(self.password).replace('=', 'A')
        data = 'request=login&admin_user_name=' + username + '&admin_user_pwd=' + password + '&user_type=0'
        try:
            url = 'http://' + self.addr + str(self.port) + '/my_cgi.cgi?0.7204311818502432'
            login = self.session.post(url, data=data)
        except Exception:
            raise ErrorTimeout
        if not login.content.find('default'):
            raise ErrorPassword

        data = 'request=load_settings&table_name=wan_info&table_name=fw_ver&table_name=hw_ver'
        try:
            url = 'http://' + self.addr + str(self.port) + '/my_cgi.cgi?0.23814993476113056'
        except Exception, e:
            raise ErrorTimeout
        else:
            r = self.session.post(url, data=data)

            firmware_pattern = re.compile(self.res['firmware'][0])
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(self.res['firmware'][1])

            hardware_pattern = re.compile(self.res['hardware'])
            hardware_match = hardware_pattern.search(r.content)
            if hardware_match:
                hardware = 'DIR 505' + hardware_match.group(self.res['hardware'][1])

            dns_pattern = re.compile(self.res['dns'][0])
            dns_match = dns_pattern.search(r.content)
            if dns_match:
                dns_info = dns_pattern.group(self.res['dns'][1])

            return dns_info, firmware, hardware
