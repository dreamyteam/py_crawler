# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import CartoonInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2
import time
import json
import re
class DmzjSpider(scrapy.Spider):


	name = "dmzj_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'dmzj'}).skip(0).limit(10)
		for i in mongo_data:
			yield scrapy.FormRequest( 	
										i['url'], 
										meta={
												'name': i['title'],
												'author': i['author'],
												'c_ticai': i['c_ticai'],
												'js_id': i['js_id']
											}, 
										dont_filter=True, 
										callback=self.parse
									)


	def parse(self, response):
		sel = Selector(text=response.body)
		item = CartoonInfo()
		item['source'] = 'dmzj'
		# print u'来源:%s' % item['source']

		item['url'] = response.url
		# print u'URL:%s' % item['url']

		item['name'] = response.meta['name']
		# print u'名称:%s' % item['name']

		item['other_name'] = str()
		item['area'] = str()
		item['all_theme'] = str()
		item['all_response'] = str()
		item['all_comments'] = str()
		item['author'] = response.meta['author']
		# print u'作者:%s' % item['author']

		item['c_type'] = str() #分类

		item['c_ticai'] = response.meta['c_ticai']
		# print u'题材:%s' % item['c_ticai']

		item['popular'] = str()
		item['update_time'] = str()
		item['status'] = str()
		item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		# print u'抓取时间:%s' % item['scrapy_time']
		item['img_url'] = sel.xpath('//*[@ class="anim_intro_ptext"]/a/img/@src').extract()[0].strip()
		# item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())
		# print u'图片地址:%s' % item['img_url']

		for i in sel.xpath('//*[@ class="anim-main_list"]/table/tr'):
			is_name = i.xpath('./th/text()').extract()[0].strip()
			if is_name in dmzj_dict:
				if is_name != u'最新收录：':

					if i.xpath('./td/a/text()').extract():
						item[dmzj_dict[is_name]] = i.xpath('./td/a/text()').extract()[0].strip()
					else:
						if i.xpath('./td/text()').extract():
							item[dmzj_dict[is_name]] = i.xpath('./td/text()').extract()[0].strip()
					# print is_name, item[dmzj_dict[is_name]]
				else:
					item['update_time'] = i.xpath('./td/span/text()').extract()[0]
					# print is_name, item['update_time']

		item['introduce'] = sel.xpath('//*[@class="line_height_content"]/text()').extract()[0].strip()
		# print item['introduce']
		
		res = urllib2.urlopen('http://manhua.dmzj.com/hits/{0}.json'.format(response.meta['js_id']))
		json_data = json.loads(res.read())
		if 'hot_hits' in json_data:
			item['popular'] = json_data['hot_hits']
		# print u'人气:%s' % item['popular']
		
		comment_url = 'http://interface.dmzj.com/api/NewComment2/total?callback=s_0&&type=4&obj_id={0}&countType=1&authorId=&_=1466496505642'.format(response.meta['js_id'],)
		comment_res = urllib2.urlopen(comment_url)
		re_result = re.findall(r'("data":)(.*?)(})', comment_res.read())
		
		if re_result:
			item['all_comments'] = re_result[0][1]
		# print item['all_theme']
		
		return item











