#-*- coding:utf-8 -*-

import urllib2
import random
from scrapy.selector import Selector
from config_constant import *
import bson


import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

def proxy_request():
	proxy = urllib2.ProxyHandler(random.choice(proxy_list))
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)

ttid_list = [
				'tt2625030',
				'tt3381008',
				'tt2948356',
				'tt2404233',
				'tt4417522',
			]

import bson
def imdb_info(ttid):
	response = urllib2.urlopen('http://www.imdb.com/title/{0}/'.format(ttid,))
	print u'当前的URL:%s' % response.url
	data = response.read()
	sel = Selector(text=data)
	mongo_dict = dict()
	#0图片
	img_url = sel.xpath('//*[@class="poster"]//*[@itemprop="image"]/@src').extract()[0].strip()
	print u'图片链接:%s' % img_url
	# img_response = urllib2.urlopen(img_url).read()
	# img_data = bson.Binary(img_response) #影片图片数据
	#1影片名称 2外文名称
	movie_name = sel.xpath('//*[@class="title_wrapper"]//*[@itemprop="name"]/text()').extract()[0].strip()
	print u'影片名称:%s' % movie_name
	#3语言 4片长
	info_dict = get_info(sel)

	for i in info_dict['language']:
		print u'语言:%s' % i
	print u'片长:%s' % info_dict['runtime']
	#上映时间和别名
	# release_info(ttid)
	#制作公司和发行公司
	# company_info(ttid)
	#IMDB编号
	print u'IMDB编号:%s' % ttid
	#演职员信息
	cast_info(ttid)
	#简介/类型风格
	storyline = sel.xpath('//*[@id="titleStoryLine"]/h2/text()')
	if storyline:
		description = sel.xpath('//*[@id="titleStoryLine"]//*[@itemprop="description"]/p/text()').extract()[0].strip()
		print u'简介:%s' % description

	if sel.xpath('//*[@itemprop="genre"]'):
		pass


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
			print u'地区:{0}\t时间:{1}'.format(release_area, release_date)
			release_list.append([release_area, release_date])
	#别名
	is_other = sel.xpath('//*[@id="akas"]')
	othername_list = list()
	if is_other:
		for i in sel.xpath('//*[@id="akas"]/tr'):
			other_name = i.xpath('./td[2]/text()').extract()[0].strip()
			print u'别名:%s' % other_name
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
			name = i.xpath('./a/text()').extract()[0].strip()
			print u'制作公司:%s' % name
			production_company.append(name)
	is_distributors = sel.xpath('//*[@id="distributors"]')
	distributors_list = list()
	if is_distributors:
		for i in sel.xpath('//*[@id="company_credits_content"]/ul[2]/li'):
			name = i.xpath('./a/text()').extract()[0].strip()
			print u'发行公司:%s' % name
			distributors_list.append(name)
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
			print u'存在的标签:%s' % IMDB_staff_list[j]
			index_info = staff_tag.index(IMDB_staff_list[j]) + 1
			# print u'索引:%s' % index_info
			# print sel.xpath('//*[@id="fullcredits_content"]/table[{0}]/tbody/tr'.format(index_info,))
			for z in sel.xpath('//*[@id="fullcredits_content"]/table[{0}]/tbody/tr'.format(index_info,)):
				# print u'执行了？'
				if z.xpath('.//*[@class="name"]'):
					staff_name = z.xpath('.//*[@class="name"]/a/text()').extract()[0].strip()
					print u'名称:{0}\t 名字:{1}'.format(IMDB_staff_list[j], staff_name)
					add_list.append(staff_name)
	#演员信息
	actor_charactor = list()
	if sel.xpath('//*[@class="cast_list"]'):

		for i in sel.xpath('//*[@class="cast_list"]/tr')[1:]:
			if i.xpath('.//*[@itemprop="actor"]/a/span'):
				actor = i.xpath('.//*[@itemprop="actor"]/a/span/text()').extract()[0].strip()
				print u'演员:%s' % actor
				character = ''
				if i.xpath('.//*[@class="character"]/div'):
					character = i.xpath('.//*[@class="character"]/div/text()').extract()[0].strip()
					print u'角色:%s' % character
				actor_charactor.append([actor, character])
	update_dict['actor_charactor'] = actor_charactor

	return update_dict




for i in ttid_list:
	imdb_info(i)
	print '-------'*8
	# break







