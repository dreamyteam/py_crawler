# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.TVData

#服务器压力测试 提高并发数测试
class MaoyanSpider(scrapy.Spider):

	name = "maoyan"

	def start_requests(self):
		
		get_info = db.TVInfo.find({'source': 'douban'}).skip(0).limit(2)

		for i in get_info:

			url = 'http://piaofang.maoyan.com/search?key=%s' % i['movie_name']

			yield scrapy.FormRequest(url, meta={'file_name': i['movie_name']}, callback=self.parse)


	def parse(self, response):
		print u'路径:%s' % response.url
		print u'电影名称:%s' % response.meta['file_name']
		sel = Selector(text=response.body)
		# print sel.xpath('//*[@id="search-list"]/article')
		for i in sel.xpath('//*[@id="search-list"]/article'):
			movie_name = i.xpath('.//*[@class="title"]/text()').extract()[0].strip()
			print u'电影名称:%s' % movie_name
			date = i.xpath('./text()').extract()[2].strip()
			print u'时间:%s' % date
			movie_url = 'http://piaofang.maoyan.com' + i.xpath('./@data-url').extract()[0].strip()
			print u'电影URL:%s' % movie_url
			print '---------' * 5

		print '*********' * 8

	def maoyan_info(self, url):

		response = urllib2.urlopen(url)
		sel = Selector(text=response.read())
		data = cateye_info()
		data['url'] = url
		print u'来源URL:%s' % data['url']
		data['all_box_office'] = sel.xpath('//*[@class="tags clearfix"]/span/text()').extract()[0].strip()
		print u'总票房:%s' % data['all_box_office']

		#日票房信息
		all_day = sel.xpath('//*[@id="ticketList"]//*[@id="ticket_tbody"]/ul')
		for i in all_day:
			date = i.xpath('./li[1]/span/b/text()').extract()[0].strip()
			print u'日期:%s' % date
			day_box_officce = i.xpath('./li[2]/text()').extract()[0].strip()
			print u'当日票房:%s' % day_box_officce
			day_box_officce_percent = i.xpath('./li[3]/text()').extract()[0].strip()
			print u'票房占比:%s' % day_box_officce_percent
			day_release_percent = i.xpath('./li[4]/text()').extract()[0].strip()
			print u'排片占比:%s' % day_release_percent
			day_people = i.xpath('./li[5]/text()').extract()[0].strip()
			print u'场均人次:%s' % day_people

			print '-------' * 5


	#城市信息
	def city_info(self, date):

		url = 'http://piaofang.maoyan.com/movie/78421/cityBox?date={0}'.format(date)
		json_data = json.loads(urllib2.urlopen(url).read())
		sel = Selector(text=json_data['html'])
		all_info = sel.xpath('//*[@class="m-table normal m-table-city"]/tbody/tr')
		for i in all_info:
			city = i.xpath('./td[1]/text()').extract()[0].strip()
			print u'城市:%s' % city
			box_office = i.xpath('./td[2]/text()').extract()[0].strip()
			print u'票房:%s' % box_office
			box_office_percent = i.xpath('./td[3]/text()').extract()[0].strip()
			print u'票房占比:%s' % box_office_percent
			release_percent = i.xpath('./td[4]/text()').extract()[0].strip()
			print u'排片占比:%s' % release_percent
			total_box_office = i.xpath('./td[5]/text()').extract()[0].strip()
			print u'累计票房:%s' % total_box_office
			position_percent = i.xpath('./td[6]/text()').extract()[0].strip()
			print u'排座占比:%s' % position_percent
			gold_percent = i.xpath('./td[7]/text()').extract()[0].strip()
			print u'黄金场占比:%s' % gold_percent
			per_people = i.xpath('./td[8]/text()').extract()[0].strip()
			print u'场均人次:%s' % per_people
			people = i.xpath('./td[9]/text()').extract()[0].strip()
			print u'人次:%s' % people
			times = i.xpath('./td[10]/text()').extract()[0].strip()
			print u'场次:%s' % times
			
			print '-------------' * 5

			# city_info('2016-06-11')
			# maoyan_info('http://piaofang.maoyan.com/movie/78421')







