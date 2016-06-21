# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2

class Dm5SourceSpider(scrapy.Spider):


	name = "dm5_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'dm5'}).skip(2).limit(1)
		for i in mongo_data:
			yield scrapy.FormRequest( i['url'], dont_filter=True, callback=self.parse)



	def parse(self, response):

		sel = Selector(text=response.body)
		item = CartoonInfo()
	 	item['source'] = 'dm5'
	 	item['name'] = sel.xpath('//*[@class="inbt_title_h2"]/text()').extract()[0].strip()
	 	item['url'] = response.url
	 	is_other_name = sel.xpath('//*[@class="inbt_title_h3"]/text()').extract()
	 	if is_other_name:
	 		item['other_name'] = is_other_name[0].strip()
	 	else:
	 		item['other_name'] = ''
	 	item['img_url'] = sel.xpath('//*[@ style=" margin-right:20px"]/img/@src').extract()[0].strip()
	 	# item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())



	 	# item['area'] = 
	 	# item['author']
	 	# item['c_type']
	 	# item['introduce']


	 	# item['popular']
	 	# item['update_time']
	 	# item['status']
	 	# item['all_theme']
	 	# item['all_response']
	 	return item

























