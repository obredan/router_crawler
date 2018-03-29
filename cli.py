#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: 'owen'
import os
import time
import sys
from optparse import OptionParser
from core.thread_pool import WorkManager
from core.cvs_helper import CsvHelper
from crawler.crawler_factory import CrawlerFactory
from dnsset.dnsset_factory import DnsSetFactory
from upgrade.upgrade_factory import UpgradeFactory

default_out_file = time.strftime("%m.%d-%H.%M.%S", time.localtime()) + '.csv'

parser = OptionParser()
# IP address input file
parser.add_option("-i", "--input-file", dest="in_file_path",
                  help="IP address input file path", metavar="FILE")
# result out file
parser.add_option("-o", "--output-file", dest="out_file_path", default=default_out_file,
                  help="scan output file path", metavar="FILE")
# thread number
parser.add_option("-t", "--threads", dest="threads_num", type="int", default=3,
                  help="scan threads num", metavar="NUM")

# crawling mode
parser.add_option("-c", "--crawl",
                  action="store_true", dest="crawl", default=False,
                  help="enable the crawling mode")

# setting dns mode
parser.add_option("-d", "--dns",
                  action="store_true", dest="dns", default=False,
                  help="enable the dns set mode")

# upgrade firmware mpde
parser.add_option("-u", "--upgrade",
                  action="store_true", dest="upgrade", default=False,
                  help="enable the upgrade firmware mode")

# crawler debug mode
parser.add_option("--cdebug",
                  action="store_true", dest="c_debug", default=False,
                  help="enable the crawler debug mode")
# dns set debug mode
parser.add_option("--ddebug",
                  action="store_true", dest="d_debug", default=False,
                  help="enable the dns set debug mode")

# firmware upgrade debubg mode
parser.add_option('--udebug',
                  action='store_true', dest='u_debug', default=False,
                  help='enable the upgrade debug mode')

# combine two cvs output files
parser.add_option('--combine',
                  action='store_true', dest='combine', default=False,
                  help='combine two cvs output files')

(options, args) = parser.parse_args()

crawl_flag = options.crawl
dns_flag = options.dns
upgrade_flag = options.upgrade
c_debug = options.c_debug
d_debug = options.d_debug
u_debug = options.u_debug
data_in_path = options.in_file_path
data_out_path = options.out_file_path
threads_num = options.threads_num

combine_mode = options.combine

if combine_mode:
    csv_helper = CsvHelper()
    if args is None:
        sys.exit(0)
    else:
        csv_helper.combine_file(args)
    print args
    sys.exit(0)

if (crawl_flag or dns_flag or c_debug or d_debug or u_debug or upgrade_flag) is False:
    print 'no mode chosen, program will exit'
    sys.exit(-1)

if c_debug:
    # add the plugins path to sys.path to load plugins
    sys.path.append('crawler/plugins')
    for arg in xrange(4):
        try:
            print args[arg]
        except Exception:
            print 'args should include ip, port, username, password'
            sys.exit(-1)
    test_crawl = CrawlerFactory(addr=args[0], port=int(args[1]),
                                username=args[2], password=args[3], debug=True)
    ret = test_crawl.produce()
    sys.exit(0)

if d_debug:
    # add the plugins path to sys.path to load plugins
    sys.path.append('dnsset/plugins')
    for arg in xrange(7):
        try:
            print args[arg]
        except Exception:
            print 'arg should include ip, port ,username, password, plugin, dns1, dns2'
            sys.exit(-1)
    test_setter = DnsSetFactory(addr=args[0], port=int(args[1]),
                                username=args[2], password=args[3], original_dns=args[6],
                                plugin=args[4], dns=args[5], debug=True)
    ret = test_setter.produce()
    sys.exit(0)

if u_debug:
    # add the plugins path to sys.path to load plugins
    sys.path.append('upgrade/plugins')
    for arg in xrange(6):
        try:
            print args[arg]
        except Exception:
            print 'arg should include ip, port, username, password, plugin, firmware'
            sys.exit(-1)
    if not os.path.exists(args[5]):
        print 'can not find the firmware file, please check the path'
        sys.exit(-1)

    firmware_path = os.path.abspath(args[5])
    test_upgrader = UpgradeFactory(addr=args[0], port=args[1],
                                   username=args[2], password=args[3],
                                   plugin=args[4], firmware=firmware_path, debug=True)
    ret = test_upgrader.produce()
    sys.exit(0)

try:
    file(data_in_path)
except Exception:
    print 'no such ip address file'
    sys.exit(0)

if crawl_flag:
    sys.path.append('./crawler/plugins')
    work_manager = WorkManager(data_in_path, data_out_path, threads_num, 'crawl')
    work_manager.wait_all()
    sys.exit(0)

if dns_flag:
    sys.path.append('./dnsset/plugins')
    try:
        dns = args[0]
    except Exception:
        print 'need dns address to continue'
        sys.exit(-1)
    work_manager = WorkManager(data_in_path, data_out_path, threads_num, 'dns', dns)
    work_manager.wait_all()
    sys.exit(0)

if upgrade_flag:
    sys.path.append('./upgrade/plugins')
    work_manager = WorkManager(data_in_path, data_out_path, threads_num, 'upgrade')
