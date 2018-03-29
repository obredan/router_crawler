#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
from core.http_helper import ErrorTimeout
from core.http_helper import HttpHelper


class PluginLoader(object):
    """Recognize the router type"""
    # attention! DD-WRT must be the first type to match, because if cotains other types' key string
    VENDOR_RES = [
         ('DD-WRT', 'DD\W?WRT'),
         ('TP-LINK', 'TP\W?LINK'), ('TP-LINK', 'TL-'),
         ('D-LINK', 'D\W?LINK'), ('D-LINK', 'DSL'), ('D-LINK', 'DCS'), ('D-LINK', 'DI-\d'),
         ('ASUS', 'RT-'),
         ('Linksys', 'WRT'), ('Linksys', 'Linksys'),
         ('Mecury', 'Wireless N Router MW'),
         ('Tenda', '11N wireless broadband router'), ('Tenda', 'Tenda'), ('Tenda', 'NAT router'),
         ['Surecom', 'Broadband Router'], ('Edimax', 'Default: admin/1234'),
         ('Cisco', 'X2000'),
         ('Netgear', 'Netgear')
    ]

    MODULE_RES = dict()
    MODULE_RES['DD-WRT'] = [
        ['DD\W?WRT', 'dd_wrt']
    ]
    MODULE_RES['TP-LINK'] = [
        ['TL-WR', 'tp_link_wr'],
        ['LINK.+?WR', 'tp_link_wr'],
        ['LINK.+?3G/4G', 'tp_link_wr'],
        ['LINK.+?Gigabit', 'tp_link_vpn_router'],
        ['SOHO', 'tp_link_soho']
    ]
    MODULE_RES['D-LINK'] = [
        ['252', 'd_link_dsl2520'],
        ['dcs', 'd_link_dcs', 'd_link_dcs_2'],
        ['D-LINK SYSTEMS, INC.(.+?)location.href = "login_real.htm"', 'd_link_dir505'],
        ['DI-5', 'd_link_di5'],
        ['DI-6', 'd_link_di6']
    ]
    MODULE_RES['ASUS'] = [
        ['RT', 'asus_rt', 'asus_rt_2']
    ]
    MODULE_RES['Linksys'] = [
        ['E1200', 'linksys_e'],
        ['WRT', 'linksys_wrt']
    ]
    MODULE_RES['Mecury'] = [
        ['Wireless N Router MW', 'mecury_wm']
    ]
    MODULE_RES['Tenda'] = [
        ['NAT router', 'tenda'],
        ['11N wireless broadband router', 'tenda'],
        ['tenda', 'tenda']
    ]
    MODULE_RES['Surecom'] = [
        ['Broadband Router', 'surecom']
    ]
    MODULE_RES['Cisco'] = [
        ['X2000', 'cisco_x2000']
    ]
    MODULE_RES['Netgear'] = [
        ['jwnr2000', 'netgear_jwnr2000', 'netgear_jwnr2000_2'],
        ['Netgear', 'netgear_wnr1']
        # ['WGR', 'netgear_wgr6', 'netgear_wnr1'],
        # ['WNR', 'netgear_wnr1', 'netgear_wgr6']
    ]
    MODULE_RES['Edimax'] = [
        ['Default: admin/1234', 'edimax']
    ]

    server = ''
    realm = ''

    def load_plugin(self, addr, port, session):
        url = 'http://' + addr + ':' + str(port)
        # try to connect routers
        try:
            r = HttpHelper.connect(session, url, 1)
        except Exception:
            raise ErrorTimeout

        if 'server' in r.headers:
            self.server = r.headers['server']
        if 'www-authenticate' in r.headers:
            self.realm = r.headers['www-authenticate']
        fingerprint_str = self.server + self.realm + r.content

        # match vendor
        for vendor_re in self.VENDOR_RES:
            vendor_pattern = re.compile(vendor_re[1], re.I)
            vendor_match = vendor_pattern.search(fingerprint_str)
            if vendor_match:
                # match module
                module_re_list = self.MODULE_RES[vendor_re[0]]
                for module_re in module_re_list:
                    module_pattern = re.compile(module_re[0], re.S | re.I)
                    vendor_match = module_pattern.search(fingerprint_str)
                    if vendor_match:
                        return module_re, self.server, self.realm, vendor_re[0]
                return '', self.server, self.realm, vendor_re[0]
        return '', self.server, self.realm, ''
