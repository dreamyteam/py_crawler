# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonSourceItem



class DmzjSpider(scrapy.Spider):
	name = "dmzj"
	start_urls = (
					'http://manhua.dmzj.com/tags/category_search/0-0-0-all-0-0-0-1.shtml#category_nav_anchor', 
				)


	def parse(self, response):

		now_url = response.url
		print u'当前URL:%s' % now_url
		sel = Selector(text=response.body)
		
		all_len = sel.xpath('//*[@class="pages"]/a')
		print len(all_len)
		for i in all_len:
			print i




	# def get_tags(self, response):
	# 	item = CartoonSourceItem()
	# 	sel = Selector(text=response.body)
	# 	for i in sel.xpath('//*[@class="innr3"]/li'):
	# 		item['source'] = 'dm5'
	# 		item['title'] = i.xpath('./a/@title').extract()[0].strip()
	# 		item['url'] = 'http://www.dm5.com' + i.xpath('./a/@href').extract()[0].strip()

	# 		yield item






















