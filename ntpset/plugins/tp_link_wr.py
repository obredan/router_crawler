#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import base64
from base_setter import BaseSetter
from base_setter import ErrorTimeout
import requests


class NtpSetter(BaseSetter):
    """NTP auto setter for TP-Link WR serial routers"""
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
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': fail, connect timeout at first connect')
            return

        if r.status_code == requests.codes.unauthorized:
            self.print_with_lock(self.addr + ': fail, wrong password')
            return

        ntp_url = "/userRpm/DateTimeCfgRpm.htm?" \
                  "timezone=1200&month=11&day=5&" \
                  "year=2015&hour=19&minute=34&" \
                  "second=58&ntpB=0.0.0.0&" \
                  "isTimeChanged=0&Save=Save&ntpA="

        ntp_url = index_url + ntp_url + ntp

        if self.debug:
            print 'ntp url: ' + ntp_url

        try:
            self.connect_auth_with_headers(ntp_url, 3)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': time out at setting ntp server')
        else:
            self.print_with_lock(self.addr + ': set ntp server success')


if __name__ == '__main__':
    """Test this unit"""
    test = NtpSetter('61.92.49.90', 80, 'admin', 'admin', requests.session(), True)
    test.ntp_set('0.uk.pool.ntp.org')
