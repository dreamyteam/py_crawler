# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import AcqqInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2
import time
import json
import re

class AcqqSpider(scrapy.Spider):


	name = "acqq_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'acqq'}).skip(100).limit(1)
		mongo_data = [i for i in mongo_data]
		for i in mongo_data:
			request_url = 'http://ac.qq.com' + i['url']
			yield scrapy.FormRequest( 	
										request_url, 
										meta={
												'name': i['title'],

											}, 
										dont_filter=True, 
										callback=self.parse
									)


	def parse(self, response):

		sel = Selector(text=response.body)
		item = AcqqInfo()
		item['source'] = 'acqq'
		print u'来源:%s' % item['source']

		item['url'] = response.url
		print u'URL:%s' % item['url']

		item['name'] = response.meta['name']
		print u'名称:%s' % item['name']

		item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		print u'抓取时间:%s' % item['scrapy_time']

		item['img_url'] = sel.xpath('//*[@class="works-cover ui-left"]/a/img/@src').extract()[0].strip()
		print u'图片链接:%s' % item['img_url']
		# item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())

		item['author'] = sel.xpath('//*[@class="works-author-info ui-left"]//*[@class="works-author-name"]/text()').extract()[0].strip()
		print u'作者:%s' % item['author']

		for i in sel.xpath('//*[@class="works-intro-digi"]/span'):

			is_which = i.xpath('./text()').extract()[0].strip()
			if is_which == u'人气：':
				item['popular'] = i.xpath('./em/text()').extract()[0].strip()
				p = re.compile("\d+,\d+?")
				for com in p.finditer(item['popular']):
					mm = com.group()
					item['popular'] = item['popular'].replace(mm, mm.replace(",", ""))
				print u'人气:%s' % item['popular']
			if is_which == u'收藏数：':
				item['collect'] = i.xpath('./em/text()').extract()[0].strip()
				print u'收藏数:%s' % item['collect']
		# is_tags = sel.xpath('//*[@ class="works-intro-tags"]//*[@id="tags-show"]/a')
		
		# item['tags'] = list()
		# if is_tags:
		# 	for tag in is_tags:
		# 		print u'标签:%s' % tag.xpath('./text()').extract()[0].strip()
		# 		item['tags'].append(tag.xpath('./text()').extract()[0].strip())
		item['introduce'] = sel.xpath('//*[@ class="works-intro-short ui-text-gray9"]/text()').extract()[0].strip()
		print u'简介:%s' % item['introduce']
		item['red_tickts'] = sel.xpath('//*[@class="works-vote-list ui-left clearfix"]//*[@id="redcount"]/text()').extract()[0].strip()
		print u'红票数量:%s' % item['red_tickts'] 

		is_score = sel.xpath('//*[@ class="works-score clearfix"]/p/strong/text()').extract()
		if is_score:
			item['score'] = is_score[0].strip()
			print u'评分:%s' % item['score']
		is_people = sel.xpath('//*[@ class="works-score clearfix"]/p/span/text()').extract()
		if is_people:
			item['grade_people'] = is_people[0].strip()
			print u'评级人数:%s' % item['grade_people']

		item['status'] = sel.xpath('//*[@ class="works-intro-status"]/text()').extract()[0].strip()
		print u'状态:%s' % item['status']




