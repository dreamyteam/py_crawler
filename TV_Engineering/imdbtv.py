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
import re


data = db.TVInfo.find({'source': 'douban'}).skip(10).limit(2)

class ImdbTV(threading.Thread):

	def __init__(self, movie_dict, flag):

		threading.Thread.__init__(self)
		self.info_dict = data_formate()
		self.movie_dict = movie_dict
		self.flag = flag
	def run(self):
		if self.flag == 'first':
			all_sel = self.all_return_body()
			#基本信息
			self.imdb_info(all_sel[0], all_sel[1])
			# 上映时间和别名
			self.info_dict.update(self.release_info(all_sel[2]))
			for i in self.info_dict['release_info']:
				print u'地区:', i[0], '\t', u'时间:', i[1]
			for i in self.info_dict['other_name']:
				print u'别名:%s' % i

			#制作公司和发行公司
			self.info_dict.update(self.company_info(all_sel[3]))
			#演职员信息
			self.info_dict.update(self.cast_info(all_sel[4]))

		#更新信息
		self.info_dict.update(self.update_info(self.movie_dict['IMDB_ID']))


	@staticmethod
	def run_threads(flag):
		threads = list()
		for i in data:
			if i['IMDB_ID']:
				thread_1 = ImdbTV(i, flag)
				thread_1.start()
				threads.append(thread_1)

		for t in threads:
			t.join()

	def all_return_body(self):
		ttid = self.movie_dict['IMDB_ID']
		#基本信息页面
		url1 = 'http://www.imdb.com/title/{0}/'.format(ttid,)
		sel1 = Selector(text=urllib2.urlopen(url1).read())
		#上映信息页面
		url2 = 'http://www.imdb.com/title/{0}/releaseinfo'.format(ttid,)
		sel2 = Selector(text=urllib2.urlopen(url2).read())
		#制作公司和发行公司
		url3 = 'http://www.imdb.com/title/{0}/companycredits'.format(ttid,)
		sel3 = Selector(text=urllib2.urlopen(url3).read())
		#职员
		url4 = 'http://www.imdb.com/title/{0}/fullcredits'.format(ttid,)
		sel4 = Selector(text=urllib2.urlopen(url4).read())
		return (url1, sel1, sel2, sel3, sel4)

	def imdb_info(self, url, sel):

		#基本其余信息
		self.info_dict['Relate_ID'] = self.movie_dict['Relate_ID']
		print u'关联ID:%s' % self.info_dict['Relate_ID'] 
		self.info_dict['source'] = 'IMDB'
		#IMDB编号
		self.info_dict['IMDB_ID'] = self.movie_dict['IMDB_ID']
		print u'IMDB编号:%s' % self.info_dict['IMDB_ID']
		self.info_dict['movie_url'] = url
		print u'IMDB起始URL:%s' % self.info_dict['movie_url']
		self.info_dict['movie_id'] = self.movie_dict['IMDB_ID']
		print u'IMDB的movie_id:%s' % self.info_dict['movie_id']

		#0图片
		if sel.xpath('//*[@class="poster"]//*[@itemprop="image"]/@src').extract():
			self.info_dict['img_url'] = sel.xpath('//*[@class="poster"]//*[@itemprop="image"]/@src').extract()[0].strip()
			print u'图片链接:%s' % self.info_dict['img_url']

			#图片二进制流
			self.info_dict['img_data'] = bson.Binary(urllib2.urlopen(self.info_dict['img_url']).read()) 

		#1影片名称 2外文名称
		self.info_dict['movie_name'] = sel.xpath('//*[@class="title_wrapper"]//*[@itemprop="name"]/text()').extract()[0].strip()
		self.info_dict['foreign_name'] = self.info_dict['movie_name']
		print u'影片名称:%s' % self.info_dict['movie_name']

		#3语言 4片长
		self.info_dict.update(self.get_info(sel))
		for i in self.info_dict['language']:
			print u'语言:%s' % i
		print u'片长:%s' % self.info_dict['runtime']

		#简介/类型风格
		storyline = sel.xpath('//*[@id="titleStoryLine"]/h2/text()')
		self.info_dict['introduce'] = list()
		if storyline:
			if sel.xpath('//*[@id="titleStoryLine"]//*[@itemprop="description"]/p/text()').extract():
				description = sel.xpath('//*[@id="titleStoryLine"]//*[@itemprop="description"]/p/text()').extract()[0].strip()
			else:
				description = ''
			print u'简介:%s' % description
			print '\n'
			self.info_dict['introduce'].append(description)

		if sel.xpath('//*[@itemprop="genre"]/text()').extract():
			for i in sel.xpath('//*[@itemprop="genre"]'):
				is_type = i.xpath('./text()').extract()[0].strip()
				if is_type:
					self.info_dict['film_type'].append(is_type)
					print is_type
		
		# db.MovieInfo.update({'movie_url': self.info_dict['movie_url']}, {'$set': info_dict}, True)

	#判断对白语言/片长/
	def get_info(self, sel):

		is_detail = sel.xpath('//*[@id="titleDetails"]//*[@class="txt-block"]')
		index_list = list()

		if is_detail:
			for i in is_detail:
				is_h4 = i.xpath('./h4/text()').extract()
				if is_h4:
					index_list.append(i.xpath('./h4/text()').extract()[0].strip())
				else:
					index_list.append(i.xpath('./text()').extract()[0].strip())
			if 'Language:' in index_list :
				language_index = index_list.index('Language:') + 1
				for j in sel.xpath('//*[@id="titleDetails"]//*[@class="txt-block"][{0}]/a'.format(language_index,)):
					self.info_dict['language'].append(j.xpath('./text()').extract()[0].strip())
			if 'Runtime:' in index_list:
				runtime_index = index_list.index('Runtime:') + 1
				self.info_dict['runtime'] = sel.xpath('//*[@id="titleDetails"]//*[@class="txt-block"][{0}]//*[@itemprop="duration"]/text()'.format(runtime_index,)).extract()[0].strip()

		return self.info_dict

	#上映时间和别名
	def release_info(self, sel):

		is_release = sel.xpath('//*[@id="release_dates"]')

		if is_release:
			for i in sel.xpath('//*[@id="release_dates"]/tr'):
				release_area = i.xpath('./td[1]/a/text()').extract()[0].strip()
				release_date1 = i.xpath('.//*[@class="release_date"]/text()').extract()[0].strip()
				release_date2 = i.xpath('.//*[@class="release_date"]/a/text()').extract()[0].strip()
				release_date = release_date1 + '\t' + release_date2
				self.info_dict['release_info'].append([release_area, release_date])
		#别名
		is_other = sel.xpath('//*[@id="akas"]')

		if is_other:
			for i in sel.xpath('//*[@id="akas"]/tr'):
				other_name = i.xpath('./td[2]/text()').extract()[0].strip()
				self.info_dict['other_name'].append(other_name)


		return self.info_dict

	#制作公司和发行公司
	def company_info(self, sel):

		is_production = sel.xpath('//*[@id="production"]')

		if is_production:
			for i in sel.xpath('//*[@id="company_credits_content"]/ul[1]/li'):
				company = i.xpath('./a/text()').extract()[0].strip()
				company_url = 'http://www.imdb.com' + i.xpath('./a/@href').extract()[0].strip()
				company_dict = {
								'name': company,
								'url': company_url,
							}
				print u'制作公司:%s' % company
				self.info_dict['production_company'].append(company_dict)

		is_distributors = sel.xpath('//*[@id="distributors"]')

		if is_distributors:
			for i in sel.xpath('//*[@id="company_credits_content"]/ul[2]/li'):
				name = i.xpath('./a/text()').extract()[0].strip()
				name_url = 'http://www.imdb.com' + i.xpath('./a/@href').extract()[0].strip()
				print u'发行公司:%s' % name
				distributors_dict = {
										'name': name,
										'url': name_url
									}
				self.info_dict['distributors'].append(distributors_dict)

		return self.info_dict

	#职员
	def cast_info(self, sel):

		staff_tag = list()

		for i in sel.xpath('//*[@id="fullcredits_content"]/h4'):
			staff_tag.append(i.xpath('./text()').extract()[0].strip())
			# print i.xpath('./text()').extract()[0].strip()

		for j in IMDB_staff_list:
			add_list = list()
			if IMDB_staff_list[j] in staff_tag:
				# print u'存在的标签:%s' % IMDB_staff_list[j]
				index_info = staff_tag.index(IMDB_staff_list[j]) + 1
				# print u'索引:%s' % index_info
				# print sel.xpath('//*[@id="fullcredits_content"]/table[{0}]/tbody/tr'.format(index_info,))
				for z in sel.xpath('//*[@id="fullcredits_content"]/table[{0}]/tbody/tr'.format(index_info,)):
					# print u'执行了？'
					if z.xpath('.//*[@class="name"]'):
						staff_name = z.xpath('.//*[@class="name"]/a/text()').extract()[0].strip()
						if z.xpath('.//*[@class="name"]/a/@href'):
							staff_name_url = 'http://www.imdb.com' + z.xpath('.//*[@class="name"]/a/@href').extract()[0].strip()
						else:
							staff_name_url = ''
						staff_dict = { 
										'name': staff_name,
										'url': staff_name_url
									}

						print u'名称:{0}\t 名字:{1}'.format(IMDB_staff_list[j], staff_name)
						add_list.append(staff_dict)

			self.info_dict[j] = add_list


		#演员信息
		actor_charactor = list()
		if sel.xpath('//*[@class="cast_list"]'):
			for i in sel.xpath('//*[@class="cast_list"]/tr')[1:]:
				if i.xpath('.//*[@itemprop="actor"]/a/span'):
					actor = i.xpath('.//*[@itemprop="actor"]/a/span/text()').extract()[0].strip()
					if i.xpath('.//*[@itemprop="actor"]/a/@href').extract():
						actor_url = i.xpath('.//*[@itemprop="actor"]/a/@href').extract()[0].strip()
					else:
						actor_url = ''
					actor_dict = {
									'name': actor,
									'url': actor_url
								}
					print u'演员:%s' % actor
					character = ''
					if i.xpath('.//*[@class="character"]'):
						if i.xpath('.//*[@class="character"]/div/a'):
							character = i.xpath('.//*[@class="character"]/div/a/text()').extract()[0].strip()
						elif i.xpath('.//*[@class="character"]/div'):
							character = i.xpath('.//*[@class="character"]/div/text()').extract()[0].strip()
						print u'角色:%s' % character
					actor_charactor.append([actor_dict, character])
		self.info_dict['actor_charactor'] = actor_charactor
		
		return self.info_dict


	#更新部分
	def update_info(self, ttid):

		#获奖提名记录
		url = 'http://www.imdb.com/title/{0}/awards'.format(ttid,)
		print u'获奖的URL:%s' % url
		sel = Selector(text=urllib2.urlopen(url).read())
		url2 = 'http://www.imdb.com/title/{0}/'.format(ttid,)
		sel2 = Selector(text=urllib2.urlopen(url2).read())
		if sel.xpath('//*[@class="desc"]'):
			#次数
			r = sel.xpath('//*[@class="desc"]/text()').extract()[0].strip().split(' ')
			
			if 'wins' in r:

				self.info_dict['wins'] = int(r[r.index('wins')-1])

			if ('nominations' in r) or ('nomination' in r):
				try:
					self.info_dict['nominations'] = int(r[r.index('nominations')-1])
				except Exception, e:
					self.info_dict['nominations'] = int(r[r.index('nomination')-1])

		print u'获奖：{0}****提名：{1}'.format(self.info_dict['wins'], self.info_dict['nominations'])

		#信息
		all_award_body = sel.xpath('//*[@class="article listo"]/h3')
		all_info = sel.xpath('//*[@class="article listo"]/table')
		award_nominate = list()
		for i in range(1,len(all_award_body)+1):
			format_dict = {
							'date': '',
							'award_body': '',
							'award_category': '',
							'Won': [],
							'Nominated': [],
							'2nd place': [],
							'3rd place': [],
						}
			won_list = list()
			nomination_list = list()
			format_dict['date'] = sel.xpath('//*[@class="article listo"]/h3[{0}]/a/text()'.format(i,)).extract()[0].strip()
			# print u'年份:%s' % format_dict['date']
			format_dict['award_body'] = sel.xpath('//*[@class="article listo"]/h3[{0}]/text()'.format(i,)).extract()[0].strip()
			# print u'机构:%s' % format_dict['award_body']
			
			# for j in sel.xpath('//*[@class="article listo"]/table[{0}]/tr'.format(i,)):
			# 	is_len = j.xpath('.//*[@class="title_award_outcome"]')
			# 	print u'获奖和提名:%s' % is_len
			is_len = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"]'.format(i,))
			
			if len(is_len) == 1:

				add_name = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"]/span/text()'.format(i,)).extract()[0].strip()
				format_dict['award_category'] = add_name
				# print add_name
				#提名还是获奖
				is_which = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"]/b/text()'.format(i,)).extract()[0].strip()
				# print is_which
				for j in sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_description"]'.format(i,)):
				
					name = j.xpath('./text()').extract()[0].strip()
					name_actor_list = j.xpath('./a')

					name_actor = list()
					if name_actor_list:
						for z in name_actor_list:
							name_actor.append(z.xpath('./text()').extract()[0].strip())
					
					insert_dict = {
									'award_name': name,
									'name_actor': name_actor,
								}
					# print u'提名还是获奖:%s' % is_which
					# print u'奖项:%s' % name
					# print u'获奖者:%s' % name_actor
					format_dict[is_which].append(insert_dict)
					
			elif len(is_len) == 2:
				# print u'有执行么'
				format_dict['award_category'] = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_category"]/text()'.format(i,)).extract()[0].strip()
				
				rowspan_list = list()
				for j in sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"]'.format(i,)):
					rowspan_list.append(j.xpath('./@rowspan').extract()[0].strip())

				# print u'列表各自的奖项数目与:%s' % rowspan_list	
				is_which1 = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"][1]/b/text()'.format(i,)).extract()[0].strip()
				# print is_which1
				is_which2 = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="title_award_outcome"][2]/b/text()'.format(i,)).extract()[0].strip()
				# print is_which2
				#第一项
				for x in range(1, int(rowspan_list[0]) + 1):
					
					name = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_description"][{1}]/text()'.format(i, x)).extract()[0].strip()
					print u'第一项名称:%s' % name
					name_actor_list = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_description"][{1}]/a'.format(i, x))
					name_actor = list()
					if name_actor_list:
						for y in name_actor_list:
							name_actor.append(y.xpath('./text()').extract()[0].strip())

						insert_dict = {
										'award_times': name,
										'name_actor': name_actor
									}
						format_dict[is_which1].append(insert_dict)	

				#第二项
				for x in range(int(rowspan_list[0]) + 1, int(rowspan_list[0]) + 1 + int(rowspan_list[1])):
					name = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_description"][{1}]/text()'.format(i, x)).extract()[0].strip()
					print u'第二项名称:%s' % name
					name_actor_list = sel.xpath('//*[@class="article listo"]/table[{0}]//*[@class="award_description"][{1}]/a'.format(i, x))
					name_actor = list()
					if name_actor_list:
						for y in name_actor_list:
							name_actor.append(y.xpath('./text()').extract()[0].strip())
						insert_dict = {
										'award_times': name,
										'name_actor': name_actor
									}
						format_dict[is_which2].append(insert_dict)
			award_nominate.append(format_dict)
		self.info_dict['award_nominate'] = award_nominate

		if sel2.xpath('//*[@itemprop="ratingValue"]/text()').extract():	
			self.info_dict['average'] = sel2.xpath('//*[@itemprop="ratingValue"]/text()').extract()[0].strip()
		
		print u'IMDB评分:%s' % self.info_dict['average']
		
		if sel2.xpath('//*[@itemprop="ratingCount"]/text()').extract():

			votes = sel2.xpath('//*[@itemprop="ratingCount"]/text()').extract()[0].strip()
			
			p = re.compile("\d+,\d+?")
			for com in p.finditer(votes):
				mm = com.group()
				votes = votes.replace(mm, mm.replace(",", ""))
			votes = int(votes)
			self.info_dict['votes'] = votes 
		
		print u'评分人数:%s' % self.info_dict['votes']

		all_long = sel2.xpath('//*[@href="externalreviews?ref_=tt_ov_rt"]/text()').extract()
		# print all_long
		if all_long:
			
			all_long = all_long[0].strip()
			self.info_dict['all_long'] = int(all_long.split('critic')[0].strip())

		print u'长评人数:%s' % self.info_dict['all_long']
		

		rank_list = sel2.xpath('//*[@class="titleReviewBarSubItem"]')
		rank = 0
		if rank_list:
			for i in rank_list:
				if i.xpath('./div/text()').extract():
					if i.xpath('./div/text()').extract()[0].strip() == 'Popularity':
						rank = i.xpath('.//*[@class="subText"]/text()').extract()[0].strip('(').strip()
						p = re.compile("\d+,\d+?")
						for com in p.finditer(rank):
							mm = com.group()
							rank = rank.replace(mm, mm.replace(",", ""))
						rank = int(rank)
						print u'排名:%s' % rank

		self.info_dict['rank'] = rank
		self.info_dict['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
		return self.info_dict



ImdbTV.run_threads('update')






