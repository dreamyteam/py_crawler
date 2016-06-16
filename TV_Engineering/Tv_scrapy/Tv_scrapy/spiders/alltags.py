# # -*- coding: utf-8 -*-

# import scrapy
# from scrapy.selector import Selector
# from Tv_scrapy.settings import *
# import urllib2
# import json
# import re
# import time
# from scrapy.http import Request


# #获取豆瓣所有标签得到电影来源
# class DoubanSpider(scrapy.Spider):

# 	name = "douban"
# 	start_id = 0

# 	def start_requests(self):

# 		url = 'https://movie.douban.com/tag/%E5%88%98%E5%BE%B7%E5%8D%8E?start={0}&type=T'.format(self.start_id,)
# 		yield scrapy.FormRequest(url, callback=self.parse)

# 	def parse(self, response):

# 		print u'标签URL:%s' % response.url
# 		sel = Selector(text=response.body)
# 		all_info = sel.xpath('//*[@class="article"]//*[@width="100%"]')

# 		if all_info[1:]:
# 			for i in all_info[1:]:
# 				movie_name = i.xpath('.//*[@class="pl2"]/a/text()').extract()[0].strip().split('/')[0].strip()
# 				movie_url = i.xpath('.//*[@class="pl2"]/a/@href').extract()[0].strip()
# 				movie_id = movie_url.split('/')[-2].strip()
# 				scrapy_time = time.strftime('%Y-%m-%d %H:%M:%S')
# 				print movie_name
# 				print movie_url
# 				print movie_id
				
# 				insert_dict = {
# 								'tag': u'刘德华',
# 								'title': movie_name,
# 								'url': movie_url,
# 								'id': movie_id,
# 								'scrapy_time': scrapy_time,
# 								'source': 'douban',
# 							}

# 				db.DoubanTagID.update({'url': movie_url}, {'$set': insert_dict}, True)

# 			is_next = sel.xpath('//*[@rel="next"]')
# 			self.start_id += 20
# 			url = 'https://movie.douban.com/tag/%E5%88%98%E5%BE%B7%E5%8D%8E?start={0}&type=T'.format(self.start_id,)
# 			if is_next:
# 				return scrapy.FormRequest(url, callback=self.parse)

# 			else:
# 				print u'没了 都在这里了'
# 		else:
# 			print u'也没了'





