#-*- coding:utf-8 -*- 


import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData
from config_constant import *
get_info = db.PeopleData.find({'source': 'douban'})

import urllib2
from scrapy.selector import Selector
def proxy_request(url):
	request = urllib2.Request(url)
	proxy = urllib2.ProxyHandler(
									{
										'http': 'http://127.0.0.1:8123',
										'https': 'https://127.0.0.1:8123',
									}
								)
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	return opener.open(request).read()


def imdb_human_info(imdb_dict, releate_id):

	data = (urllib2.urlopen(imdb_dict['url']).read())
	get_dict = human_info_format()
	get_dict['human_url'] = imdb_dict['url']
	sel = Selector(text=data)
	print u'imdb路径:%s' % get_dict['human_url']
	get_dict['en_name'] = sel.xpath('//*[@id="overview-top"]//*[@itemprop="name"]/text()').extract()[0].strip()
	print u'英文名:%s' % get_dict['en_name']
	get_dict['Releate_ID'] = releate_id
	print u'和豆瓣关联的ID:%s' % get_dict['Releate_ID']
	get_dict['source'] = 'IMDB'
	print u'来源:%s' % get_dict['source']
	db.PeopleData.update({'human_url': get_dict['human_url']}, {'$set': get_dict}, True)
	


# imdb_human_info({'url': 'http://www.imdb.com/name/nm0000553/'})

for i in get_info:
	if i['IMDB_ID']:
		imdb_human_info(i['IMDB_ID'], i['Releate_ID'])
		print '----------' * 5
# 		break









