#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import base64
from base_setter import BaseSetter
from base_setter import ErrorTimeout
import requests


class NtpSetter(BaseSetter):
    """NTP auto setter for ASUS RT routers version 2 (new type)"""

    def __init__(self, addr, port, username, password, session, debug=False):
        BaseSetter.__init__(self, addr, port, username, password, session, debug)
        auth_cookie = base64.b64encode(self.try_username + ':' + self.try_passwd)
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'
        self.headers['Accept-Language'] = 'en-US'
        self.headers['Referer'] = ''
        self.headers['Cookie'] = 'tLargeScreenP=1; subType=pcSub; Authorization=Basic ' + auth_cookie

    def ntp_set(self, ntp):
        index_url = 'http://' + self.addr + ':' + str(self.port)
        self.headers['Referer'] = 'http://' + self.addr + ':' + str(self.port)
        try:
            r = self.connect_auth_with_headers(index_url, 2)
            r = self.connect_auth_with_headers(index_url, 2)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': fail, connect timeout at first connect')
            return

        if r.status_code == requests.codes.unauthorized:
            self.print_with_lock(self.addr + ': fail, wrong password')
            return

        ntp_url = '/start_apply.htm'

        ntp_url = index_url + ntp_url

        ntp_data_1 = 'current_page=Advanced_System_Content.asp&' \
                   'next_page=Advanced_System_Content.asp&' \
                   'modified=0&' \
                   'action_mode=apply&' \
                   'action_script=restart_time&' \
                   'time_zone_select=CST-8&' \
                   'ntp_server0=' + ntp

        ntp_data_2 = 'current_page=Advanced_System_Content.asp&' \
                     'next_page=&' \
                     'sid_list=LANHostConfig%3BGeneral%3B&' \
                     'group_id=&' \
                     'modified=0&' \
                     'action_mode=+Apply+&' \
                     'action_script=&' \
                     'time_zone=UCT12&' \
                     'ntp_server0=' + ntp

        if self.debug:
            print 'ntp url: ' + ntp_url

        try:
            self.post_auth_with_headers(ntp_url, ntp_data_1, 3)
            self.post_auth_with_headers(ntp_url, ntp_data_2, 3)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': time out at setting ntp server')
        else:
            self.print_with_lock(self.addr + ': set ntp server success')


if __name__ == '__main__':
    """Test this unit"""
    # test = NtpSetter('113.255.205.64', 80, 'admin', 'admin', requests.session(), True)
    test = NtpSetter('1.64.136.20', 8080 , 'admin', 'admin', requests.session(), True)
    test.ntp_set('0.uk.pool.ntp.org')
    # test.ntp_set('time.nist.gov')
