#-*- coding:utf-8 -*-

import urllib2
import random
from scrapy.selector import Selector
from config_constant import *
import bson
import re

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData
proxy_list = ['proxy', 'no']
def proxy_request(url):
	request = urllib2.Request(url)
	proxy = urllib2.ProxyHandler(
									{
										'http': 'http://127.0.0.1:8123',
										'https': 'https://127.0.0.1:8123',
									}
								)
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)

	return opener.open(request).read()

def no_proxy(url):
	response = urllib2.urlopen(url)
	return  response.read()

def return_info(ttid):
	url = 'http://www.imdb.com/title/{0}/'.format(ttid,)
	if random.choice(proxy_list) == 'proxy':
		html_data = proxy_request(url)
	else:
		html_data = no_proxy(url)
	sel = Selector(text=html_data)




def imdb_info(ttid, relate_id):

	response = urllib2.urlopen('http://www.imdb.com/title/{0}/'.format(ttid,))
	movie_url = response.url
	print u'当前的URL:%s' % movie_url
	data = response.read()
	sel = Selector(text=data)

	info_dict = dict()


	info_dict['Relate_ID'] = relate_id
	info_dict['source'] = 'IMDB'
	info_dict['movie_url'] = movie_url
	info_dict['movie_id'] = ttid
	#0图片
	if sel.xpath('//*[@class="poster"]//*[@itemprop="image"]/@src').extract():
		info_dict['img_url'] = sel.xpath('//*[@class="poster"]//*[@itemprop="image"]/@src').extract()[0].strip()
		print u'图片链接:%s' % info_dict['img_url']
		img_response = urllib2.urlopen(info_dict['img_url']).read()
		info_dict['img_data'] = bson.Binary(img_response) #影片图片数据
	else:
		info_dict['img_url'] = ''
		info_dict['img_data'] = ''
	#1影片名称 2外文名称
	info_dict['movie_name'] = sel.xpath('//*[@class="title_wrapper"]//*[@itemprop="name"]/text()').extract()[0].strip()
	print u'影片名称:%s' % info_dict['movie_name']
	info_dict['foreign_name'] = info_dict['movie_name']
	#3语言 4片长
	info_dict.update(get_info(sel))
	# # for i in info_dict['language']:
	# # 	print u'语言:%s' % i
	# print u'片长:%s' % info_dict['runtime']

	# # 上映时间和别名
	info_dict.update(release_info(ttid))
	# # for i in info_dict['release_info']:
	# # 	print i[0], '\t', i[1]
	# # for i in info_dict['other_name']:
	# 	# print u'别名:%s' % i
	# #制作公司和发行公司
	info_dict.update(company_info(ttid))
	# #IMDB编号
	info_dict['IMDB_ID'] = ttid
	# print u'IMDB编号:%s' % info_dict['IMDB_ID']
	# #演职员信息
	info_dict.update(cast_info(ttid))

	# #简介/类型风格
	storyline = sel.xpath('//*[@id="titleStoryLine"]/h2/text()')
	info_dict['introduce'] = list()
	if storyline:
		if sel.xpath('//*[@id="titleStoryLine"]//*[@itemprop="description"]/p/text()').extract():
			description = sel.xpath('//*[@id="titleStoryLine"]//*[@itemprop="description"]/p/text()').extract()[0].strip()
		else:
			description = ''
		# print u'简介:%s' % description
		# print '\n'
		info_dict['introduce'].append(description)
	info_dict['film_type'] = list()
	if sel.xpath('//*[@itemprop="genre"]/text()').extract():
		for i in sel.xpath('//*[@itemprop="genre"]'):
			is_type = i.xpath('./text()').extract()[0].strip()
			if is_type:
				info_dict['film_type'].append(is_type)
				# print is_type
	#更新信息
	info_dict.update(update_info(ttid, sel))
	# print info_dict

	db.MovieInfo.update({'movie_url': info_dict['movie_url']}, {'$set': info_dict}, True)

#判断对白语言/片长/
def get_info(sel):
	is_detail = sel.xpath('//*[@id="titleDetails"]//*[@class="txt-block"]')
	info_dict = dict()
	index_list = list()
	language_list = list()
	runtime = ''
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
				language_list.append(j.xpath('./text()').extract()[0].strip())
		if 'Runtime:' in index_list:
			runtime_index = index_list.index('Runtime:') + 1
			runtime = sel.xpath('//*[@id="titleDetails"]//*[@class="txt-block"][{0}]//*[@itemprop="duration"]/text()'.format(runtime_index,)).extract()[0].strip()
		info_dict['language'] = language_list
		info_dict['runtime'] = runtime
	return info_dict

#上映时间和别名
def release_info(ttid):
	response = urllib2.urlopen('http://www.imdb.com/title/{0}/releaseinfo'.format(ttid,))
	#上映时间
	data = response.read()
	sel = Selector(text=data)
	info_dict = dict()
	is_release = sel.xpath('//*[@id="release_dates"]')
	release_list = list()
	if is_release:
		for i in sel.xpath('//*[@id="release_dates"]/tr'):
			release_area = i.xpath('./td[1]/a/text()').extract()[0].strip()
			release_date1 = i.xpath('.//*[@class="release_date"]/text()').extract()[0].strip()
			release_date2 = i.xpath('.//*[@class="release_date"]/a/text()').extract()[0].strip()
			release_date = release_date1 + '\t' + release_date2
			# print u'地区:{0}\t时间:{1}'.format(release_area, release_date)
			release_list.append([release_area, release_date])
	#别名
	is_other = sel.xpath('//*[@id="akas"]')
	othername_list = list()
	if is_other:
		for i in sel.xpath('//*[@id="akas"]/tr'):
			other_name = i.xpath('./td[2]/text()').extract()[0].strip()
			# print u'别名:%s' % other_name
			othername_list.append(other_name)
	info_dict['release_info'] = release_list
	info_dict['other_name'] = othername_list
	return info_dict

