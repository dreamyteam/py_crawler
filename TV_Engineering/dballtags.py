#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from configfile import *
import threading
import urllib2
import bson
from scrapy.selector import Selector
import time
import re
import random

data = db.AllTags.find_one()

#取所有标签获取豆瓣大部分库存电影
class DoubanTags(threading.Thread):

	def __init__(self, tag_name):

		threading.Thread.__init__(self)

		self.tag_name = tag_name

	def run(self):

		print u'标签名:%s' % self.tag_name
		self.parse(self.tag_name, 0)

	@staticmethod
	def run_threads():

		threads = list()
		for i in data['tag_list'][100:200]:

			thread_1 = DoubanTags(i)
			thread_1.start()
			threads.append(thread_1)

		for t in threads:
			t.join()
			
	def parse(self, tag_name, page):

		url = 'https://movie.douban.com/tag/{0}?start={1}&type=T'.format(tag_name.encode('utf-8'), page)
		is_which = random.choice(request_list)
		if is_which == 'proxy':
			response = proxy_request(url)
		else:
			response = urllib2.urlopen(url)
		# response = proxy_request(url)
		print u'标签URL:%s' % response.url
		sel = Selector(text=response.read())
		all_info = sel.xpath('//*[@class="article"]//*[@width="100%"]')

		if all_info[1:]:
			for i in all_info[1:]:
				movie_name = i.xpath('.//*[@class="pl2"]/a/text()').extract()[0].strip().split('/')[0].strip()
				movie_url = i.xpath('.//*[@class="pl2"]/a/@href').extract()[0].strip()
				movie_id = movie_url.split('/')[-2].strip()
				scrapy_time = time.strftime('%Y-%m-%d %H:%M:%S')
				print movie_name
				print movie_url
				print movie_id
				
				insert_dict = {
								'tag': tag_name,
								'title': movie_name,
								'url': movie_url,
								'id': movie_id,
								'scrapy_time': scrapy_time,
								'source': 'douban',
							}
		
				db.DoubanTagID.update({'url': movie_url}, {'$set': insert_dict}, True)

			is_next = sel.xpath('//*[@rel="next"]')
			page += 20
			return self.parse(tag_name, page)

DoubanTags.run_threads()































