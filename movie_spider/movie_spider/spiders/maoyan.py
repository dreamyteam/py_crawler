# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData


class MaoyanSpider(scrapy.Spider):

	name = "maoyan"

	def start_requests(self):
		# get_info =db.MovieInfo.find({'source': 'douban'}).skip(100).limit(100)
		# for i in get_info:
		name = '钢铁侠'
		url = 'http://piaofang.maoyan.com/search?key=%s' % name
		# url = 'http://piaofang.maoyan.com/search?key=%E9%AD%94%E5%85%BD'
		yield scrapy.FormRequest(url, callback=self.parse)
		
		
	def parse(self, response):
		print u'路径:%s' % response.url
		sel = Selector(text=response.body)
		# print sel.xpath('//*[@id="search-list"]/article')
		for i in sel.xpath('//*[@id="search-list"]/article'):
			movie_name = i.xpath('.//*[@class="title"]/text()').extract()[0].strip()
			print u'电影名称:%s' % movie_name
			movie_url = 'http://piaofang.maoyan.com' + i.xpath('./@data-url').extract()[0].strip()
			print u'电影URL:%s' % movie_url
			print '---------' * 5
			
		print '*********' * 5







