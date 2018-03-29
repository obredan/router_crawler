#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'

import csv
import sys
import time
from module_support import ModuleSupport


class CsvHelper(object):
    def __init__(self):
        pass

    @staticmethod
    def combine_file(file_path_list):
        time_prefix = time.strftime("%m.%d-%H.%M.%S", time.localtime())
        reader_list = []
        for file_path in file_path_list:
            tmp_reader = csv.reader(open(file_path, 'rb'))
            for line in tmp_reader:
                # jump those error rows
                if len(line) < 10:
                    continue
                # select online targets
                if line[2] != 'offline':
                    reader_list.append(line)
        reader_list.sort(key=lambda x: x[0])
        default_out_file = time_prefix + '_combine_out.csv'
        default_dns_file = time_prefix + '_combine_dns.csv'
        default_upgrade_file = time_prefix + '_combine_upgrade.csv'
        file_out = open(default_out_file, 'wb')
        file_dns = open(default_dns_file, 'wb')
        file_upgrade = open(default_upgrade_file, 'wb')
        writer_out = csv.writer(file_out)
        dns_out = csv.writer(file_dns)
        upgrade_out = csv.writer(file_upgrade)
        for line in reader_list:
            if line[2] == 'success':
                dns_method = ModuleSupport.dns_set_method(line[5])
                if dns_method:
                    dns_out.writerow([line[0], line[1], line[6],
                                      line[7], line[10], dns_method])
                upgrade_method, firmware_path = ModuleSupport.upgrade_set_method(line[5], line[8],
                                                                                 line[9])
                if upgrade_method:
                    upgrade_out.writerow([line[0], line[1], line[6],
                                          line[7], upgrade_method, firmware_path])
            writer_out.writerow(line)
        print 'combine file finish'

    @staticmethod
    def ori_combine_file(path_lft, path_rht):
        time_prefix = time.strftime("%m.%d-%H.%M.%S", time.localtime())
        default_out_file = time_prefix + '_combine_out.csv'
        default_dns_file = time_prefix + '_combine_dns.csv'
        default_upgrade_file = time_prefix + '_combine_upgrade.csv'
        file_lft = open(path_lft, 'rb')
        file_rht = open(path_rht, 'rb')
        file_out = open(default_out_file, 'wb')
        file_dns = open(default_dns_file, 'wb')
        file_upgrade = open(default_upgrade_file, 'wb')
        reader_lft = csv.reader(file_lft)
        reader_rht = csv.reader(file_rht)
        writer_out = csv.writer(file_out)
        dns_out = csv.writer(file_dns)
        upgrade_out = csv.writer(file_upgrade)

        list_lft = []
        list_rht = []
        for line in reader_lft:
            list_lft.append(line)
        for line in reader_rht:
            list_rht.append(line)
        list_lft.sort(key=lambda x: x[0])
        list_rht.sort(key=lambda x: x[0])

        for i in xrange(len(list_lft)):
            # print list_lft[i][0], list_rht[i][0]
            if list_lft[i][2] == 'success':
                writer_out.writerow(list_lft[i])
                dns_method = ModuleSupport.dns_set_method(list_lft[i][5])
                if dns_method:
                    dns_out.writerow([list_lft[i][0], list_lft[i][1], list_lft[i][6],
                                      list_lft[i][7], list_lft[i][10], dns_method])
                upgrade_method, firmware_path = ModuleSupport.upgrade_set_method(list_lft[i][5], list_lft[i][8],
                                                                                 list_lft[i][9])
                if upgrade_method:
                    upgrade_out.writerow([list_lft[i][0], list_lft[i][1], list_lft[i][6],
                                          list_lft[i][7], upgrade_method, firmware_path])
                continue
            elif list_rht[i][2] == 'success':
                writer_out.writerow(list_rht[i])
                dns_method = ModuleSupport.dns_set_method(list_rht[i][5])
                if dns_method:
                    dns_out.writerow([list_rht[i][0], list_rht[i][1], list_rht[i][6],
                                      list_rht[i][7], list_rht[i][10], dns_method])
                upgrade_method, firmware_path = ModuleSupport.upgrade_set_method(list_rht[i][5], list_rht[i][8],
                                                                                 list_rht[i][9])
                if upgrade_method:
                    upgrade_out.writerow([list_rht[i][0], list_rht[i][1], list_rht[i][6],
                                          list_rht[i][7], upgrade_method, firmware_path])
                continue
            if list_lft[i][2] == '':
                writer_out.writerow(list_lft[i])
                continue
            elif list_rht[i][2] == '':
                writer_out.writerow(list_rht[i])
                continue
            if list_lft[i][2] == 'unknown type':
                writer_out.writerow(list_lft[i])
                continue
            elif list_rht[i][2] == 'unknown type':
                writer_out.writerow(list_rht[i])
                continue
            else:
                writer_out.writerow(list_lft[i])

        print 'combine file finish'


if __name__ == '__main__':
    csv_helper = CsvHelper()
    csv_helper.combine_file(sys.argv[1], sys.argv[2])
