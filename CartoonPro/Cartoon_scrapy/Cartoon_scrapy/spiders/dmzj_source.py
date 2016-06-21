# -*- coding: utf-8 -*-

import scrapy
from Cartoon_scrapy.items import CartoonSourceItem
import re
import json

class DmzjSpider(scrapy.Spider):

	name = "dmzj"
	start_urls = (
					'http://s.acg.178.com/mh/index.php?c=category&m=doSearch&status=0&reader_group=0&zone=0&initial=all&type=0&p=1&callback=search.renderResult&_=1466475447527',
				)

	def parse(self, response):

		now_url = response.url
		print u'当前URL:%s' % now_url
		re_result = re.findall(r'(search.renderResult)(.*?)(;)', response.body)
		json_data = json.loads(re_result[0][1][1:-1])
		all_pages = json_data['page_count']
		# print all_pages
		for i in range(1, all_pages+1):
			request_url = 'http://s.acg.178.com/mh/index.php?c=category&m=doSearch&status=0&reader_group=0&zone=0&initial=all&type=0&p={0}&callback=search.renderResult&_=1466475447527'.format(i, )
			yield scrapy.FormRequest( request_url, dont_filter=True, callback=self.get_tags)

	def get_tags(self, response):
	# 	print response.url
		item = CartoonSourceItem()
		re_result = re.findall(r'(search.renderResult)(.*?)(;)', response.body)
		json_data = json.loads(re_result[0][1][1:-1])
		# print json_data
		for i in json_data['result']:
			item['source'] = 'dmzj'
			item['title'] = i['name']
			item['url'] = 'http://manhua.dmzj.com' + i['comic_url']
			
			yield item






















