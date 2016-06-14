#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from configfile import *
import threading
import urllib2
import bson
from scrapy.selector import Selector
import time

data = db.DoubanTagID.find().skip(2103).limit(20)

class DoubanTV(threading.Thread):

	def __init__(self, movie_dict, flag):

		threading.Thread.__init__(self)
		self.info_dict = data_formate()
		self.movie_dict = movie_dict
		self.flag = flag
	def run(self):
		if self.flag == 'first':
			sel = self.return_info()
			if self.base_info(sel) != 'pass':
				self.info_dict.update(self.base_info(sel))
		self.info_dict.update(self.update_info(sel))
		db.TVInfo.update({'movie_url': self.info_dict['movie_url']}, {'$set': self.info_dict}, True)

	@staticmethod
	def run_threads(flag):
		threads = list()
		for i in data:
			thread_1 = DoubanTV(i, flag)
			thread_1.start()
			threads.append(thread_1)
		for t in threads:
			t.join()

	def return_info(self):
		url = self.movie_dict['url']
		response = urllib2.urlopen(url)
		return_data = response.read()
		sel = Selector(text=return_data)
		return sel

	def base_info(self, sel):
		
		#其余基本信息
		self.info_dict['source'] = 'douban'
		print u'来源:%s' % self.info_dict['source']
		self.info_dict['movie_id'] = self.movie_dict['url'].split('/')[-2]
		print u'豆瓣ID:%s' % self.info_dict['movie_id']
		self.info_dict['Relate_ID'] = self.info_dict['movie_id']
		print u'关联ID:%s' % self.info_dict['Relate_ID']

		#豆瓣电影URL
		self.info_dict['movie_url'] = self.movie_dict['url']
		print u'电影URL:%s' % self.info_dict['movie_url']

		#0 图片直接存入图片链接和将二进制流存入mongodb
		try:
			self.info_dict['img_url'] = sel.xpath('//div[@id="mainpic"]/a/img/@src').extract()[0].strip()
		except Exception, e:
			return 'pass' #感觉有bug

		print u'影片图片地址:***%s' % self.info_dict['img_url']
		self.info_dict['img_data'] = bson.Binary(urllib2.urlopen(self.info_dict['img_url']).read())
		
		#1电影名称和年份
		all_name = sel.xpath('//*[@property="v:itemreviewed"]/text()').extract()[0].strip()
		all_name_list = all_name.split(' ')
		self.info_dict['movie_name'] = all_name_list[0]
		print u'影片名称:****%s' % self.info_dict['movie_name']
		all_name_list.pop(0)
		self.info_dict['foreign_name'] = ' '.join(all_name_list)
		print u'外文名:%s' % self.info_dict['foreign_name']
		self.info_dict['movie_time'] = sel.xpath('//*[@class="year"]/text()').extract()[0].strip().split('(')[1].strip().split(')')[0].strip()
		print u'影片年份:*****%s' % self.info_dict['movie_time'] #和时光网关联标识

		#4片长
		is_runtime = sel.xpath('//*[@property="v:runtime"]')
		if is_runtime:
			is_runtime = sel.xpath('//*[@property="v:runtime"]/text()').extract()[0].strip()
			if u'分钟' in is_runtime:
				is_runtime = is_runtime.split(u'分钟')[0].strip()
			self.info_dict['runtime'] = is_runtime
		print u'片长:%s' % self.info_dict['runtime']
		
		#5/6先国家 后地区
		is_time = sel.xpath('//*[@property="v:initialReleaseDate"]')
		if is_time:
			for rt in is_time:
				release_info = rt.xpath('./text()').extract()[0].strip()
				release_date = release_info.split('(')[0].strip()
				if ('(' in release_info) and (')' in release_info):
					release_area = release_info.split('(')[1].strip().split(')')[0].strip()
				else:
					release_area = ''
				self.info_dict['release_info'].append([release_area, release_date])
				print u'上映国家:{0} 时间:{1}'.format(release_area, release_date)

		#7IMDB编号 可能没有ttid
		imdb_info = sel.xpath('//div[@id="info"]//*[@rel="nofollow"]')
		if imdb_info:
			for imdb in imdb_info:
				is_imdb = imdb.xpath('./text()').extract()[0].strip()
				if ('tt' in is_imdb) and (len(is_imdb) == 9):
					is_exist = is_imdb
			self.info_dict['IMDB_ID'] = is_exist
		print u'IMDB_编号:%s' % self.info_dict['IMDB_ID']

		#8导演
		is_director = sel.xpath('//*[@rel="v:directedBy"]')
		if is_director:
			for direc in is_director:
				director = direc.xpath('./text()').extract()[0].strip()
				if direc.xpath('./@href').extract():
					director_url = 'https://movie.douban.com' + direc.xpath('./@href').extract()[0].strip()
				else:
					director_url = ''
				director_dict = {
									'name': director,
									'url': director_url
								}
				self.info_dict['director'].append(director_dict)
				print u'导演:%s' % director

		#9主演
		is_main_actor = sel.xpath('//*[@rel="v:starring"]')
		if is_main_actor:
			for ac in is_main_actor:
				actor = ac.xpath('./text()').extract()[0].strip()
				if ac.xpath('./@href').extract():
					actor_url = 'https://movie.douban.com' + ac.xpath('./@href').extract()[0].strip()
				else:
					actor_url = ''
				actor_dict = {
								'name': actor,
								'url': actor_url
							}
				print u'主演:%s' % actor
				self.info_dict['main_actor'].append(actor_dict)

		#10编剧
		try:
			is_editor = sel.xpath('//div[@id="info"]/span[2]/span[1]/text()').extract()[0].strip()
		except Exception, e:
			is_editor = sel.xpath('//div[@id="info"]/span[2]/text()').extract()[0].strip()
		
		if is_editor == u'编剧':
			for edi in sel.xpath('//div[@id="info"]/span[2]/span[2]/a'):
				editor = edi.xpath('./text()').extract()[0].strip()
				if edi.xpath('./@href').extract():
					editor_url = 'https://movie.douban.com' + edi.xpath('./@href').extract()[0].strip()
				else:
					editor_url = ''
				editor_dict = {
								'name': editor,
								'url': editor_url
							}
				print u'编剧:%s' % editor
				self.info_dict['editor'].append(editor_dict)

		#11类型
		is_type = sel.xpath('//*[@property="v:genre"]')
		if is_type:
			for t in is_type:
				film_type = t.xpath('./text()').extract()[0].strip()
				print u'类型:%s' % film_type
				self.info_dict['film_type'].append(film_type) 

		#12影片简介
		is_introduce = sel.xpath('//*[@id="link-report"]//*[@class="all hidden"]/text()').extract()
		if is_introduce:
			self.info_dict['introduce'].extend(is_introduce)
		else:
			is_introduce = sel.xpath('//*[@id="link-report"]//*[@property="v:summary"]/text()').extract()
			if is_introduce:
				introduce= sel.xpath('//*[@id="link-report"]//*[@property="v:summary"]/text()').extract()
				self.info_dict['introduce'].extend(is_introduce)
		for i in is_introduce:
			print u'简介:%s' % i

		#13豆瓣影片标签
		is_tags = sel.xpath('//div[@class="tags"]').extract()
		if is_tags:
			tags_body = sel.xpath('//div[@class="tags-body"]/a')
			for j in tags_body:
				tag_dict = dict()
				tag_dict['tag_name'] = j.xpath('./text()').extract()[0].strip()
				tag_dict['tag_url'] = j.xpath('./@href').extract()[0].strip()
				print u'标签:******%s'  % tag_dict['tag_name']
				self.info_dict['tags'].append(tag_dict)

		return self.info_dict

	def update_info(self, sel):
		movie_id = self.movie_dict['url'].split('/')[-2]
		if sel.xpath('//*[@property="v:average"]'):
			self.info_dict['average'] = sel.xpath('//*[@property="v:average"]/text()').extract()
			if self.info_dict['average']:
				self.info_dict['average'] = sel.xpath('//*[@property="v:average"]/text()').extract()[0].strip()
				print u'豆瓣评分:%s' % self.info_dict['average']

		if sel.xpath('//*[@property="v:votes"]'):
			self.info_dict['votes'] = sel.xpath('//*[@property="v:votes"]/text()').extract()[0].strip()
			print u'评分人数:%s' % self.info_dict['votes']
		if sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/comments"]'.format(movie_id,)):
			all_short = sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/comments"]/text()'.format(movie_id,)).extract()[0].strip()
			self.info_dict['all_short'] = all_short.split(u'全部')[1].strip().split(u'条')[0].strip()
			print u'短评数量:%s' % self.info_dict['all_short']

		if sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/reviews"]'.format(movie_id,)):
			all_long = sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/reviews"]/text()'.format(movie_id,)).extract()[0].strip()
			self.info_dict['all_long'] = all_long.split(u'全部')[1].strip().split(u'条')[0].strip()
			print u'长评数量:%s' % self.info_dict['all_long']

		self.info_dict['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		print u'更新时间:%s' % self.info_dict['update_time']
		return self.info_dict

DoubanTV.run_threads('first')
















