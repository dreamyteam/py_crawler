# -*- coding: utf-8 -*-

from Cartoon_scrapy.items import CartoonSourceItem
from Cartoon_scrapy.settings import *

class CartoonPipeline(object):

    def process_item(self, item, spider):

        # print item['title']
        # print item['url']
        db.CartoonSource.update({'url': item['url']}, {'$set': item}, True)




