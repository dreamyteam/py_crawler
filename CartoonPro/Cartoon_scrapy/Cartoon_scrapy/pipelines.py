# -*- coding: utf-8 -*-

from Cartoon_scrapy.items import CartoonSourceItem, CartoonInfo
from Cartoon_scrapy.settings import *


class CartoonPipeline(object):

	def process_item(self, item, spider):

		if spider.__class__.name in ['dm5', 'dmzj', 'QQ', 'U']:
			
			db.CartoonSource.update({'url': item['url']}, {'$set': item}, True)
		
		elif spider.__class__.name == 'U_info':
			if item['return_status'] != 'pass':
				db.CartoonInfo.update({'url': item['url']}, {'$set': item}, True)

		elif spider.__class__.name == 'acqq_info':
			print u'******可以自动执行*********'
			# db.CartoonInfo.update({'c_id': item['url']}, {'$set': item})
		else:
			print u'******可以自动执行*********' 
		# else:
		# 	db.CartoonInfo.update({'url': item['url']}, {'$set': item}, True)

				






