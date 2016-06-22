#-*- coding:utf-8 -*-

import urllib2

#动漫之家配置信息
dmzj_dict = {

				u'地域：': 'area',
				u'分类：': 'c_type',
				u'状态：': 'status',
				u'最新收录：': 'update_time',
				u'别名：': 'other_name',
		}



#代理
def proxy_request(url):
	request = urllib2.Request(url)
	proxy = urllib2.ProxyHandler(
									{
										'http': 'http://127.0.0.1:8123',
										'https': 'https://127.0.0.1:8123',
									},
								)

	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	return opener.open(request)




def dmzj():

	data= dict()
	#一次性
	data['source'] = str()
	data['name'] = str()
	data['url'] = str()
	data['other_name'] = str()
	data['img_url'] = str()
	data['area'] = str()
	data['author'] = str()
	data['c_type'] = str()
	data['c_fenlei'] = str()
	data['c_ticai'] = str()
	data['introduce'] = str()

	#每月
	data['popular'] = str()
	data['update_time'] = str()
	data['status'] = str()

	data['relate_info'] = list()
	
	#每天
	data['all_theme'] = str()
	data['all_response'] = str()
	data['scrapy_time'] = str()
	data['rss_num'] = str()
	
	return data

