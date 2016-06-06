#-*- coding:utf-8 -*-

import random
import urllib2
import pymongo
from scrapy.selector import Selector

client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData
get_info = db.MovieInfo.find().skip(15).limit(20)

from config_constant import *
from get_time_id import *

def proxy_request():
	proxy = urllib2.ProxyHandler(random.choice(proxy_list))
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
def search_name(name):
	
	response = urllib2.urlopen('http://search.mtime.com/search/?q=%E5%8D%A1%E9%97%A8%E8%A5%BF%E5%A1%94')
	return response.read()

# data  = search_name('Le Clown et ses chiens')
# print Selector(text=data).xpath('//*[@id="moreRegion"]/li[1]/h3/a/text()').extract()
# get_info = db.IMDB_ID.find().limit(10)
# search_name_list = [i['title'] for i in get_info]
# for j in search_name_list:
# 	pass
# 	# proxy_request()
# 	# data = search_name(j)
# 	# f = open('/Users/mac/Desktop/testhtml/%s.html' % j, 'w')
# 	# f.write(data)
# 	# f.close()
# 	# print u'查询的电影:%s' % j

# 	break
single_test = [
				'http://movie.mtime.com/11925/',
			]
movie_url_list = [
					'http://movie.mtime.com/196613/',
					'http://movie.mtime.com/164011/',
					'http://movie.mtime.com/11925/',
					'http://movie.mtime.com/216573/',
					'http://movie.mtime.com/209122/',
					'http://movie.mtime.com/134727/',
					'http://movie.mtime.com/134720/',
					'http://movie.mtime.com/134729/',
				]
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
				people_info = j.xpath('./a/text()').extract()[0].strip()
				people_url = j.xpath('./a/@href').extract()
				if people_url:
					people_url = people_url[0].strip()
				else:
					people_url = ''
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
					print u'公司:%s' % company_name
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
						print u'发行公司:%s' % sale_company_name
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
def movie_info(url, relate_id):

	time_movie_info = dict()
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
	print u'获奖记录URL:%s' % response5.url
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
	time_movie_info['movie_time_long'] = ''
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
	time_movie_info['IMDB_ID'] = ''
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
	time_movie_info['area'] = ''
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

		awards_record(sel5)

def awards_record(sel5):
	print u'奖项种类:%s' % len(sel5.xpath('//*[@id="awardInfo_data"]/dd'))
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
		print u'奖项名称:%s' % format_dict['award_category']

		if i.xpath('.//*[@class="mr15"]/a/text()').extract():
			#只得过一届的信息处理
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

					award_name = i.xpath('./dl/dd[{0}]/span/text()'.format(dd)).extract()[0].strip()
					insert_dict['award_name'] = award_name
					# print u'获奖类型:%s' % insert_dict['award_name']
					for na in i.xpath('./dl/dd[{0}]/a'.format(dd)):
						# print u'获奖者:%s' % na.xpath('./text()').extract()[0].strip()
						insert_dict['name_actor'].append(na.xpath('./text()').extract()[0].strip())
					format_dict['Won'].append(insert_dict)

				for dd1 in range(won_times + 1, won_times + 1 + nominated_times):
					# print u'dd1的值:%s' % dd1
					award_name = i.xpath('./dl/dd[{0}]/span/text()'.format(dd1)).extract()[0].strip()
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
				print u'次数:%s' % times
				is_which = i.xpath('./dl/dt/text()').extract()[0].strip()
				if is_which == u'获奖':
					won_times_list.append(times)
				else:
					nominated_times_list.append(times)

				for dd2 in i.xpath('./dl/dd'):
					insert_dict['award_name'] = dd2.xpath('./span/text()').extract()[0].strip()
					print u'种类:%s' % insert_dict['award_name']
					for ba in dd2.xpath('./a'):
						print u'人:%s' % ba.xpath('./text()').extract()[0].strip()
						insert_dict['name_actor'].append(ba.xpath('./text()').extract()[0].strip())

		else:
			format_dict['date'] = ''

		print u'哪一届:%s' % format_dict['date']

		award_nominate.append(format_dict)



#时光网内测
movie_info('http://movie.mtime.com/11925/', '123')
# for i in movie_url_list:
# 	movie_info(i, '123')
# 	print '********' * 5 


#从豆瓣到时光网
# for i in get_info:
# 	get_id = time_id(i)

# 	if get_id != 'nofind':
# 		url = 'http://movie.mtime.com/{0}/'.format(get_id)
# 		print u'时光网的URL:%s' % url
# 		movie_info(url, i['Relate_ID'])

# 	print '------' * 5

	# break














