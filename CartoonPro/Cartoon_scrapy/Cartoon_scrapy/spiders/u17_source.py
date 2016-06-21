# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonSourceItem



class USpider(scrapy.Spider):
	name = "U"
	start_urls = (
					'http://www.u17.com/comic_list/th99_gr99_ca99_ss0_ob0_ac0_as0_wm0_p1.html', 
				)


	def parse(self, response):

		now_url = response.url
		print u'当前URL:%s' % now_url
		sel = Selector(text=response.body)

		position = len(sel.xpath('//*[@class="pagelist"]/a')) - 1
		print position
		all_pages = int(sel.xpath('//*[@class="pagelist"]/a[{0}]/text()'.format(position,)).extract()[0].strip())
		for i in range(1, all_pages + 1):
			request_url = 'http://www.u17.com/comic_list/th99_gr99_ca99_ss0_ob0_ac0_as0_wm0_p{0}.html'.format(i,)
			yield scrapy.FormRequest(request_url, dont_filter=True, callback=self.get_tags)


	def get_tags(self, response):
		item = CartoonSourceItem()
		sel = Selector(text=response.body)

		for i in sel.xpath('//*[@class="comiclist"]/ul/li'):
			item['source'] = 'u17'
			item['title'] = i.xpath('.//*[@class="info"]/h3/strong/a/text()').extract()[0].strip()
			item['url'] = i.xpath('.//*[@class="info"]/h3/strong/a/@href').extract()[0].strip()
			
			yield item






















