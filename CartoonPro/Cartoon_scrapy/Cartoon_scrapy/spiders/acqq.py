# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector
from Cartoon_scrapy.items import AcqqInfo
from Cartoon_scrapy.settings import *
import bson
import urllib2
import time
import json
import re

class AcqqSpider(scrapy.Spider):


	name = "acqq_info"

	def start_requests(self):

		mongo_data = db.CartoonSource.find({'source': 'acqq', 'url': '/Comic/comicInfo/id/505430'})
		mongo_data = [i for i in mongo_data]
		for i in mongo_data:
			request_url = 'http://ac.qq.com' + i['url']
			yield scrapy.FormRequest( 	
										request_url, 
										meta={
												'name': i['title'],

											}, 
										dont_filter=True, 
										callback=self.parse
									)


	def parse(self, response):

		sel = Selector(text=response.body)
		item = AcqqInfo()
		item['source'] = 'acqq'
		print u'来源:%s' % item['source']

		item['url'] = response.url
		print u'URL:%s' % item['url']

		item['name'] = response.meta['name']
		print u'名称:%s' % item['name']

		item['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		print u'抓取时间:%s' % item['scrapy_time']

		item['img_url'] = sel.xpath('//*[@class="works-cover ui-left"]/a/img/@src').extract()[0].strip()
		print u'图片链接:%s' % item['img_url']
		# item['img_data'] = bson.Binary(urllib2.urlopen(item['img_url']).read())

		item['author'] = sel.xpath('//*[@class="works-author-info ui-left"]//*[@class="works-author-name"]/text()').extract()[0].strip()
		print u'作者:%s' % item['author']

		for i in sel.xpath('//*[@class="works-intro-digi"]/span'):

			is_which = i.xpath('./text()').extract()[0].strip()
			if is_which == u'人气：':
				item['popular'] = i.xpath('./em/text()').extract()[0].strip()
				p = re.compile("\d+,\d+?")
				for com in p.finditer(item['popular']):
					mm = com.group()
					item['popular'] = item['popular'].replace(mm, mm.replace(",", ""))
				print u'人气:%s' % item['popular']
			if is_which == u'收藏数：':
				item['collect'] = i.xpath('./em/text()').extract()[0].strip()
				print u'收藏数:%s' % item['collect']
		
		item['introduce'] = sel.xpath('//*[@ class="works-intro-short ui-text-gray9"]/text()').extract()[0].strip()
		print u'简介:%s' % item['introduce']
		item['red_tickts'] = sel.xpath('//*[@class="works-vote-list ui-left clearfix"]//*[@id="redcount"]/text()').extract()[0].strip()
		print u'红票数量:%s' % item['red_tickts'] 

		is_score = sel.xpath('//*[@ class="works-score clearfix"]/p/strong/text()').extract()
		if is_score:
			item['score'] = is_score[0].strip()
			print u'评分:%s' % item['score']
		is_people = sel.xpath('//*[@ class="works-score clearfix"]/p/span/text()').extract()
		if is_people:
			item['grade_people'] = is_people[0].strip()
			print u'评级人数:%s' % item['grade_people']

		item['status'] = sel.xpath('//*[@ class="works-intro-status"]/text()').extract()[0].strip()
		print u'状态:%s' % item['status']

		is_update_time = sel.xpath('//*[@ class="works-chapter-log ui-left"]//*[@class="ui-pl10 ui-text-gray6"]/text()').extract()
		if is_update_time:
			item['update_time'] = is_update_time[0].strip()
			print u'最近更新时间:%s' % item['update_time']

		cartoon_id = response.url.split('/')[-1]
		print u'月票信息ID:%s' % cartoon_id
		#月票排名
		u1 = 'http://ac.qq.com/Comic/getMonthTicketInfo/id/{0}?_=1466562048238'.format(cartoon_id,)
		json_r1 = json.loads(urllib2.urlopen(u1).read())
		if json_r1:
			item['month_tickts'] = json_r1['monthTicket']['monthTotal']
			print u'本月月票:%s' % item['month_tickts']
			item['today_tickts'] = json_r1['monthTicket']['dayTotal']
			print u'今日月票:%s' % item['today_tickts']
			item['rank'] = json_r1['monthTicket']['rank']['rankNo']
			print u'本月排名:%s' % item['rank']
			
		#标签
		item['tags'] = list()
		u2 = 'http://ac.qq.com/Comic/userComicInfo?comicId={0}&_=1466562048289'.format(cartoon_id,)
		json_r2 = json.loads(urllib2.urlopen(u2).read())
		for i in json_r2['tag']:
			item['tags'].append(i['name'])
		for ta in item['tags']:
			print u'标签:%s' % ta

		#总评论数
		u3 = 'http://ac.qq.com/Community/topicList?targetId={0}&page=1&_=1466567447160'.format(cartoon_id,)
		sel3 = Selector(text=urllib2.urlopen(u3).read())

		is_comment = sel3.xpath('//*[@ id="pagination-node"]/span/em/text()').extract()
		if is_comment:
			item['all_comments'] = is_comment[0].strip()
			print u'总评论数:%s' % item['all_comments']


		return item




