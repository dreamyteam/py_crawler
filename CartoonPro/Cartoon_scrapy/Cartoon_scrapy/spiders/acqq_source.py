# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonSourceItem



class AcQQSpider(scrapy.Spider):
	
	name = "QQ"
	start_urls = (
					'http://ac.qq.com/Comic/all/search/time/page/1', 
				)


	def parse(self, response):

		now_url = response.url
		print u'当前URL:%s' % now_url
		# sel = Selector(text=response.body)
		# print sel.xpath('/html/body/div[3]/div[2]/div/div[2]/ul/li[9]/div[2]/h3/a/text()').extract()[0].strip()
		# position = len(sel.xpath('//*[@id="pagination2"]/a')) - 1

		for i in range(1, 2):
			yield scrapy.FormRequest('http://ac.qq.com/Comic/all/search/time/page/{0}'.format(i,), dont_filter=True, callback=self.get_tags)
				
	def get_tags(self, response):
		item = CartoonSourceItem()
		sel = Selector(text=response.body)

		for i in sel.xpath('//*[@class="ret-search-list clearfix"]/li'):
			
			item['source'] = 'acqq'
			item['title'] = i.xpath('./div[2]/h3/a/text()').extract()[0].strip()
			item['url'] = i.xpath('./div[2]/h3/a/@href').extract()[0].strip()

			yield item






















