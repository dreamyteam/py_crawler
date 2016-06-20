# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Tv_scrapy.settings import *
import urllib2
import json
import re
import time

#猫眼服务器压力测试 提高并发数测试
class MaoyanSpider(scrapy.Spider):

	name = "maoyan"

	def start_requests(self):
		
		get_info = db.TVInfo.find({'source': 'douban'}).skip(2000)

		for i in get_info:

			url = 'http://piaofang.maoyan.com/search?key=%s' % i['movie_name']
			yield scrapy.FormRequest(	
										url, 
										meta={
												'movie_name': i['movie_name'],  
												'movie_time': i['movie_time'],
												'movie_url': i['movie_url'],
												'IMDB_ID': i['IMDB_ID'],
												'source': i['source'],
												'Relate_ID': i['Relate_ID'],
											}, 
										callback=self.parse
									)


	#按名称和时间刷选电影 搜索按照先豆瓣后IMDB检索

	def parse(self, response):

		print u'猫眼搜索路径:%s' % response.url
		print u'豆瓣电影:%s' % response.meta['movie_name']
		print u'豆瓣URL:%s' % response.meta['movie_url']

		sel = Selector(text=response.body)

		for i in sel.xpath('//*[@id="search-list"]/article'):

			is_all_words = list()
			
			movie_name = i.xpath('.//*[@class="title"]/text()').extract()[0].strip()
			
			date = i.xpath('./text()').extract()[2].strip().split('-')[0].strip()
			
			maoyan_url = 'http://piaofang.maoyan.com' + i.xpath('./@data-url').extract()[0].strip()
			
			is_box_office = i.xpath('./em/text()').extract()[0].strip()
			
			for j in response.meta['movie_name']:
				if j in movie_name:
					is_all_words.append('ok')
				else:
					is_all_words.append('no')
			no_repid_list = list(set(is_all_words))

			if (len(no_repid_list) == 1) and ( no_repid_list[0] == 'ok' ):

				if response.meta['movie_time'] == date:

					print u'cat名称:%s' % movie_name 
					print u'cat时间:%s' % date
					print u'catURL:%s' % maoyan_url

					if is_box_office != u'暂无票房数据':

							return scrapy.FormRequest(	maoyan_url, 
														meta={
																'movie_name': response.meta['movie_name'],  
																'movie_time': response.meta['movie_time'],
																'movie_url': response.meta['movie_url'],
																'IMDB_ID': response.meta['IMDB_ID'],
																'source': response.meta['source'],
																'Relate_ID': response.meta['Relate_ID'],
																'cat_url': maoyan_url,
															},													
															callback=self.maoyan_info
													)

	#猫眼基本信息
	def maoyan_info(self, response):

		sel = Selector(text=response.body)
		data = dict()
		data['source'] = response.meta['source']
		data['movie_name'] = response.meta['movie_name']
		print u'豆瓣电影名:%s' % data['movie_name']
		data['movie_url'] = response.meta['movie_url']
		data['IMDB_ID'] = response.meta['IMDB_ID']
		print u'豆瓣电影URL:%s' % data['movie_url']
		data['Relate_ID'] = response.meta['Relate_ID']
		print u'内置关联ID:%s' % data['Relate_ID']

		data['all_box_office'] = sel.xpath('//*[@class="tags clearfix"]/span/text()').extract()[0].strip()
		print u'总票房:%s' % data['all_box_office']

		
		#日票房信息
		all_day = sel.xpath('//*[@id="ticketList"]//*[@id="ticket_tbody"]/ul')
		data['day_info'] = list()

		for i in all_day:

			update_dict = dict()
			update_dict['date'] = i.xpath('./li[1]/span/b/text()').extract()[0].strip()
			print u'日期:%s' % update_dict['date']
			update_dict['day_box_officce'] = i.xpath('./li[2]/text()').extract()[0].strip()
			print u'当日票房:%s' % update_dict['day_box_officce']
			update_dict['day_box_officce_percent'] = i.xpath('./li[3]/text()').extract()[0].strip()
			print u'票房占比:%s' % update_dict['day_box_officce_percent']
			update_dict['day_release_percent'] = i.xpath('./li[4]/text()').extract()[0].strip()
			print u'排片占比:%s' % update_dict['day_release_percent']
			update_dict['day_people'] = i.xpath('./li[5]/text()').extract()[0].strip()
			print u'场均人次:%s' % update_dict['day_people']
			data['day_info'].append(update_dict)
			print '-------' * 5

		city_data = self.city_info(data, response.meta['cat_url'])
		# print city_data
		data.update(city_data)
		data['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		db.CatEyeInfo.update({'movie_url': data['movie_url']}, {'$set': data}, True)


	#猫眼城市信息
	def city_info(self, meta_data, maoyan_url):

		update_data = dict()
		update_data['city_info'] = dict()

		for i in meta_data['day_info']:
			url = maoyan_url + '/cityBox?date={0}'.format(i['date'])
			print u'城市票房的URL:%s' % url
			json_data = json.loads(urllib2.urlopen(url).read())

			sel = Selector(text=json_data['html'])

			all_info = sel.xpath('//*[@class="m-table normal m-table-city"]/tbody/tr')
			
			city_info_list = list()

			for j in all_info:

				update_dict = dict()
				update_dict['city'] = j.xpath('./td[1]/text()').extract()[0].strip()
				print u'城市:%s' % update_dict['city']
				update_dict['box_office'] = j.xpath('./td[2]/text()').extract()[0].strip()
				print u'票房:%s' % update_dict['box_office']
				update_dict['box_office_percent'] = j.xpath('./td[3]/text()').extract()[0].strip()
				print u'票房占比:%s' % update_dict['box_office_percent']
				update_dict['release_percent'] = j.xpath('./td[4]/text()').extract()[0].strip()
				print u'排片占比:%s' % update_dict['release_percent']
				update_dict['total_box_office'] = j.xpath('./td[5]/text()').extract()[0].strip()
				print u'累计票房:%s' % update_dict['total_box_office']
				update_dict['position_percent'] = j.xpath('./td[6]/text()').extract()[0].strip()
				print u'排座占比:%s' % update_dict['position_percent']
				update_dict['gold_percent'] = j.xpath('./td[7]/text()').extract()[0].strip()
				print u'黄金场占比:%s' % update_dict['gold_percent']
				update_dict['per_people'] = j.xpath('./td[8]/text()').extract()[0].strip()
				print u'场均人次:%s' % update_dict['per_people']
				update_dict['people'] = j.xpath('./td[9]/text()').extract()[0].strip()
				print u'人次:%s' % update_dict['people']
				update_dict['times'] = j.xpath('./td[10]/text()').extract()[0].strip()
				print u'场次:%s' % update_dict['times']

				city_info_list.append(update_dict)
				print '-------------' * 5

			update_data['city_info'][i['date']] = city_info_list


		return update_data



