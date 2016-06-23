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

dmzj_dict2 = {
				'c_fenlei': u'类型：',
				'c_type': u'类别：',
				'status': u'状态：',
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
	#名称
	data['name'] = str()
	#链接
	data['url'] = str()
	#别名
	data['other_name'] = str()
	#图片
	data['img_url'] = str()
	#地区
	data['area'] = str()
	#作者
	data['author'] = str()
	#分类
	data['c_type'] = str()
	#类型
	data['c_fenlei'] = str()
	#题材
	data['c_ticai'] = str()
	#简介
	data['introduce'] = str()

	#每月
	#人气
	data['popular'] = str()
	#最近更新
	data['update_time'] = str()
	#状态
	data['status'] = str()
	#相关信息
	data['relate_info'] = list()
	
	#每天
	#所有主题
	data['all_theme'] = str()
	#所有回复
	data['all_response'] = str()
	#抓取时间
	data['scrapy_time'] = str()
	#订阅数
	data['rss_num'] = str()
	
	return data

