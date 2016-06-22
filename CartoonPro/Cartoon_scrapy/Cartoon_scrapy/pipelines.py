# -*- coding: utf-8 -*-

from Cartoon_scrapy.items import CartoonSourceItem, CartoonInfo
from Cartoon_scrapy.settings import *

class CartoonPipeline(object):

	def process_item(self, item, spider):
		# print spider.__class__.name
		if spider.__class__.name in ['dm5', 'dmzj', 'QQ', 'U']:
			# print item['title']
			# print item['url']
			db.CartoonSource.update({'url': item['url']}, {'$set': item}, True)
		
		elif spider.__class__.name == 'U_info':
			if item['return_status'] != 'pass':
				db.CartoonInfo.update({'url': item['url']}, {'$set': item}, True)
		
		else:
			db.CartoonInfo.update({'url': item['url']}, {'$set': item}, True)

				






