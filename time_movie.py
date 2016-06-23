#-*- coding:utf-8 -*-

import random
import urllib2
import pymongo
from scrapy.selector import Selector

client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData
get_info = db.MovieInfo.find().skip(831).limit(100)

from config_constant import *
from get_time_id import *
import re
import json
import time


#判断制作国家和地区
def select_contry(para_list):
	if u'国家地区：' in para_list:
		index_info = para_list.index(u'国家地区：') + 1
		return index_info
	else:
		return None
#判断对白语言
def search_language(para_language_list):
	if u'对白语言：' in para_language_list:
		index_info = para_language_list.index(u'对白语言：' ) + 1
		return index_info
	else:
		return None

#时光网的所有演职员信息
def staff_info(sel4,staff_list_info, selector_list_info):
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
def company_type(sel2):
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

#影片基本信息
import bson
def movie_info(url, relate_id, time_get_id, imdb_id):

	time_movie_info = data_formate()
	time_movie_info['Relate_ID'] = relate_id
	print u'三表关联的ID:%s' % time_movie_info['Relate_ID']
	time_movie_info['movie_url'] = url
	time_movie_info['source'] = 'time'
	time_movie_info['movie_id'] = url.split('/')[-2]
	response = urllib2.urlopen(url) #影片起始页面
	response2 = urllib2.urlopen(url + 'details.html') #影片更多资料
	response3 = urllib2.urlopen(url + 'plots.html') #影片简介
	response4 = urllib2.urlopen(url + 'fullcredits.html') #演职人员
	response5 = urllib2.urlopen(url + 'awards.html') #获奖记录
	print u'更多资料URL:%s' % response.url
	# print u'获奖记录URL:%s' % response5.url
	data = response.read()
	data2 = response2.read()
	data3 = response3.read()
	data4 = response4.read()
	data5 = response5.read()
	# print u'状态码:%s' % response5.code
	sel = Selector(text=data)
	sel2 = Selector(text=data2)
	sel3 = Selector(text=data3)
	sel4 = Selector(text=data4)
	sel5 = Selector(text=data5)
	#0 电影图片
	img_url = sel.xpath('//*[@id="db_head"]//img/@src').extract()[0].strip()
	img_response = urllib2.urlopen(img_url)
	img_data = bson.Binary(img_response.read())
	time_movie_info['img_url'] = img_url
	print u'图片链接:%s' % time_movie_info['img_url']
	time_movie_info['img_data'] = img_data
	#1 电影名称
	movie_name = sel.xpath('//*[@property="v:itemreviewed"]/text()').extract()[0].strip()
	time_movie_info['movie_name'] = movie_name
	print u'电影名称:%s' % time_movie_info['movie_name']
	#2 英文名称
	is_en_name = sel2.xpath('//*[@class="db_enname"]/a/text()').extract()
	time_movie_info['foreign_name'] = ''
	if is_en_name:
		en_name = sel2.xpath('//*[@class="db_enname"]/a/text()').extract()[0].strip()
		time_movie_info['foreign_name'] = en_name

	# print u'外文名称:%s' % time_movie_info['foreign_name']
	#3/5电影片长和别名
	is_exist = sel2.xpath('//*[@class="pb12"]')
	time_movie_info['other_name'] = list()
	time_movie_info['runtime'] = ''
	if is_exist:
		if len(is_exist) == 1:
			movie_time_long = is_exist[0].xpath('./p/text()').extract()[0].strip()
			time_movie_info['runtime'] = movie_time_long
			# print u'电影片长:%s' %  time_movie_info['runtime']

		elif len(is_exist) > 1:
			for i in is_exist[:-1]:
				other_name_list = i.xpath('./p')
				for j in other_name_list:
					other_name = j.xpath('./text()').extract()[0].strip()
					time_movie_info['other_name'].append(other_name)
					# print u'别名:%s' % other_name

			movie_time_long = is_exist[-1].xpath('./p/text()').extract()[0].strip()
			time_movie_info['runtime'] = movie_time_long
			# print u'电影片长:%s' %  time_movie_info['movie_time_long']
			# print u'别名列表:%s' % time_movie_info['other_name']
	#6影片类型
	is_type = sel.xpath('//*[@property="v:genre"]')
	time_movie_info['film_type'] = list()
	if is_type:
		for i in is_type:
			movie_type = i.xpath('./text()').extract()[0].strip()
			# print u'影片类型:%s' % movie_type
			time_movie_info['film_type'].append(movie_type)
	# print u'影片类型列表:%s' % time_movie_info['film_type']
	#7/8 简介和IMDB编号
	time_movie_info['IMDB_ID'] = imdb_id
	time_movie_info['introduce'] = list()
	is_introduce = sel3.xpath('//*[@class="plots_box"]')
	if is_introduce:
		for i in is_introduce:
			introduce1 = i.xpath('.//*[@class="first_letter"]/text()').extract()[0].strip()
			introduce_list = i.xpath('./div[2]//p/text()').extract()
			introduce2 = ''.join(introduce_list)
			# print u'简介:{0}{1}'.format(introduce1, introduce2)
			time_movie_info['introduce'].append(introduce1+introduce2)
		# print u'简介列表:%s' % time_movie_info['introduce']

	#10 制作国家/地区	
	is_info_l = sel.xpath('//*[@pan="M14_Movie_Overview_BaseInfo"]')
	para_list = list()
	if is_info_l:
		for i in is_info_l:
			info_l = i.xpath('./strong/text()').extract()[0].strip()
			para_list.append(info_l)
			# print u'------{0}-----'.format(info_l,)
	is_area = select_contry(para_list)
	if is_area != None:
		area = sel.xpath('//*[@pan="M14_Movie_Overview_BaseInfo"][{0}]/a/text()'.format(is_area,)).extract()[0].strip()
		time_movie_info['area'] = area
		# print u'制作国家和地区:%s' % time_movie_info['area']

	#11/12上映时间的地区
	is_release = sel2.xpath('//*[@class="db_showdate"]')
	time_movie_info['release_time_area'] = list()
	if is_release:
		release_list = is_release[0].xpath('./ul/li')
		for i in release_list[1:]:
			countryname = i.xpath('./div[1]/p/text()').extract()[0].strip()
			datecont = i.xpath('./div[2]/text()').extract()[0].strip()
			# print u'{0}*****{1}'.format(countryname, datecont)
			save_list = [countryname, datecont]
			time_movie_info['release_time_area'].append(save_list)

	#13语言
	is_language = sel2.xpath('//*[@class="db_movieother_2"]/dl')
	time_movie_info['language'] = list()
	para_language_list = list()
	if is_language and sel2.xpath('//*[@class="pb12"]'):
		# print is_language[1].xpath('./dd')
		for i in is_language[1].xpath('./dd'):
			info_l = i.xpath('./strong/text()').extract()[0].strip()
			para_language_list.append(info_l)
	# print para_language_list
	info_language = search_language(para_language_list)

	if info_language != None:
		# print info_language
		language_list = sel2.xpath('//*[@class="db_movieother_2"]/dl[2]/dd[{0}]/p/a'.format(info_language,))
		# print language_list
		for i in language_list:
			language = i.xpath('./text()').extract()[0].strip().split('/')[0].strip()
			# print u'对白语言:%s' % language
			time_movie_info['language'].append(language)

	#14导演-24武术指导
	is_all = sel4.xpath('//*[@class="credits_r"]/div')
	selector_list_info = list()
	if is_all:
		for i in is_all:
			staff_people = i.xpath('./h4/text()').extract()[0].strip()
			selector_list_info.append(staff_people)
			# print staff_people

	update_info = staff_info(sel4, staff_list, selector_list_info)
	# for x in update_info:
	# 	print update_info[x]
	# 	print '\n'
	time_movie_info.update(update_info)

	#27制作公司/28发行公司
	if sel2.xpath('//*[@id="companyRegion"]'):
		time_movie_info.update(company_type(sel2))
	else:
		time_movie_info['production_company'] = list()
		time_movie_info['distributors'] = list()
	#28主演/29饰演角色
	is_actor = sel4.xpath('//*[@class="db_actor"]/dl')
	time_movie_info['actor_charactor'] = list()

	if is_actor:
		for i in is_actor:
			for j in i.xpath('./dd'):
				actor = j.xpath('.//*[@class="actor_tit"]//h3/a/text()').extract()[0].strip()
				if j.xpath('.//*[@class="actor_tit"]//h3/a/@href').extract():
					actor_url = j.xpath('.//*[@class="actor_tit"]//h3/a/@href').extract()[0].strip()
				else:
					actor_url = ''
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
				time_movie_info['actor_charactor'].append([actor_dict, charactor])

	#29获奖记录 30提名
	if response5.url == 'http://www.mtime.com/404.html':
		time_movie_info['award_nominate'] = list()

	else:
		time_movie_info.update(awards_record(sel5))

	#其余更新部分
	time_movie_info.update(update_other_info(time_get_id))
	db.MovieInfo.update({'movie_url': url}, {'$set': time_movie_info}, True)

