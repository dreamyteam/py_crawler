#-*- coding:utf-8 -*-


'''增量抓取脚本'''

import urllib2
from scrapy.selector import Selector
import pymongo 
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.CartoonData
import time

def acqq():

	#抓取前面10页
	for i in range(1, 11):
		res = urllib2.urlopen('http://ac.qq.com/Comic/all/search/time/page/{0}'.format(i,))
		sel = Selector(text=res.read())
		item = dict()
		for i in sel.xpath('//*[@class="ret-search-list clearfix"]/li'):
			item['source'] = 'acqq'
			item['title'] = i.xpath('./div[2]/h3/a/text()').extract()[0].strip()
			item['url'] = i.xpath('./div[2]/h3/a/@href').extract()[0].strip()
			item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

acqq()













