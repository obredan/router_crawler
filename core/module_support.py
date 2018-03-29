#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import re
import os


class ModuleSupport(object):
    """
    Check if router is available for auto upgrade firmware
    or setting DNS
    """

    UPGRADED_SUPPORT_TYPES = dict()
    # UPGRADE_SUPPORT_TYPE sample
    # [('scan_plugin_name', 'firmware_version', 'hardware_version', 'upgrade_plugin_name', 'firmware_file_path')]

    UPGRADED_SUPPORT_TYPES['TP-LINK'] = []
    # TL-WR740N_v1v2_100910_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '100910', 'WR740N.+?(v1|v2)', 'tp_link_wr',
                                              '/firmware/TL-WR740N_v1v2_100910_en/wr740nv1_100910-ok-en.bin'))
    # TL-WR740N_V4_130520_TW
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130520', 'WR740N.+?v4', 'tp_link_wr',
                                              '/firmware/TL-WR740N_V4_130520_TW/wr740nv4-130520-tw-ok.bin'))
    # TL-WR841N_V8_130506
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130506', 'WR841N.+?V8', 'tp_link_wr',
                                              '/firmware/TL-WR841N_V8_130506_en/841nv8-130506-en-notify.bin'))
    # TL-WR842ND_V1_130110_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130110', 'WR842.+?v1', 'tp_link_wr',
                                              '/firmware/TL-WR842ND_V1_130110_en/wr842ndv1_130110-en-ok.bin'))
    # TL-WR842ND_V2_130628_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130628', 'WR842ND.+?v2', 'tp_link_wr',
                                              '/firmware/TL-WR842ND_V2_130628_en/wr842ndv2_130628-en-ok.bin'))
    # TL-WR941ND_V5_130709_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130709', 'WR941ND.+?v5', 'tp_link_wr',
                                              '/firmware/TL-WR941ND_V5_130709_en/wr941ndv5_130709-en-ok.bin'))
    # TL-WR941ND_V5_140627_en-check
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '140627', 'WR941ND.+?v5', 'tp_link_wr',
                                              '/firmware/TL-WR941ND_V5_140627_en-check/wr941ndv5-160627-en-ok.bin'))
    # TL-WR1043ND_V2_130925_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '130925', 'WR1043ND.+?v2', 'tp_link_wr',
                                              '/firmware/TL-WR1043ND_V2_130925_en/wr1043v2_130925-en-ok.bin'))
    # TL-WR1043ND_V2_140613_en
    UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '140613', 'WR1043ND.+?v2', 'tp_link_wr',
                                              '/firmware/TL-WR1043ND_V2_140613_en/wr1043v2-140613-en-ok.bin'))

    # only for TEST!!!
    # wr841nv7_en_3_12_9_up(120221)
    # UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '120201', 'WR841.+?(v6|v7)', 'tp_link_wr',
    #                                           '/firmware/Test_841N/wr841nv7_en_3_12_9_up(120221).bin'))
    # UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '120221', 'WR841.+?(v6|v7)', 'tp_link_wr',
    #                                           '/firmware/Test_841N/wr841nv7_en_3_13_9_up(120201).bin'))
    # UPGRADED_SUPPORT_TYPES['TP-LINK'].append(('tp_link_wr', '120221', 'WR941.+?(v5|v6)', 'tp_link_wr',
    #                                           '/firmware/Test_941N/wr941nv4_v5.bin'))

    # DNSSET_SUPPORT_TYPE sample
    # ['scan_plugin_name', 'dnsset_plugin_name']
    DNSSET_SUPPORT_TYPES = dict()
    # TODO: more plugin pair
    DNSSET_SUPPORT_TYPES['TP-LINK'] = [
        ('tp_link_wr', 'tp_link_wr')
    ]

    def __init__(self):
        pass

    @classmethod
    def dns_set_method(cls, router_plugin_info):
        """
        using router_plugin_info return by crawler to determine dns set plugin name
        :param router_plugin_info: plugin name crawler using for scanning, read from csv file
        :return: router dns set plugin name
        """
        if router_plugin_info.find(':') > 0:
            vendor = router_plugin_info.split(':')[0]
            scan_plugin = router_plugin_info.split(':')[1]
            if vendor in cls.DNSSET_SUPPORT_TYPES:
                support_list = cls.DNSSET_SUPPORT_TYPES[vendor]
                for support_tuple in support_list:
                    if support_tuple[0] == scan_plugin:
                        # return router dns set method
                        return support_tuple[1]
        return None

    @classmethod
    def upgrade_set_method(cls, router_plugin_info, firmware_version, hardware_version):
        """
        same as dns_set_method, but return upgrade plugin name
        :param router_plugin_info: same param in dns_set_method
        :param firmware_version: router firmware version
        :param hardware_version: router hardware version
        :return:
        """
        # router_plugin_info sample
        # TP-Link:tp_link_wr
        if router_plugin_info.find(':') > 0:
            # fetch the vendor
            vendor = router_plugin_info.split(':')[0]
            # fetch the scanning plugin name
            scan_plugin = router_plugin_info.split(':')[1]
            if vendor in cls.UPGRADED_SUPPORT_TYPES:
                # fetch all vendor's upgrade plugins' name
                support_list = cls.UPGRADED_SUPPORT_TYPES[vendor]
                for support_tuple in support_list:
                    if support_tuple[0] == scan_plugin and cls.version_check(firmware_version, hardware_version,
                                                                             support_tuple[1], support_tuple[2]):
                        # return router upgrade method and firmware path
                        # os.getcwd() get the workspace dir
                        return support_tuple[3], os.getcwd() + support_tuple[4]
        return None, None

    @staticmethod
    def version_check(firmware_version, hardware_version, support_firmware_version, support_hardware_version):
        s_f_v_pattern = re.compile(support_firmware_version, re.I)
        s_f_v_match = s_f_v_pattern.search(firmware_version)
        s_h_v_pattern = re.compile(support_hardware_version, re.I)
        s_h_v_match = s_h_v_pattern.search(hardware_version)

        if s_f_v_match and s_h_v_match:
            return True
        else:
            return False
