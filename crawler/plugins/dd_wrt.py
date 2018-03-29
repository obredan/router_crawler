#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re

from base_crawler import BaseCrawler
from core.http_helper import ErrorPassword
from core.http_helper import ErrorTimeout


class Crawler(BaseCrawler):
    """crawler for DD-WRT routers"""
    def __init__(self, addr, port, username, password, session, debug):
        BaseCrawler.__init__(self, addr, port, username, password, session, debug)
        self.res['dns'] = ['/userRpm/StatusRpm.htm', 'var wanPara = new Array(.+?)"([\d\.]+? , [\d\.]+?)"', 2]
        self.res['firmware'] = ['', 'openAboutWindow.+?>(.+?)</a>"', 1]
        self.res['hardware'] = ['', '>Capture\(status_router.sys_model.+?\n(.+?)&nbsp;', 1]

    def get_info(self):
        dns_info = ''
        firmware = ''
        hardware = ''

        dns_url = 'http://' + self.addr + ':' + str(self.port) + self.res['dns'][0]
        
        firmware_url = 'http://' + self.addr + ':' + str(self.port) + self.res['firmware'][0]
        if firmware_url == dns_url:
            firmware_pattern = re.compile(self.res['firmware'][1], re.I | re.S)
            firmware_match = firmware_pattern.search(r.content)
            if firmware_match:
                firmware = firmware_match.group(self.res['firmware'][2])
        else:
            try:
                r = self.connect(firmware_url, 1)
            except ErrorTimeout, e:
                pass
            else:
                firmware_pattern = re.compile(self.res['firmware'][1], re.I | re.S)
                firmware_match = firmware_pattern.search(r.content)
                if firmware_match:
                    firmware = firmware_match.group(self.res['firmware'][2])

                hardware_pattern = re.compile(self.res['hardware'][1], re.I | re.S)
                hardware_match = hardware_pattern.search(r.content)
                if hardware_match:
                    hardware = hardware_match.group(self.res['hardware'][2])
        return dns_info, firmware, hardware
