#-*- coding:utf-8 -*-

'''将IMDB中豆瓣存在的电影URL存入单独一张表到时候按表读取数据'''

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
# # client = pymongo.MongoClient('localhost', 27017)
db = client.MovieData

import urllib2
import random

from config_constant import *
from scrapy.selector import Selector
import time
# def subject_search(end_num):
# start_time = time.time()
for i in range(803300,804300):
	proxy = urllib2.ProxyHandler(random.choice(proxy_list))
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	response = urllib2.urlopen('https://movie.douban.com/subject_search?search_text=+tt%07d&cat=1002' % i)
	# response = urllib2.urlopen('https://movie.douban.com/subject_search?search_text=+tt%07d&cat=1002')
	# print u'URL路径:%s' % response.url
	data = response.read()
	info = Selector(text=data).xpath('//div[@class="pl2"]/a/text()')
	if info:
		IMDB_id = dict()
		ttid = 'tt%07d' % i
		print u'tt编号:%s' % ttid
		title = Selector(text=data).xpath('//div[@class="pl2"]/a/text()').extract()[0].strip().split('/')[0].strip()
		print u'电影名称:%s' % title
		movie_url = Selector(text=data).xpath('//div[@class="pl2"]/a/@href').extract()[0].strip()
		print u'电影路径:%s' % movie_url
		IMDB_id['ttid'] = ttid
		IMDB_id['title'] = title
		IMDB_id['movie_url'] = movie_url
		db.IMDB_ID.update({'_id': ttid}, {'$set': IMDB_id}, True)
	# 	print u'豆瓣不存在的电影:%s' % response.url

# print u'用时:%s' % (time.time() - start_time)
# subject_search(3)







