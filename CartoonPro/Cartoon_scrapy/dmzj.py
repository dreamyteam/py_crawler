# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from scrapy.selector import Selector
import urllib2
import time
import json
import re

import pymongo 
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.CartoonData
from cartoonconfig import *


class Dmzj(object):

	def __init__(self, movie_dict, flag):

		self.info_dict = dmzj()
		self.movie_dict = movie_dict
		self.flag = flag
		

	def run(self):
		
		if self.flag == 'first':
			if 'http://manhua.' in self.movie_dict['url']:
				return_info = self.base_info()
			elif 'http://www.' in self.movie_dict['url']:
				return_info = self.base_info_2()
		if return_info != 'pass':
			db.CartoonInfo.update({'url': self.info_dict['url']}, {'$set': self.info_dict}, True)
	
	def base_info(self):

		try:
			response = proxy_request(self.movie_dict['url'])
		except urllib2.HTTPError, e:
			return 'pass'

		sel = Selector(text=response.read())

		self.info_dict['source'] = 'dmzj'
		# print u'来源:%s' % self.info_dict['source']

		self.info_dict['url'] = response.url
		print u'URL:%s' % self.info_dict['url']

		self.info_dict['name'] = self.movie_dict['title']
		print u'名称:%s' % self.info_dict['name']

		self.info_dict['author'] = self.movie_dict['author']
		# print u'作者:%s' % self.info_dict['author']

		self.info_dict['c_ticai'] = self.movie_dict['c_ticai']
		# print u'题材:%s' % self.info_dict['c_ticai']

		self.info_dict['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		# print u'抓取时间:%s' % self.info_dict['scrapy_time']
		self.info_dict['img_url'] = sel.xpath('//*[@ class="anim_intro_ptext"]/a/img/@src').extract()[0].strip()
		# print u'图片地址:%s' % self.info_dict['img_url']

		for i in sel.xpath('//*[@ class="anim-main_list"]/table/tr'):
			is_name = i.xpath('./th/text()').extract()[0].strip()
			if is_name in dmzj_dict:
				if is_name != u'最新收录：':

					if i.xpath('./td/a/text()').extract():
						self.info_dict[dmzj_dict[is_name]] = i.xpath('./td/a/text()').extract()[0].strip()
					else:
						if i.xpath('./td/text()').extract():
							self.info_dict[dmzj_dict[is_name]] = i.xpath('./td/text()').extract()[0].strip()
					# print is_name, self.info_dict[dmzj_dict[is_name]]
				else:
					self.info_dict['update_time'] = i.xpath('./td/span/text()').extract()[0]
					# print is_name, self.info_dict['update_time']

		self.info_dict['introduce'] = sel.xpath('//*[@class="line_height_content"]/text()').extract()[0].strip()
		# print self.info_dict['introduce']
		
		res = proxy_request('http://manhua.dmzj.com/hits/{0}.json'.format(self.movie_dict['js_id']))
		json_data = json.loads(res.read())
		if 'hot_hits' in json_data:
			self.info_dict['popular'] = json_data['hot_hits']
		# print u'人气:%s' % self.info_dict['popular']
		if 'sub_amount' in json_data:
			self.info_dict['rss_num'] = json_data['sub_amount']
		# print u'订阅人数:%s' % self.info_dict['rss_num']

		comment_url = 'http://interface.dmzj.com/api/NewComment2/total?callback=s_0&&type=4&obj_id={0}&countType=1&authorId=&_=1466496505642'.format(self.movie_dict['js_id'],)
		comment_res = proxy_request(comment_url)
		re_result = re.findall(r'("data":)(.*?)(})', comment_res.read())
		
		if re_result:
			self.info_dict['all_comments'] = re_result[0][1]
		# print u'所有评论:%s' %  self.info_dict['all_comments']
		is_relate = sel.xpath('//*[@ class="anim_data_mnew about-info"]//ul/li')
		if is_relate:
			animation = sel.xpath('//*[@ class="anim_data_mnew about-info"]//ul/li/a/strong/text()').extract()[0].strip()
			# print u'动画:%s' % animation
			a_status = sel.xpath('//*[@ class="anim_data_mnew about-info"]//ul/li/span/text()').extract()[0].strip()
			# print u'状态:%s' % a_status
			self.info_dict['relate_info'].append([animation, a_status])

	def base_info_2(self):

		try:
			response = proxy_request(self.movie_dict['url'])
		except urllib2.HTTPError, e:
			return 'pass'

		sel = Selector(text=response.read())

		self.info_dict['source'] = 'dmzj'
		print u'来源:%s' % self.info_dict['source']

		self.info_dict['url'] = response.url
		print u'URL:%s' % self.info_dict['url']

		self.info_dict['name'] = self.movie_dict['title']
		print u'名称:%s' % self.info_dict['name']

		self.info_dict['author'] = self.movie_dict['author']
		print u'作者:%s' % self.info_dict['author']

		self.info_dict['c_ticai'] = self.movie_dict['c_ticai']
		print u'题材:%s' % self.info_dict['c_ticai']

		self.info_dict['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		print u'抓取时间:%s' % self.info_dict['scrapy_time']

		self.info_dict['img_url'] = sel.xpath('//*[@class="comic_i_img"]/a/img/@src').extract()[0].strip()

		print u'图片地址:%s' % self.info_dict['img_url']

		for i in sel.xpath('//*[@class="comic_deCon_liO"]/li'):

			is_name = i.xpath('./text()').extract()[0].strip()

			for j in dmzj_dict2:
				if dmzj_dict2[j] in is_name:
					self.info_dict[j] = is_name
					print j, is_name


		is_introduce = sel.xpath('//*[@class="comic_deCon_d"]/text()').extract()
		if is_introduce:
			self.info_dict['introduce'] = is_introduce[0].strip()
		else:
			self.info_dict['introduce'] = sel.xpath('//*[@class="comic_deCon_d"]/a/text()').extract()[0].strip()
		print self.info_dict['introduce']
		
		self.info_dict['update_time'] = sel.xpath('//*[@class="zj_list_head_dat"]/text()').extract()[0].strip()
		print u'更新时间:%s' % self.info_dict['update_time'] 

		res = proxy_request('http://www.dmzj.com/static/hits/{0}.json'.format(self.movie_dict['js_id']))
		json_data = json.loads(res.read())
		if 'hot_hits' in json_data:
			self.info_dict['popular'] = json_data['hot_hits']
		print u'人气:%s' % self.info_dict['popular']
		if 'sub_amount' in json_data:
			self.info_dict['rss_num'] = json_data['sub_amount']
		print u'订阅人数:%s' % self.info_dict['rss_num']

		comment_url = 'http://interface.dmzj.com/api/NewComment2/total?callback=s_0&&type=4&obj_id={0}&countType=1&authorId=&_=1466496505642'.format(self.movie_dict['js_id'],)
		comment_res = proxy_request(comment_url)
		re_result = re.findall(r'("data":)(.*?)(})', comment_res.read())
		
		if re_result:
			self.info_dict['all_comments'] = re_result[0][1]
		print u'所有评论:%s' %  self.info_dict['all_comments']
		

def run_threads():

	mongo_data = db.CartoonSource.find({'source':'dmzj','url':{'$regex':'http://manhua.'}}).skip(6900)
	mongo_data = [i for i in mongo_data]
	count = 0

	for i in mongo_data:
		print i['title']
		print i['url']
		count += 1
		print u'第几个:%s' % count
		Dmzj(i, 'first').run()
		time.sleep(1)
		print '*******' * 5

run_threads()






