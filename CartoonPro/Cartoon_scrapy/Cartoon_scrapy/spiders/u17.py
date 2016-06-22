# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import UInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2
import time
import json
import re

class USpider(scrapy.Spider):


	name = "U_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'u17'})
		mongo_data = [i for i in mongo_data]
		for i in mongo_data:
			yield scrapy.FormRequest( 	
										i['url'], 
										meta={
												'name': i['title'],

											}, 
										dont_filter=True, 
										callback=self.parse
									)


	def parse(self, response):

		sel = Selector(text=response.body)
		item = UInfo()
		item['source'] = 'u17'
		# print u'来源:%s' % item['source']

		item['url'] = response.url
		# print u'URL:%s' % item['url']

		item['name'] = response.meta['name']
		# print u'名称:%s' % item['name']

		item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		# print u'抓取时间:%s' % item['scrapy_time']

		try:
			item['img_url'] = sel.xpath('//*[@ id="cover"]/a/img/@src').extract()[0].strip()
			# print u'图片链接:%s' % item['img_url']
			# item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())
		except Exception, e:
			item['return_status'] = 'pass'
			return item

		item['return_status'] = 'ok'
		item['author'] = sel.xpath('//*[@ class="author_info"]//*[@class="info"]//*[@class="name"]/text()').extract()[0].strip()
		# print u'作者:%s' % item['author']

		for i in sel.xpath('//*[@class="info"]//*[@class="top"]/div'):
			is_list = list()
			for j in i.xpath('./text()').extract():
				is_list.append(j.strip())
			for z in u17_dict:
				if z in is_list:
					index_p = is_list.index(z) + 1
					get_info = i.xpath('./span[{0}]/text()'.format(index_p,)).extract()[0].strip()
					if '/' in get_info:
						deal_list = list()
						for x in get_info.split('/'):
							deal_list.append(x.strip())
						get_info = '/'.join(deal_list)
					item[u17_dict[z]] = get_info
					# print '******%s:%s*****' % (z, item[u17_dict[z]])
		
			if u'总点击：' in is_list:
				item['all_click'] = i.xpath('./i/text()').extract()[0].strip()
				# print u'总点击：%s' % item['all_click']
			if u'总月票：' in is_list:
				item['all_tickts'] = i.xpath('./i/text()').extract()[0].strip()
				# print u'总月票：%s' % item['all_tickts']

		tag_list = list()	
		for t in sel.xpath('//*[@ class="label"]//*[@class="label_con"]//*[@id="1-1"]/a'):
			tag_list.append(t.xpath('./text()').extract()[0].strip())

		item['tags'] = tag_list
		# for tt in item['tags']:
			# print u'标签:%s' % tt

		is_col = sel.xpath('//*[@ id="bookrack"]/a/span/i/text()').extract()
		if is_col:
			item['collect'] = is_col[0].strip()
			# print u'收藏:%s' % item['collect']

		is_update = sel.xpath('//*[@class="bot"]//*[@class="fl"]/span/text()').extract()
		if is_update:
			item['update_time'] = is_update[0].strip()
			# print u'最后更新时间:%s' % item['update_time']

		item['introduce'] = sel.xpath('//*[@ id="words"]/text()').extract()[0].strip()
		# print u'简介:%s' % item['introduce']

		
		for c1 in sel.xpath('//*[@class="more"]//*[@class="pop_box"]/p'):
			for c2 in c1.xpath('./span'):
				
				if c2.xpath('./text()').extract()[0].strip() == u'总评论：':
					item['all_comments'] = c2.xpath('./em/text()').extract()[0].strip()
					# print u'总评论:%s' % item['all_comments']

		return item
		





