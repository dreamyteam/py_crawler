# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonSourceItem



class Dm5SourceSpider(scrapy.Spider):
	name = "dm5"
	start_urls = (
					'http://www.dm5.com/manhua-updated-p1/', 
					'http://www.dm5.com/manhua-completed-p1/',
				)


	def parse(self, response):
		now_url = response.url
		print u'当前URL:%s' % now_url
		sel = Selector(text=response.body)
		position = len(sel.xpath('//*[@id="search_fy"]/a')) - 1
		all_pages = int(sel.xpath('//*[@id="search_fy"]/a[{0}]/text()'.format(position,)).extract()[0].strip())
		print u'总页数:%s' % all_pages

		for i in range(1, all_pages + 1):
			request_url = now_url.split('-p')[0] + '-p{0}/'.format(i,)
			yield scrapy.FormRequest(request_url, dont_filter=True, callback=self.get_tags)


	def get_tags(self, response):
		item = CartoonSourceItem()
		sel = Selector(text=response.body)
		for i in sel.xpath('//*[@class="innr3"]/li'):
			item['source'] = 'dm5'
			item['title'] = i.xpath('./a/@title').extract()[0].strip()
			item['url'] = 'http://www.dm5.com' + i.xpath('./a/@href').extract()[0].strip()

			yield item






