#获奖和提名记录还有次数属于更新
def awards_record(sel5):
	# print u'奖项种类:%s' % len(sel5.xpath('//*[@id="awardInfo_data"]/dd'))
	update_dict = dict()
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
def update_other_info(time_get_id):
	update_dict = dict()
	url = 'http://service.library.mtime.com/Movie.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Library.Services&Ajax_CallBackMethod=GetMovieOverviewRating&Ajax_CrossDomain=1&Ajax_RequestUrl=http%3A%2F%2Fmovie.mtime.com%2F{0}%2F&t=2016671225976913&Ajax_CallBackArgument0={1}'.format(time_get_id, time_get_id)
	response = urllib2.urlopen(url)
	# print u'返回结果:%s'% response.code
	data = (response.read())
	# print data
	re_info = re.findall(r'(var result_2016671225976913 = )(.*?)(;var movieOverviewRatingResult=result_2016671225976913;)', data)
	# print re_info[0][1]
	json_data = json.loads(re_info[0][1])
	if json_data['value'] == None:
		update_dict['average'] = 0
		update_dict['votes'] = 0
		update_dict['rank'] = 0
	else:
		update_dict['average'] = json_data['value']['movieRating']['RatingFinal']
		update_dict['votes'] = json_data['value']['movieRating']['Usercount']
		if 'topList' in json_data['value']:
			update_dict['rank'] = json_data['value']['topList']['Ranking']
		else:
			update_dict['rank'] = 0
		
	print u'评分:%s' % update_dict['average']
	# print u'评分人数:%s' % update_dict['votes']
	# print u'排名:%s' % update_dict['rank']
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
	# print u'长影评:%s' % long_comment
	# print u'短影评:%s' % short_comment
	news_url = 'http://movie.mtime.com/{0}/'.format(time_get_id,)
	sel1 = Selector(text=urllib2.urlopen(news_url).read())
	news_times = sel1.xpath('//*[@token="RelatedNews"]/a/span/text()').extract()[0].strip()
	# print u'新闻数量:%s' % news_times
	update_dict['all_long'] = long_comment
	update_dict['all_short'] = short_comment
	update_dict['all_news'] = news_times
	return update_dict
	
#时光网单测
# movie_info('http://movie.mtime.com/228521/', '123', 228521, '111')
# for i in movie_url_list:
# 	movie_info(i, '123')
# 	print '********' * 5 


#从豆瓣到时光网
count = 0
for i in get_info:
	time.sleep(2)
	count += 1
	print u'第几个:%s' % count
	get_id = time_id(i)

	if get_id != 'nofind':
		url = 'http://movie.mtime.com/{0}/'.format(get_id)
		print u'时光网的URL:%s' % url
		movie_info(url, i['Relate_ID'], get_id, i['IMDB_ID'])
		# break
# 	print '------' * 5
















