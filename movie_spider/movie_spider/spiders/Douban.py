# -*- coding: utf-8 -*-
import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

import urllib2
import random
from scrapy.selector import Selector
from config_constant import *

import bson

movie_info_list = db.DoubanTagID.find().limit(20)



class DoubanSpider(scrapy.Spider):

	name = "Douban"

	def start_requests(self):
		for i in movie_info_list:
			yield scrapy.FormRequest(i['url'], dont_filter=True, callback=self.parse)

	def parse(self, response):
		pass



	def proxy_request(self, url):
		request = urllib2.Request(url)
		proxy = urllib2.ProxyHandler(
										{
											'http': 'http://127.0.0.1:8123',
											'https': 'https://127.0.0.1:8123',
										}
									)
		opener = urllib2.build_opener(proxy)
		urllib2.install_opener(opener)
		response_data = opener.open(request).read()
		return response_data










