#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import base64
import re
from base_setter import BaseSetter
from core.http_helper import ErrorTimeout
from core.http_helper import HttpHelper


class DnsSetter(BaseSetter):
    """DNS auto setter for TP-Link WR serial routers
       Includes 3 types:
       static ip, dynamic, PPPOE

    """
    def __init__(self, addr, port, username, passwd, session, debug=False):
        BaseSetter.__init__(self, addr, port, username, passwd, session, debug)
        auth_cookie = base64.b64encode(self.username + ':' + self.password)
        self.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
        self.headers['Accept-Language'] = 'en-US',
        self.headers['Referer'] = '',
        self.headers['Cookie'] = 'tLargeScreenP=1; subType=pcSub; Authorization=Basic ' + auth_cookie

        self.wan_type_search = '/userRpm/WanCfgRpm.htm'
        self.dyna_para = '?Save=save&dnsserver=[dns1]&dnsserver2=[dns2]&manual=2&mtu=1500&wantype=0'
        self.dyna_ref = '/userRpm/WanDynamicIpCfgRpm.htm?wan=0'
        self.ppp_para = "?wan=0&lcpMru=1480&ServiceName=&AcName=&EchoReq=0" \
                        "&manual=2&dnsserver=[dns1]&dnsserver2=[dns2]&Save=Save&Advanced=Advanced"
        self.ppp_ref = '/userRpm/PPPoECfgAdvRpm.htm?Advanced=Advanced&wan=0'
        self.static_para = "?wan=0&wantype=1&ip=[ip]&mask=[mask]" \
                           "&gateway=[gateway]&mtu=1500&dnsserver=[dns1]&dnsserver2=[dns2]&Save=save"
        self.static_ref = '/userRpm/WanStaticIpCfgRpm.htm'

    def dns_set(self, dns):
        url = 'http://' + self.addr + ':' + str(self.port) + self.wan_type_search
        self.headers['Referer'] = 'http://' + self.addr + ':' + str(self.port)
        try:
            r = HttpHelper.connect_auth_with_headers(None, url, 3, (self.username, self.password), self.headers)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': fail, connect timeout')
            return

        ref_re = 'location.href="(.+?)"'
        ref_re_index = 1
        ref_pattern = re.compile(ref_re, re.I)
        match = ref_pattern.search(r.content)
        if match:
            wan_url = 'http://' + self.addr + ':' + str(self.port) + match.group(ref_re_index)
        else:
            self.print_with_lock(self.addr + ': fail, can not find the wan_url')
            return

        if wan_url.find('WanDynamic') > 0:
            payload = self.__dyna_payload(dns[0], dns[1])
            dns_url = wan_url + payload
            if self.debug:
                self.print_with_lock(self.addr + ': Wan Dynamic')
        elif wan_url.find('PPPoE') > 0:
            payload = self.__ppp_payload(dns[0], dns[1])
            dns_url = wan_url.replace('PPPoECfgRpm', 'PPPoECfgAdvRpm') + payload
            if self.debug:
                self.print_with_lock(self.addr + ': PPPoE')
        elif wan_url.find('WanStatic') > 0:
            try:
                r = HttpHelper.connect_auth_with_headers(None, 3, (self.username, self.password), self.headers)
                static_ip_info_re = 'var staticIpInf = new Array.+"(.+?)".{2}"(.+?)".{2}"(.+?)".{2}1500,'
                static_ip_info_pattern = re.compile(static_ip_info_re, re.I | re.S)
                static_ip_info_match = static_ip_info_pattern.search(r.content)
                if not static_ip_info_match:
                    raise ErrorTimeout
                else:
                    static_ip = static_ip_info_match.group(1)
                    static_mask = static_ip_info_match.group(2)
                    static_gateway = static_ip_info_match.group(3)
            except ErrorTimeout:
                self.print_with_lock(self.addr + ': timeout, static ip but can not load the info page')
                return

            payload = self.__static_payload(dns[0], dns[1], static_ip, static_mask, static_gateway)
            dns_url = wan_url + payload
            if self.debug:
                self.print_with_lock(self.addr + ': Static IP')
        else:
            self.printLock(self.addr + ': fail, can not find the dns change method in this router')
            return

        if self.debug:
            self.print_with_lock(dns_url)
        try:
            r = HttpHelper.connect_auth_with_headers(None, dns_url, 3, (self.username, self.password), self.headers)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': maybe fail, no response')
        else:
            if r.content.find(dns[0]) > 0:
                self.print_with_lock(self.addr + ': success')
            else:
                self.print_with_lock(self.addr + ': fail, change dns fail')

    def __dyna_payload(self, dns1, dns2):
        self.headers['Referer'] = 'http://' + self.addr + ':' + str(self.port) + self.dyna_ref
        payload = self.dyna_para.replace('[dns1]', dns1)
        payload = payload.replace('[dns2]', dns2)
        return payload

    def __ppp_payload(self, dns1, dns2):
        self.headers['Referer'] = 'http://' + self.addr + ':' + str(self.port) + self.ppp_ref
        payload = self.ppp_para.replace('[dns1]', dns1)
        payload = payload.replace('[dns2]', dns2)
        return payload

    def __static_payload(self, dns1, dns2, ip, mask, gatewaty):
        self.headers['Referer'] = 'http://' + self.addr + ':' + str(self.port) + self.static_ref
        payload = self.static_para.replace('[dns1]', dns1)
        payload = payload.replace('[dns2]', dns2)
        payload = payload.replace('[ip]', ip)
        payload = payload.replace('[mask]', mask)
        payload = payload.replace('[gateway]', gatewaty)
        return payload

if __name__ == '__main__':
    """Test this unit"""
    req = __import__('requests')
    test = DnsSetter('192.168.1.1', 80, 'admin', 'admin', req.session)