#制作公司和发行公司
def company_info(ttid):
	response = urllib2.urlopen('http://www.imdb.com/title/{0}/companycredits'.format(ttid,))
	data = response.read()
	sel = Selector(text=data)
	is_production = sel.xpath('//*[@id="production"]')
	info_dict = dict()
	production_company = list()
	if is_production:
		for i in sel.xpath('//*[@id="company_credits_content"]/ul[1]/li'):
			company = i.xpath('./a/text()').extract()[0].strip()
			company_url = 'http://www.imdb.com' + i.xpath('./a/@href').extract()[0].strip()
			company_dict = {
							'name': company,
							'url': company_url,
						}
			# print u'制作公司:%s' % name
			production_company.append(company_dict)
	is_distributors = sel.xpath('//*[@id="distributors"]')
	distributors_list = list()
	if is_distributors:
		for i in sel.xpath('//*[@id="company_credits_content"]/ul[2]/li'):
			name = i.xpath('./a/text()').extract()[0].strip()
			name_url = 'http://www.imdb.com' + i.xpath('./a/@href').extract()[0].strip()
			# print u'发行公司:%s' % name
			distributors_dict = {
									'name': name,
									'url': name_url
								}
			distributors_list.append(distributors_dict)
	info_dict['production_company'] = production_company
	info_dict['distributors'] = distributors_list
	return info_dict
#职员
def cast_info(ttid):
	response = urllib2.urlopen('http://www.imdb.com/title/{0}/fullcredits'.format(ttid,))
	data = response.read()
	sel = Selector(text=data)
	staff_tag = list()
	update_dict = dict()
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

					# print u'名称:{0}\t 名字:{1}'.format(IMDB_staff_list[j], staff_name)
					add_list.append(staff_dict)
		update_dict[j] = add_list


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
				# print u'演员:%s' % actor
				character = ''
				if i.xpath('.//*[@class="character"]'):
					if i.xpath('.//*[@class="character"]/div/a'):
						character = i.xpath('.//*[@class="character"]/div/a/text()').extract()[0].strip()
					elif i.xpath('.//*[@class="character"]/div'):
						character = i.xpath('.//*[@class="character"]/div/text()').extract()[0].strip()
					# print u'角色:%s' % character
				actor_charactor.append([actor_dict, character])
	update_dict['actor_charactor'] = actor_charactor
	
	return update_dict

# #更新部分
def update_info(ttid, sel2):
	update_dict = dict()
	#获奖提名记录
	url = 'http://www.imdb.com/title/{0}/awards'.format(ttid,)
	sel = Selector(text=urllib2.urlopen(url).read())
	award_times = 0
	nominate_times = 0
	if sel.xpath('//*[@class="desc"]'):
		#次数
		r = sel.xpath('//*[@class="desc"]/text()').extract()[0].strip().split(' ')
		
		if 'wins' in r:
			award_times = int(r[r.index('wins')-1])
		if ('nominations' in r) or ('nomination' in r):
			try:
				nominate_times = int(r[r.index('nominations')-1])
			except Exception, e:
				nominate_times = int(r[r.index('nomination')-1])
	update_dict['wins'] = award_times
	update_dict['nominations'] = nominate_times
	# print u'{0}****{1}'.format(award_times, nominate_times)

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
				# print u'第一项名称:%s' % name
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
				# print u'第二项名称:%s' % name
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
	update_dict['award_nominate'] = award_nominate
	if sel2.xpath('//*[@itemprop="ratingValue"]/text()').extract():	
		average = sel2.xpath('//*[@itemprop="ratingValue"]/text()').extract()[0].strip()
	else:
		average = ''
	# print u'IMDB评分:%s' % average
	update_dict['average'] = average
	if sel2.xpath('//*[@itemprop="ratingCount"]/text()').extract():
		votes = sel2.xpath('//*[@itemprop="ratingCount"]/text()').extract()[0].strip()
		
		p = re.compile("\d+,\d+?")
		for com in p.finditer(votes):
			mm = com.group()
			votes = votes.replace(mm, mm.replace(",", ""))
		votes = int(votes)
	else:
		votes = 0
	update_dict['votes'] = votes
	# print u'人数:%s' % votes
	all_long = sel2.xpath('//*[@href="externalreviews?ref_=tt_ov_rt"]/text()').extract()
	# print all_long
	if all_long:
		# print u'执行了？'
		all_long = all_long[0].strip()
	else:
		all_long = 0
	# print u'长评人数:%s' % all_long
	
	update_dict['all_long'] = all_long
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
					# print u'排名:%s' % rank

	update_dict['rank'] = rank
	update_dict['all_short'] = 0
	return update_dict

get_douban_info = db.MovieInfo.find({'source': 'douban'}).skip(1639).limit(61)
count_index = 0
for i in get_douban_info:
	count_index += 1
	print u'第几个:%s' % count_index
	if i['IMDB_ID']:
		imdb_info(i['IMDB_ID'], i['Relate_ID'])
	print '-------' * 5






