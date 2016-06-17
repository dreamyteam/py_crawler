#-*- coding:utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from configfile import *
import threading
import urllib2
import json
import bson
from scrapy.selector import Selector
import time
import re

import random


class TimeTV(object):

	def __init__(self, movie_dict, flag):

		self.info_dict = data_formate()
		self.movie_dict = movie_dict
		self.flag = flag

	def run(self):

		if self.flag == 'first':
			time_id = self.time_id(self.movie_dict)
			if time_id != 'nofind':
				tuple_list = self.all_return_result(time_id, self.movie_dict)
				self.info_dict.update(self.movie_info(tuple_list, self.movie_dict, time_id))
				self.info_dict.update(self.awards_record(time_id))
				self.info_dict.update(self.update_other_info(time_id))
				self.info_dict['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
				print u'更新时间:%s' % self.info_dict['update_time']
				db.TVInfo.update({'movie_url': self.info_dict['movie_url']}, {'$set': self.info_dict}, True)

	#时光网搜索电影
	def search_movie(self, search_name, movie_time):

		url = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=1&i=0&c=290&t=20166612441087539&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=1&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)
		response = urllib2.urlopen(url)
		data = response.read()
		re_info = re.findall(r'(var result_1,20166612441087539 = )(.*?)(;var getSearchResult=result_1,20166612441087539;)', data)
		
		deal_data = json.loads(re_info[0][1])

		keywords = ''.join([i['value'] for i in deal_data['value']['words']])
		# print u'检索出来的关键字:%s' % keywords
		
		#检索和判断
		if 'moreMovies' in deal_data['value']['movieResult']:
			for i in deal_data['value']['movieResult']['moreMovies']:
				print i['movieTitle']
				is_in_list = list()
				is_in_other_list = list()
				for j in keywords:
					if j in i['movieTitle'].lower():
						is_in_list.append('ok')
					else:
						is_in_list.append('no')
					if j in i['titleOthers'].lower():
						is_in_other_list.append('ok')
					else:
						is_in_other_list.append('no')
				norepid_list = list(set(is_in_list))
				norepid_list_2 = list(set(is_in_other_list))
				if (len(norepid_list) == 1) and (norepid_list[0] == 'ok') and (str(movie_time) in i['movieTitle']):
				# movie_title = ''.join(i['movieTitle'].split(' '))
					return i['movieId']

				elif (len(norepid_list) != 1) and (str(movie_time) in i['movieTitle']):
					if (len(norepid_list_2) == 1) and (norepid_list_2[0] == 'ok'):
						return i['movieId']
				elif (len(norepid_list) != 1) and (str(movie_time) not in i['movieTitle']):
					if (len(norepid_list_2) == 1) and (norepid_list_2[0] == 'ok') and (str(movie_time) in i['titleOthers']):
						return i['movieId']
				# print '\n'

		return 'nomatch'

	#通过豆瓣电影名称和时间获取时光网的电影ID
	def time_id(self, movie_dict):
		name_list = movie_dict['movie_name'].split(' ')

		movie_name = '**'.join(name_list)
		print u'处理过的电影名称对比', movie_name, movie_dict['movie_time']
		result_first = self.search_movie(name_list[0].encode('utf-8'), movie_dict['movie_time'])
		
		if result_first == 'nomatch':
			name_list.pop(0)
			if name_list:
				new_search_word = '%20'.join(name_list)
				# print u'第二次检索关键词:%s' % new_search_word
				result_second = search_movie(new_search_word.encode('utf-8'), movie_dict['movie_time'])
				# print u'第二次返回的时光网ID:%s' % result_second
				if result_second == 'nomatch':
					return 'nofind'
					# print '检索不到，我去，居然没找到'
				else:
					return result_second

			else:
				# print u'暂时从时光网搜索不到或者是我太菜没检索到，改进检索算法' 
				return 'nofind'
		else:
			# print u'第一次返回的时光网ID:%s' % result_first
			return result_first

	def all_return_result(self, time_id, movie_dict):
		url = 'http://movie.mtime.com/{0}/'.format(time_id)
		try:
			all_tuple = self.request_again(url)
		except urllib2.HTTPError, e:
			time.sleep(1)
			all_tuple = self.request_again(url)
		else:
			time.sleep(1)
			all_tuple = self.request_again(url)
		return all_tuple

	#处理502再请求一遍
	def request_again(self, url):
		#影片起始页面
		response1 = urllib2.urlopen(url)
		#影片更多资料
		response2 = urllib2.urlopen(url + 'details.html') 
		#影片简介
		response3 = urllib2.urlopen(url + 'plots.html') 
		#演职人员
		response4 = urllib2.urlopen(url + 'fullcredits.html') 
		data1 = response1.read()
		data2 = response2.read()
		data3 = response3.read()
		data4 = response4.read()
		sel1 = Selector(text=data1)
		sel2 = Selector(text=data2)
		sel3 = Selector(text=data3)
		sel4 = Selector(text=data4)
		return (url, sel1, sel2, sel3, sel4)


	#影片基本信息
	def movie_info(self, tuple_list, movie_dict, time_id):
		
		update_dict = dict()
		#非请求基本信息
		update_dict['Relate_ID'] = movie_dict['Relate_ID']
		print u'三表关联的ID:%s' % update_dict['Relate_ID']
		update_dict['movie_url'] = tuple_list[0]
		print u'起始URL:%s' % update_dict['movie_url']
		update_dict['source'] = 'time'
		update_dict['movie_id'] = time_id
		print u'时光网ID:%s' % update_dict['movie_id']
		update_dict['IMDB_ID'] = movie_dict['IMDB_ID']
		print u'IMDB编号:%s' % update_dict['IMDB_ID']

		#0 电影图片
		img_url = tuple_list[1].xpath('//*[@id="db_head"]//img/@src').extract()[0].strip()
		img_data = bson.Binary(urllib2.urlopen(img_url).read())
		update_dict['img_url'] = img_url
		print u'图片链接:%s' % update_dict['img_url']
		update_dict['img_data'] = img_data

		#1 电影名称
		update_dict['movie_name'] = tuple_list[1].xpath('//*[@property="v:itemreviewed"]/text()').extract()[0].strip()
		print u'电影名称:%s' % update_dict['movie_name']

		#2 英文名称
		is_en_name = tuple_list[2].xpath('//*[@class="db_enname"]/a/text()').extract()
		update_dict['foreign_name'] = str()
		if is_en_name:
			update_dict['foreign_name'] = tuple_list[2].xpath('//*[@class="db_enname"]/a/text()').extract()[0].strip()

		print u'外文名称:%s' % update_dict['foreign_name']

		#3/5电影片长和别名
		is_exist = tuple_list[2].xpath('//*[@class="pb12"]')
		update_dict['other_name'] = list()
		if is_exist:
			if len(is_exist) == 1:
				update_dict['runtime'] = is_exist[0].xpath('./p/text()').extract()[0].strip()

			elif len(is_exist) > 1:
				for i in is_exist[:-1]:
					other_name_list = i.xpath('./p')
					for j in other_name_list:
						other_name = j.xpath('./text()').extract()[0].strip()
						update_dict['other_name'].append(other_name)
						# print u'别名:%s' % other_name

				update_dict['runtime'] = is_exist[-1].xpath('./p/text()').extract()[0].strip()

			# print u'电影片长:%s' %  update_dict['runtime']
				
		#6影片类型
		is_type = tuple_list[1].xpath('//*[@property="v:genre"]')
		update_dict['film_type'] = list()
		if is_type:
			for i in is_type:
				movie_type = i.xpath('./text()').extract()[0].strip()
				# print u'影片类型:%s' % movie_type
				update_dict['film_type'].append(movie_type)

		#7/8 简介和IMDB编号
		is_introduce = tuple_list[3].xpath('//*[@class="plots_box"]')
		update_dict['introduce'] = list()
		if is_introduce:
			for i in is_introduce:
				introduce1 = i.xpath('.//*[@class="first_letter"]/text()').extract()[0].strip()
				introduce_list = i.xpath('./div[2]//p/text()').extract()
				introduce2 = ''.join(introduce_list)
				# print u'简介:{0}{1}'.format(introduce1, introduce2)
				update_dict['introduce'].append(introduce1+introduce2)

		#10 制作国家/地区	
		is_info_l = tuple_list[1].xpath('//*[@pan="M14_Movie_Overview_BaseInfo"]')
		para_list = list()
		if is_info_l:
			for i in is_info_l:
				info_l = i.xpath('./strong/text()').extract()[0].strip()
				para_list.append(info_l)
				# print u'------{0}-----'.format(info_l,)
		is_area = self.select_contry(para_list)
		if is_area != None:
			area = tuple_list[1].xpath('//*[@pan="M14_Movie_Overview_BaseInfo"][{0}]/a/text()'.format(is_area,)).extract()[0].strip()
			update_dict['area'] = area
			# print u'制作国家和地区:%s' % update_dict['area']

		#11/12上映时间的地区
		is_release = tuple_list[2].xpath('//*[@class="db_showdate"]')
		update_dict['release_info'] = list()
		if is_release:
			release_list = is_release[0].xpath('./ul/li')
			for i in release_list[1:]:
				countryname = i.xpath('./div[1]/p/text()').extract()[0].strip()
				datecont = i.xpath('./div[2]/text()').extract()[0].strip()
				# print u'地区:{0}*****时间:{1}'.format(countryname, datecont)
				update_dict['release_info'].append([countryname, datecont])

		#13语言
		is_language = tuple_list[2].xpath('//*[@class="db_movieother_2"]/dl')
		update_dict['language'] = list()
		para_language_list = list()
		if is_language and tuple_list[2].xpath('//*[@class="pb12"]'):
			# print is_language[1].xpath('./dd')
			for i in is_language[1].xpath('./dd'):
				info_l = i.xpath('./strong/text()').extract()[0].strip()
				para_language_list.append(info_l)
		info_language = self.search_language(para_language_list)
		if info_language != None:
			# print info_language
			language_list = tuple_list[2].xpath('//*[@class="db_movieother_2"]/dl[2]/dd[{0}]/p/a'.format(info_language,))
			# print language_list
			for i in language_list:
				language = i.xpath('./text()').extract()[0].strip().split('/')[0].strip()
				# print u'对白语言:%s' % language
				update_dict['language'].append(language)

		#14导演-24武术指导
		is_all = tuple_list[4].xpath('//*[@class="credits_r"]/div')
		selector_list_info = list()
		if is_all:
			for i in is_all:
				staff_people = i.xpath('./h4/text()').extract()[0].strip()
				selector_list_info.append(staff_people)
				# print staff_people

		add_staff_info = self.staff_info(tuple_list[4], staff_list, selector_list_info)
		# for x in update_info:
		# 	print update_info[x]
		# 	print '\n'
		update_dict.update(add_staff_info)

		#27制作公司/28发行公司
		if tuple_list[2].xpath('//*[@id="companyRegion"]'):
			update_dict.update(self.company_type(tuple_list[2]))

		#28主演/29饰演角色
		is_actor = tuple_list[4].xpath('//*[@class="db_actor"]/dl')
		update_dict['actor_charactor'] = list()
		if is_actor:
			for i in is_actor:
				for j in i.xpath('./dd'):
					actor = j.xpath('.//*[@class="actor_tit"]//h3/a/text()').extract()
					if actor:
						actor = j.xpath('.//*[@class="actor_tit"]//h3/a/text()').extract()[0].strip()
						if j.xpath('.//*[@class="actor_tit"]//h3/a/@href').extract():
							actor_url = j.xpath('.//*[@class="actor_tit"]//h3/a/@href').extract()[0].strip()
						else:
							actor_url = str()
					else:
						actor = str()


					actor_dict = {
									'name': actor,
									'url': actor_url,
								}

					charactor = j.xpath('.//*[@class="character_inner"]//h3/a/text() | .//*[@class="character_inner"]//h3/text()').extract()
					if charactor:
						charactor = j.xpath('.//*[@class="character_inner"]//h3/a/text() | .//*[@class="character_inner"]//h3/text()').extract()[0].strip()
					else:
						charactor = ''
					# print u'演员:{0}\t\t角色:{1}'.format(actor, charactor)
					update_dict['actor_charactor'].append([actor_dict, charactor])
		return update_dict

	#判断制作国家和地区
	def select_contry(self, para_list):
		if u'国家地区：' in para_list:
			index_info = para_list.index(u'国家地区：') + 1
			return index_info
		else:
			return None

	#判断对白语言
	def search_language(self, para_language_list):
		if u'对白语言：' in para_language_list:
			index_info = para_language_list.index(u'对白语言：' ) + 1
			return index_info
		else:
			return None

	#时光网的所有演职员信息
	def staff_info(self, sel4, staff_list_info, selector_list_info):
		update_dict = dict()
		for i in staff_list_info:
			new_info_list = list()
			if staff_list[i] in selector_list_info:
				index_info = selector_list_info.index(staff_list[i]) + 1

				for j in sel4.xpath('//*[@class="credits_r"]/div[{0}]/p'.format(index_info,)):
					
					people_info = j.xpath('./a/text()').extract()
					if people_info:
						people_info = people_info[0].strip()
					else:
						people_info = str()
					people_url = j.xpath('./a/@href').extract()
					if people_url:
						people_url = people_url[0].strip()
					else:
						people_url = str()
					insert_dict = {
									'name': people_info,
									'url': people_url,
								}
					# print u'{0}:{1}'.format(staff_list[i], people_info)
					new_info_list.append(insert_dict)
				update_dict[i] = new_info_list
		return update_dict

	#制作公司和发行公司
	def company_type(self, sel2):
		company_list = list()
		distributors_list = list()
		add_dict = dict()
		if len(sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div')) <= 2:
			if sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div[1]/ul/li'):
				for i in sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div[1]/ul/li'):
						company_name = i.xpath('./a/text()').extract()[0].strip()
						if i.xpath('./a/@href').extract():
							company_url = i.xpath('./a/@href').extract()[0].strip()
						else:
							company_url = ''
						product_dict = {
										'name': company_name,
										'url': company_url,
									}
						# print u'公司:%s' % company_name
						company_list.append(product_dict)

				if sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div[1]/h4/text()').extract()[0].strip() == u'制作公司':
					add_dict['production_company'] = company_list
					return add_dict
					if sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div[2]/h4/text()'):
						for i in sel2.xpath('//*[@id="companyRegion"]/dd/div[1]/div[2]/ul/li'):
							sale_company_name = i.xpath('./a/text()').extract()[0].strip()
							if i.xpath('./a/@href').extract():
								sale_company_url = i.xpath('./a/@href').extract()[0].strip()
							else:
								sale_company_url = ''
							# print u'发行公司:%s' % sale_company_name
							sale_dict = {
											'name': sale_company_name,
											'url': sale_company_url,
										}
							distributors_list.append(sale_dict)
						add_dict['distributors'] = distributors_list
						return add_dict
				else:
					add_dict['distributors'] = company_list
					return add_dict

	#获奖和提名记录还有次数属于更新
	def awards_record(self, time_id):
		update_dict = dict()
		url = 'http://movie.mtime.com/{0}/awards.html'.format(time_id)
		# if random.choice(request_list) == 'no':
		try:
			get_return = urllib2.urlopen(url) #获奖记录
		except urllib2.HTTPError, e:
			time.sleep(1)
			get_return = urllib2.urlopen(url) #再请求一次
		else:
			time.sleep(1)
			get_return = urllib2.urlopen(url) #请求2.0
		# else:
		# 	get_return = proxy_request(url)

		#29获奖记录 30提名
		if get_return.url == 'http://www.mtime.com/404.html':
			
			update_dict['award_nominate'] = list()
			return update_dict['award_nominate']
		else:
			sel5 = Selector(text=get_return.read())
			# print u'奖项种类:%s' % len(sel5.xpath('//*[@id="awardInfo_data"]/dd'))
			
			won_times_list = list()
			nominated_times_list = list()
			award_nominate = list()

			for i in sel5.xpath('//*[@id="awardInfo_data"]/dd'):

				format_dict = {
								'date': '',
								'award_body': '',
								'award_category': '',
								'Won': [],
								'Nominated': [],
								'2nd place': [],
								'3rd place': [],
							}

				both_name = i.xpath('./h3/b/text()').extract()[0].strip()
				format_dict['award_body'] = both_name
				format_dict['award_category'] = both_name
				# print u'奖项名称:%s' % format_dict['award_category']
				#只得过一届的信息处理
				if i.xpath('.//*[@class="mr15"]/a/text()').extract():
					format_dict['date'] = i.xpath('.//*[@class="mr15"]/a/text()').extract()[0].strip()
					#提名获奖都有
					if  len(i.xpath('./h3/text()').extract()) == 5:
						won_times = int(i.xpath('./h3/strong[1]/text()').extract()[0].strip())
						# print u'获奖次数:%s' % won_times
						nominated_times = int(i.xpath('./h3/strong[2]/text()').extract()[0].strip())
						# print u'提名次数:%s' % nominated_times
						won_times_list.append(won_times)
						nominated_times_list.append(nominated_times)
						insert_dict = {
											'award_name': '',
											'name_actor': [],
									}

						for dd in range(1, won_times + 1):

							award_name = i.xpath('./dl/dd[{0}]/span/text()'.format(dd)).extract()
							if award_name:
								award_name = i.xpath('./dl/dd[{0}]/span/text()'.format(dd)).extract()[0].strip()
							else:
								award_name = str()
							insert_dict['award_name'] = award_name
							# print u'获奖类型:%s' % insert_dict['award_name']
							for na in i.xpath('./dl/dd[{0}]/a'.format(dd)):
								# print u'获奖者:%s' % na.xpath('./text()').extract()[0].strip()
								insert_dict['name_actor'].append(na.xpath('./text()').extract()[0].strip())
							# print u'演员列表是否有:%s' % insert_dict['name_actor']
							format_dict['Won'].append(insert_dict)

						for dd1 in range(won_times + 1, won_times + 1 + nominated_times):
							# print u'dd1的值:%s' % dd1
							if i.xpath('./dl/dd[{0}]/span/text()'.format(dd1)).extract():
								award_name = i.xpath('./dl/dd[{0}]/span/text()'.format(dd1)).extract()[0].strip()
							else:
								award_name = str()
							insert_dict['award_name'] = award_name
							# print u'提名项:%s' % insert_dict['award_name']

							for na in i.xpath('./dl/dd[{0}]/a'.format(dd1)):
								# print i.xpath('./dl/dd[{0}]/a'.format(dd1))
								# print u'提名者:%s' % na.xpath('./text()').extract()[0].strip()
								insert_dict['name_actor'].append(na.xpath('./text()').extract()[0].strip())
							format_dict['Nominated'].append(insert_dict)
					elif len(i.xpath('./h3/text()').extract()) == 4:
						insert_dict = {
											'award_name': '',
											'name_actor': [],
									}
						times = int(i.xpath('./h3/strong/text()').extract()[0].strip())
						# print u'次数:%s' % times

						for dd2 in i.xpath('./dl/dd'):
							is_award_name = dd2.xpath('./span/text()').extract()
							if is_award_name:
								insert_dict['award_name'] = dd2.xpath('./span/text()').extract()[0].strip()
							else:
								insert_dict['award_name'] = str()

							# print u'种类:%s' % insert_dict['award_name']
							for ba in dd2.xpath('./a'):
								# print u'人:%s' % ba.xpath('./text()').extract()[0].strip()
								insert_dict['name_actor'].append(ba.xpath('./text()').extract()[0].strip())
						is_which = i.xpath('./dl/dt/text()').extract()[0].strip()

						if is_which == u'获奖':
							won_times_list.append(times)
							format_dict['Won'].append(insert_dict)
						else:
							nominated_times_list.append(times)
							format_dict['Nominated'].append(insert_dict)
						# print u'获奖还是提名:%s' % is_which

				#获得过多届
				else:
					#历届获奖或者提名次数
					many_list = [t.xpath('./text()').extract()[0].strip() for t in i.xpath('./h3/strong')]
					if len(many_list) == 2:
						won_times_list.append(int(many_list[0]))
						# print u'获奖次数:%s' % many_list[0]
						nominated_times_list.append(int(many_list[1]))
						# print u'提名次数:%s' % many_list[1]

					else:
						for l in i.xpath('./h3/text()').extract():
							if '\t' not in l:
								if l == u' 获奖：':
									won_times_list.append(int(i.xpath('./h3/strong/text()').extract()[0].strip()))
								else:
									nominated_times_list.append(int(i.xpath('./h3/strong/text()').extract()[0].strip()))
					#历届信息(具体信息的获取)
					for each in i.xpath('./dl//*[@style="font-size: 20px;"]'):
						format_dict = dict()
						format_dict['2nd place'] = list()
						format_dict['3rd place'] = list()
						format_dict['Won'] = list()
						format_dict['Nominated'] = list()
						format_dict['award_body'] = both_name
						format_dict['award_category'] = both_name
						# print u'多届的奖项种类:%s' % format_dict['award_body']
						format_dict['date'] = each.xpath('./a/text()').extract()[0].strip()
						# print u'多届的中的哪一届:*****%s' % format_dict['date']

				# print u'哪一届:%s' % format_dict['date']
				award_nominate.append(format_dict)

			update_dict['nominations'] = sum(nominated_times_list)
			update_dict['wins'] = sum(won_times_list)
			update_dict['award_nominate'] = award_nominate
			
			return update_dict


	#其余更新部分
	def update_other_info(self, time_get_id):
		update_dict = dict()
		url = 'http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetMovieOverviewRating&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%2F{0}%2F&t=2016671225976913&Ajax_CallBackArgument0={1}'.format(time_get_id, time_get_id)
		
		try:
			get_return = urllib2.urlopen(url).read()
		except urllib2.HTTPError, e:
			time.sleep(1)
			get_return = urllib2.urlopen(url).read()
		else:
			time.sleep(1)
			get_return = urllib2.urlopen(url).read()
		# else:
		# print u'返回结果:%s'% response.code
		# data = (response.read())
			# get_return = proxy_request(url).read()
		# print data
		re_info = re.findall(r'(var result_2016671225976913 = )(.*?)(;var movieOverviewRatingResult=result_2016671225976913;)', get_return)
		# print re_info[0][1]
		json_data = json.loads(re_info[0][1])
		if json_data['value'] == None:
			update_dict['average'] = 0
			update_dict['votes'] = 0
			update_dict['rank'] = 0
		else:
			if 'movieRating' in json_data['value']:
				update_dict['average'] = json_data['value']['movieRating']['RatingFinal']
				update_dict['votes'] = json_data['value']['movieRating']['Usercount']
				if 'topList' in json_data['value']:
					update_dict['rank'] = json_data['value']['topList']['Ranking']
				else:
					update_dict['rank'] = 0
			else:
				update_dict['average'] = 0
				update_dict['votes'] = 0
				update_dict['rank'] = 0


		print u'评分:%s' % update_dict['average']
		print u'评分人数:%s' % update_dict['votes']
		print u'排名:%s' % update_dict['rank']
		comment_url = 'http://movie.mtime.com/{0}/comment.html'.format(time_get_id,)
		sel = Selector(text=urllib2.urlopen(comment_url).read())
		if sel.xpath('//*[@class="details_nav"]/ul/li[1]/a/text()').extract():
			long_comment = sel.xpath('//*[@class="details_nav"]/ul/li[1]/a/text()').extract()[0].strip().split('(')[1].split(')')[0].strip()
			short_comment = sel.xpath('//*[@class="details_nav"]/ul/li[2]/a/text()').extract()[0].strip().split('(')[1].split(')')[0].strip()
		
		else:
			new_comment_url = 'http://movie.mtime.com/{0}/reviews/short/hot.html'.format(time_get_id,)
			sel = Selector(text=urllib2.urlopen(new_comment_url).read())
			if sel.xpath('//*[@class="details_nav"]/ul/li[1]/a/text()').extract():
				long_comment = sel.xpath('//*[@class="details_nav"]/ul/li[1]/a/text()').extract()[0].strip().split('(')[1].split(')')[0].strip()
				short_comment = sel.xpath('//*[@class="details_nav"]/ul/li[2]/a/text()').extract()[0].strip().split('(')[1].split(')')[0].strip()
			else:
				long_comment = str()
				short_comment = str()
		print u'长影评:%s' % long_comment
		print u'短影评:%s' % short_comment
		news_url = 'http://movie.mtime.com/{0}/'.format(time_get_id,)
		sel1 = Selector(text=urllib2.urlopen(news_url).read())
		news_times = sel1.xpath('//*[@token="RelatedNews"]/a/span/text()').extract()[0].strip()
		print u'新闻数量:%s' % news_times
		update_dict['all_long'] = long_comment
		update_dict['all_short'] = short_comment
		update_dict['all_news'] = news_times
		
		return update_dict
		
def run_threads():

	data_info = db.TVInfo.find({'source': 'douban'}).skip(1147).limit(500)
	count = 0
	for i in data_info:
		count += 1
		print u'第几个:%s' % count
		TimeTV(i, 'first').run()
		time.sleep(4)
		print '-------' * 5

run_threads()





