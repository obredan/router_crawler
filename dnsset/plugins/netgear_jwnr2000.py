#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import requests
from base_setter import BaseSetter
from core.http_helper import ErrorTimeout
from core.http_helper import HttpHelper


class DnsSetter(BaseSetter):
    """DNS auto setter for Netgear JWNR2000 serial routers"""

    def __init__(self, addr, port, username, password, session, debug):
        BaseSetter.__init__(self, addr, port, username, password, session, debug)

        self.headers = {
            b'User-Agent': b'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            b'Accept-Language': b'en-US',
            b'Referer': '',
        }
        self.base_url = 'http://' + self.addr + ':' + str(port)

    def get_now_info(self, internet_type):

        bas_ref = self.base_url + '/BAS_basic.htm'
        self.headers[b'Referer'] = bas_ref
        dyna_bas_url = self.base_url + '/BAS_ether.htm'
        pppoe_bas_url = self.base_url + ''
        static_bas_url = self.base_url + ''
        if internet_type == 'static':
            jump_url = static_bas_url
        elif internet_type == pppoe_bas_url:
            jump_url = ''
        else:
            jump_url = dyna_bas_url
        r = HttpHelper.connect_auth_with_headers(None, jump_url, 3, (self.username, self.password),
                                                 self.headers)
        return r.content

    def connect_type_rec(self):
        jump_url = self.base_url + '/BAS_basic.htm'
        r = HttpHelper.connect_auth_with_headers(None, jump_url, 3, (self.username, self.password),
                                                 self.headers)
        type_re = 'select_basic="(.)"'
        type_ret = re.compile(type_re, re.I).search(r.content)
        if type_ret == '1':
            return 'dyna'
        elif type_ret == '0':
            return 'pppoe'
        else:
            return 'static'

    def __pppoe_payload(self, content, dns):
        pppoe_payload = dict()
        pppoe_payload['head'] = "submit_flag=pppoe&" \
                                "conflict_wanlan=&" \
                                "change_wan_type=1&" \
                                "run_test=no&" \
                                "Apply=Apply&" \
                                "login_type=Other&" \
                                "timestamp=82977&" \
                                "DNSAssign=1"
        pppoe_payload['pppoe_ipaddr'] = '&pppoe_ipaddr='
        pppoe_payload['pppoe_subnet'] = '&pppoe_subnet='
        pppoe_payload['pppoe_dnsaddr1'] = '&pppoe_dnsaddr1='
        pppoe_payload['pppoe_dnsaddr2'] = '&pppoe_dnsaddr2='
        pppoe_payload['hidden_pppoe_idle_time'] = '&hidden_pppoe_idle_time=0'
        pppoe_payload['pppoe_username'] = '&pppoe_username='
        pppoe_payload['pppoe_passwd'] = '&pppoe_passwd='
        pppoe_payload['pppoe_servername'] = '&pppoe_servername='
        pppoe_payload['pppoe_dod'] = '&pppoe_dod=1'
        pppoe_payload['pppoe_idletime'] = '&pppoe_idletime=0'
        pppoe_payload['wan_assign'] = '&WANAssign='
        pppoe_payload['mac_assign'] = '&MACAssign='
        pppoe_payload['spoof_mac'] = '&Spoofmac='

        pppoe_re = dict()
        pppoe_match = dict()
        pppoe_re['wan_assign'] = "var pppoe_get_wan_assign='(.)'"
        pppoe_re['mac_assign'] = "pppoe_get_mac_assign='(.)'"
        pppoe_re['lan_ip'] = 'var lan_ip="(.+?)"'
        pppoe_re['lan_subnet'] = 'var lan_subnet="(.+?)"'
        pppoe_re['spoof_mac'] = 'var pppoe_get_this_mac="(.+?)"'
        pppoe_re['pppoe_dnsaddr1'] = 'var pppoe_get_dns1="(.+?)"'
        pppoe_re['pppoe_dnsaddr2'] = 'var pppoe_get_dns1="(.+?)"'
        pppoe_re['dod'] = "form.pppoe_dod.value = '(.)'"
        # pppoe_re['idlt_timeout'] = 'name="pppoe_idletime" maxLength="5" size="16" value="(.+?)"'
        pppoe_re['pppoe_username'] = 'form.pppoe_username.value="(.+?)"'
        pppoe_re['pppoe_passwd'] = 'form.pppoe_passwd.value="(.+?)"'
        pppoe_re['pppoe_servername'] = 'form.pppoe_servername.value="(.+?)"'

        for key, val in pppoe_re.iteritems():
            pppoe_match[key] = re.compile(val, re.I).search(content)

        if pppoe_match['wan_assign'] == '0':
            pppoe_payload['wan_assign'] += 'Dynamic'
        else:
            pppoe_payload['wan_assign'] += 'Fixed'

        if pppoe_match['mac_assign'] == '0':
            pppoe_payload['mac_assign'] += '0'
        else:
            pppoe_payload['mac_assign'] += '2' + pppoe_payload['spoof_mac'] + pppoe_match['spoof_mac'].replace('.',
                                                                                                               '%3A')
        pppoe_payload['pppoe_ipaddr'] += pppoe_match['lan_ip']
        pppoe_payload['pppoe_subnet'] += pppoe_match['lan_subnet']
        pppoe_payload['pppoe_dnsaddr1'] += dns[0]
        pppoe_payload['pppoe_dnsaddr2'] += dns[1]
        pppoe_payload['pppoe_username'] += pppoe_match['pppoe_username']
        pppoe_payload['pppoe_passwd'] += pppoe_match['pppoe_passwd']
        pppoe_payload['pppoe_servername'] += pppoe_match['pppoe_servername']

        return pppoe_payload['head'] + pppoe_payload['pppoe_ipaddr'] + pppoe_payload['pppoe_subnet'] + \
               pppoe_payload['pppoe_dnsaddr1'] + pppoe_payload['pppoe_dnsaddr2'] + pppoe_payload[
                   'hidden_pppoe_idle_time'] + \
               pppoe_payload['pppoe_username'] + pppoe_payload['pppoe_passwd'] + pppoe_payload['pppoe_servername'] + \
               pppoe_payload['wan_assign'] + pppoe_payload['mac_assign']

    def __dyna_payload(self, content, dns):
        dyna_payload = dict()
        dyna_payload['head'] = "submit_flag=ether&" \
                               "conflict_wanlan=&" \
                               "change_wan_type=1&" \
                               "run_test=no&" \
                               "domain_name=&" \
                               "WANAssign=dhcp&" \
                               "DNSAssign=1" \
                               "flush_flag=0&" \
                               "Apply=Apply&" \
                               "timestamp=82775&" \
                               "loginreq=dhcp"
        dyna_payload['sys_name'] = '&system_name='
        dyna_payload['ether_ip'] = "&ether_ipaddr="
        dyna_payload['ether_subnet'] = '&ether_subnet='
        dyna_payload['ether_gateway'] = '&ether_gateway='
        dyna_payload['ether_dnsaddr1'] = '&ether_dnsaddr1='
        dyna_payload['ether_dnsaddr2'] = '&ether_dnsaddr2='
        dyna_payload['mtu'] = '&hid_mtu_value='
        dyna_payload['mac_assign'] = '&MACAssign='
        dyna_payload['spoof_mac'] = '&Spoofmac='

        dyna_re = dict()
        dyna_match = dict()
        # dyna_re['ether_dnsaddr1'] = 'ether_get_dns1="(.+?)"'
        # dyna_re['ether_dnsaddr2'] = 'ether_get_dns2="(.+?)"'
        dyna_re['ether_ip'] = 'var old_wan_ip="(.+?)"'
        dyna_re['ether_subnet'] = 'ether_get_subnet="(.+?)"'
        dyna_re['ether_gateway'] = 'ether_get_gateway="(.+?)"'
        dyna_re['sys_name'] = 'name="system_name" size="20" maxlength="60" value="(.+?)"'
        dyna_re['mtu'] = "var wan_mtu_now='(.+?)'"

        dyna_re['spoof_mac'] = 'var ether_get_this_mac="(.+?)"'
        dyna_re['mac_assign'] = "var ether_get_mac_assign='(.+?)'"

        for key, val in dyna_re.iteritems():
            item_pattern = re.compile(val, re.I)
            dyna_match[key] = item_pattern.search(content).group(1)
            dyna_payload[key] += dyna_match[key]

        dyna_payload['ether_dnsaddr1'] += dns[0]
        dyna_payload['ether_dnsaddr2'] += dns[1]

        if dyna_match['mac_assign'] == '2':
            dyna_payload['spoof_mac'] = dyna_payload['spoof_mac'].replace(':', '%3A')
            return dyna_payload['head'] + dyna_payload['sys_name'] + dyna_payload['ether_ip'] + \
                   dyna_payload['ether_subnet'] + dyna_payload['ether_gateway'] + dyna_payload['ether_dnsaddr1'] + \
                   dyna_payload['ether_dnsaddr2'] + dyna_payload['mtu'] + dyna_payload['mac_assign'] + dyna_payload[
                       'spoof_mac']
        else:
            return dyna_payload['head'] + dyna_payload['sys_name'] + dyna_payload['ether_ip'] + \
                   dyna_payload['ether_subnet'] + dyna_payload['ether_gateway'] + dyna_payload['ether_dnsaddr1'] + \
                   dyna_payload['ether_dnsaddr2'] + dyna_payload['mtu'] + dyna_payload['mac_assign'] + dyna_payload[
                       'spoof_mac']

    def __generate_payload(self, content, dns, type):
        if type == 'pppoe':
            return self.__pppoe_payload(content, dns)
        elif type == 'dyna':
            return self.__dyna_payload(content, dns)

    def dns_set(self, dns):
        try:
            self.headers[b'Referer'] = self.base_url
            self.connect_auth_with_headers(self.base_url, 2)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': connect timout at first try')
            return

        try:
            type = self.connect_type_rec()
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': connect timmeout at type recognition')
            return
        if self.debug:
            self.print_with_lock(self.addr + ': type ' + type)

        try:
            content = self.get_now_info(type)
        except ErrorTimeout:
            self.print_with_lock(self.addr + 'connect timeout at get info')
            return
        post_url_re = '<FORM method="POST" action="(.+?)"'
        post_url = self.base_url + re.compile(post_url_re, re.I).search(content).group(1).replace(' ', '%20')
        payload = self.__generate_payload(content, dns, type)
        if self.debug:
            self.print_with_lock('payload: ' + payload)
            self.print_with_lock('url: ' + post_url)

        try:
            r = HttpHelper.post_auth_with_headers(None, post_url, 3, (self.username, self.password), self.headers,
                                                  payload)
        except ErrorTimeout:
            self.print_with_lock(self.addr + ': connect timeout at post')
            return

        self.print_with_lock(self.addr + ': success')


if __name__ == '__main__':
    """Test this unit"""
    s = requests.session()
    crawler = DnsSetter('192.168.33.1', 80, 'admin', 'password', s, True)
    crawler.dns_set(['8.8.8.8', '5.5.5.5'])
