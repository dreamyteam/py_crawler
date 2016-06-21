# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2
import time
class Dm5SourceSpider(scrapy.Spider):


	name = "dm5_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'dm5'})
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
	 	item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())
	 	item['area'] = str()
	 	item['author'] = str()
	 	item['c_type'] = str()
	 	item['introduce'] = str()
	 	item['popular'] = str()
	 	item['update_time'] = str()
	 	item['status'] = str()
	 	item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
	 	item['all_theme'] = str()
	 	item['all_response'] = str()
	 	for i in sel.xpath('//*[@class="innr92 red_lj"]/span')[1:]:
	 		for j in dm5_dict:
	 			if dm5_dict[j] in i.xpath('./text()').extract()[0].strip():
		 			if i.xpath('./a/text()').extract():
		 				item[j] = i.xpath('./a/text()').extract()[0].strip()
		 			else:
		 				item[j] = i.xpath('./text()').extract()[0].strip().split(u'：')[1].strip()
		 				
		if sel.xpath('//*[@ class="mhjj mato10 red_lj"][1]'):
			item['introduce'] = sel.xpath('//*[@ class="mhjj mato10 red_lj"][1]/p/text()').extract()[0].strip()
			if sel.xpath('//*[@ class="mhjj mato10 red_lj"][1]//*[@style="display: none;"]/text()').extract():
				item['introduce'] = item['introduce'] + sel.xpath('//*[@ class="mhjj mato10 red_lj"][1]//*[@style="display: none;"]/text()').extract()[0].strip()
		if sel.xpath('//*[@ class="inkk ma5"]//*[@ class="inbt"]/span/text()').extract():
			theme_res = sel.xpath('//*[@ class="inkk ma5"]//*[@ class="inbt"]/span/text()').extract()[0].strip()
			left_res = theme_res.split(u'总计')[1].split(u'篇')
			item['all_theme'] = left_res[0].strip()
			item['all_response'] = left_res[1].split(u'，')[1].split(u'个')[0].strip()

	 	
	 	return item

























