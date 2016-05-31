# -*- coding: utf-8 -*-
import scrapy

from movie_spider.items import MovieSpiderItem
from scrapy.selector import Selector
import time

class TtidSpider(scrapy.Spider):

	name = "TtidSpider"

	def start_requests(self):

		for i in range(1,1000):
			yield scrapy.FormRequest('https://movie.douban.com/subject_search?search_text=+tt%07d&cat=1002' % i, meta={'send_id': i},
									dont_filter=True, callback=self.parse)

	def parse(self, response):
		get_info = MovieSpiderItem()
		data = response.body
		info = Selector(text=data).xpath('//tr[@class="item"]/td[2]/div[@class="pl2"]/a/text()')

		if info:
			# ttid = 'tt%07d' % i
			# print u'tt编号:%s' % ttid
			# title = Selector(text=data).xpath('//div[@class="pl2"]/a/text()').extract()[0].strip().split('/')[0].strip()
			# print u'电影名称:%s' % title
			# movie_url = Selector(text=data).xpath('//div[@class="pl2"]/a/@href').extract()[0].strip()
			# print u'电影路径:%s' % movie_url
			get_info['ttid'] = 'tt%07d' % response.meta['send_id']
			get_info['title'] = Selector(text=data).xpath('//div[@class="pl2"]/a/text()').extract()[0].strip().split('/')[0].strip()
			get_info['movie_url'] = Selector(text=data).xpath('//div[@class="pl2"]/a/@href').extract()[0].strip()
			get_info['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		yield get_info




