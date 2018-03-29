# router crawler
- - -
A router crawler collection includes information crawler, automatic DNS setting and firmware upgrade.

#### Working with: 
- TP-Link
	- WR serial 
	- VPN 
- DD-WRT
- D-Link 
	- DIR-505
	- DI serial
	- ADSL
	- DCS
- Mecury
	- WM
- Cisco/Linksys
	- E2000
	- X2000
	- WGT
- Surecom
- Netgear
	- JWNR
	- WGR
	- WNR
- Edimax
- Tenda

#### Lib:
- requests

#### To do:
- More types support
	- [ ] ROM-0
	- [x] Netgear DNS
	- [ ] Netgear firmware upgrade plugins
	- [x] TP-Link firmware upgrade plugins

- - -

#### usage：
```bash
$python cli.py -h --help		view help
$python cli.py --combine <file_1> <file_2> combine two crawlling output csv files
$python cli.py --cdebug <ip_address> <port> <username> <password>		test router info crawling func
$python cli.py --ddebug <ip_address> <port> <username> <password><dns1><dns2><router_typep>		test router dns setting func
$python cli.py -c -i <target csv file> [-o <result out file>] -t <thread_num>		crawling targets info
$python cli.py -d -i <target csv file> -t <thread_num> <dns>		set targets dns
$python cli.py -u -i <target csv file> -t <thread_num>		upgrade target routers' firmware
```

the input file for crawling should be csv format like following:
```js
ip, port, username, password
```
the output file format：
```js
ip, port, status, server, www-authentication, plugin, username, password, dns
14.199.15.34, 80, success,Router Webserver, Basic realm="TP-LINK Wireless N Gigabit Router WR1043ND" , TP-LINK:tp_link_wr, admin, admin, 202.120.2.101
```

**Notice:** the last column *plugin* is the router model type detected by type_recognition.py, it will help the dns setting function to find the dns changing methods.


the input file for dns setting format:
```js
ip, port, username, password, plugin
58.152.26.245, 80, admin, admin, dd_wrt
```

- - -

#### Sourcecode structure
```
├── cli.py
├── crawler/
|   ├── plugin/
|   |   ├── base_crawler.py
|   |   ├── tp_link_wr.py
|   ├── crawler_facotry.py
|   ├── plugin_loader.py
├── dnsset/
|   ├── plugin/
|   |	├── base_setter.py
|   |   ├── tp_link_wr.py
|   ├── dnsset_factory.py
|   ├── plugin_loader.py
├── upgrade/
|   ├── plugin/
|   |	├── base_setter.py
|   |   ├── tp_link_wr.py
|   ├── upgrade_factory.py
|   ├── plugin_loader.py
├── core/
|   ├──  thread_pool.py
|   ├── sqlite_helperr.py
|   ├── cvs_helper.py
```

Although most of the plugins look very similar, but the plugin struct is necessary for the following reasons:
- web manage page may change
- authentications are different, including cookies, basic auth, etc
- some routers' crawling methods are very *strange*

When you need **add a crawler/dnsset/upgrade plugin**, just extends the base class(base_crawler.py/base_setter.py/base_upgrade.py). And rewrite the get_info/dns_set/upgrade function.
For each new crawler plugin, you need modify crawler/plugin_loader.py module, add regular expression for new router type to register the plugin.
For DNS set/upgrade, the file needs modification is in core/module_support.py. Some firmware and harware infomation need to be added.

