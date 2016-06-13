#-*- coding:utf-8 -*-

'''将IMDB_ID中的豆瓣链接读取，抓取豆瓣中有的信息'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

import urllib2
import json
import random
from scrapy.selector import Selector
from config_constant import *
import bson
import time
data = db.DoubanTagID.find().skip(2100)

request_list = ['proxy', 'no']

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

def base_info(sel, url):

	info_dict = dict()

	#豆瓣电影url
	info_dict['movie_url'] = url
	print u'电影URL:**%s' % info_dict['movie_url']
	#0 图片直接存入图片链接和将二进制流存入mongodb
	try:
		info_dict['img_url'] = sel.xpath('//div[@id="mainpic"]/a/img/@src').extract()[0].strip()
	except Exception, e:
		return 'pass'
	# info_dict['img_url'] = sel.xpath('//div[@id="mainpic"]/a/img/@src').extract()[0].strip()
	# print u'影片图片地址:***%s' % info_dict['img_url']

	info_dict['img_data'] = bson.Binary(urllib2.urlopen(info_dict['img_url']).read())

	#1电影名称和年份
	info_dict['movie_name'] = sel.xpath('//*[@property="v:itemreviewed"]/text()').extract()[0].strip()
	print u'影片名称:****%s' % info_dict['movie_name']
	info_dict['movie_time'] = sel.xpath('//*[@class="year"]/text()').extract()[0].strip().split('(')[1].strip().split(')')[0].strip()
	# print u'影片年份:*****%s' % info_dict['movie_time'] #和时光网关联标识

	#13豆瓣影片标签
	is_tags = sel.xpath('//div[@class="tags"]').extract()
	info_dict['tags'] = list()
	if is_tags:
		tags_body = sel.xpath('//div[@class="tags-body"]/a')
		tags_list = list()
		for j in tags_body:
			tag = j.xpath('./text()').extract()[0].strip()
			# print u'标签:******%s'  %tag
			info_dict['tags'].append(tag)

	#12影片简介
	
	info_dict['introduce'] = list()
	
	is_introduce = sel.xpath('//*[@id="link-report"]//*[@class="all hidden"]/text()').extract()
	if is_introduce:
		info_dict['introduce'].extend(is_introduce)
	else:
		is_introduce = sel.xpath('//*[@id="link-report"]//*[@property="v:summary"]/text()').extract()
		if is_introduce:
			introduce= sel.xpath('//*[@id="link-report"]//*[@property="v:summary"]/text()').extract()
			info_dict['introduce'].extend(is_introduce)
	for i in is_introduce:
		print i



	#9主演
	is_main_actor = sel.xpath('//*[@rel="v:starring"]')
	info_dict['main_actor'] = list()
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
			info_dict['main_actor'].append(actor_dict)

	#8导演
	is_director = sel.xpath('//*[@rel="v:directedBy"]')
	info_dict['director'] = list()
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
			info_dict['director'].append(director_dict)
			print u'导演:%s' % director

	#10编剧
	try:
		is_editor = sel.xpath('//div[@id="info"]/span[2]/span[1]/text()').extract()[0].strip()
	except Exception, e:
		is_editor = sel.xpath('//div[@id="info"]/span[2]/text()').extract()[0].strip()
	
	info_dict['editor'] = list()
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
			info_dict['editor'].append(editor_dict)

	# print u'编剧列表:%s' % info_dict['editor']

	#11类型
	is_type = sel.xpath('//*[@property="v:genre"]')
	info_dict['film_type'] = list()
	if is_type:
		for t in is_type:
			film_type = t.xpath('./text()').extract()[0].strip()
			print u'类型:%s' % film_type
			info_dict['film_type'].append(film_type) 

	#5/6先国家 后地区
	is_time = sel.xpath('//*[@property="v:initialReleaseDate"]')
	info_dict['release_time_area'] = list()
	if is_time:
		for rt in is_time:
			release_info = rt.xpath('./text()').extract()[0].strip()
			release_date = release_info.split('(')[0].strip()
			if ('(' in release_info) and (')' in release_info):
				release_area = release_info.split('(')[1].strip().split(')')[0].strip()
			else:
				release_area = ''
			info_dict['release_time_area'].append([release_area, release_date])
			print u'上映国家:{0} 时间:{1}'.format(release_area, release_date)

	#7IMDB编号 可能没有ttid
	imdb_info = sel.xpath('//div[@id="info"]//*[@rel="nofollow"]')
	is_exist = ''
	if imdb_info:
		for imdb in imdb_info:
			is_imdb = imdb.xpath('./text()').extract()[0].strip()
			if ('tt' in is_imdb) and (len(is_imdb) == 9):
				is_exist = is_imdb
		info_dict['IMDB_ID'] = is_exist
	else:

		info_dict['IMDB_ID'] = is_exist

	print u'IMDB_编号:%s' % info_dict['IMDB_ID']


	#4片长
	is_runtime = sel.xpath('//*[@property="v:runtime"]')
	info_dict['runtime'] = ''
	if is_runtime:
		is_runtime = sel.xpath('//*[@property="v:runtime"]/text()').extract()[0].strip()
		if u'分钟' in is_runtime:
			is_runtime = is_runtime.split(u'分钟')[0].strip()
		info_dict['runtime'] = is_runtime
	print u'片长:%s' % info_dict['runtime']
	#剩余信息
	zero_dict = {
					'production_company': [],
					'distributors': [],
					'other_name': [],
					'language': [],
					'foreign_name': [],
					'produce_by': [],
					'film_enditing': [],
					'music': [],
					'art_design': [],
					'cloth_design': [],
					'Visual_Effects_Supervisor': [],
					'Choreographer': [],
					'Cinematography': [],
					'award_record': [],
					'nominate_record': [],
					'actor_charactor': [],
				}
	info_dict.update(zero_dict)
	return info_dict

def update_info(sel, url):

	movie_id = url.split('/')[-2]
	# print u'电影id:%s' % movie_id

	info_dict = dict()
	info_dict['movie_id'] = movie_id
	info_dict['Relate_ID'] = movie_id
	info_dict['average'] = '' 
	info_dict['votes'] = ''
	info_dict['all_short'] = '' 
	info_dict['all_long'] = ''
	if sel.xpath('//*[@property="v:average"]'):
		info_dict['average'] = sel.xpath('//*[@property="v:average"]/text()').extract()
		if info_dict['average']:
			info_dict['average'] = sel.xpath('//*[@property="v:average"]/text()').extract()[0].strip()
		else:
			info_dict['average'] = ''
	if sel.xpath('//*[@property="v:votes"]'):
		info_dict['votes'] = sel.xpath('//*[@property="v:votes"]/text()').extract()[0].strip()

	if sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/comments"]'.format(movie_id,)):
		all_short = sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/comments"]/text()'.format(movie_id,)).extract()[0].strip()
		info_dict['all_short'] = all_short.split(u'全部')[1].strip().split(u'条')[0].strip()
	if sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/reviews"]'.format(movie_id,)):
		all_long = sel.xpath('//*[@href="https://movie.douban.com/subject/{0}/reviews"]/text()'.format(movie_id,)).extract()[0].strip()
		info_dict['all_long'] = all_long.split(u'全部')[1].strip().split(u'条')[0].strip()
	# print info_dict['average'],'\n', info_dict['votes'], info_dict['all_short'], info_dict['all_long']
	info_dict['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
	return info_dict

def return_info(url):
	if random.choice(request_list) == 'proxy':
		html_data = proxy_request(url)
	else:
		html_data = no_proxy(url)
	sel = Selector(text=html_data)

	dict_1 = base_info(sel, url)
	if dict_1 != 'pass':
		dict_2 = update_info(sel, url)
	else:
		return 'pass'

	return (dict_1, dict_2)

#go go go 
def run(data):
	for i in data:
		time.sleep(random.random())
		save_data = return_info(i['url'])
		if save_data == 'pass':
			pass
		else:
		# print save_data[0]
		# print save_data[1]
			save_data[0].update(save_data[1])
			save_data[0]['source'] = 'douban'
			# db.MovieInfoData.update({'_id': save_data[0]['movie_id']}, {'$set': save_data[0]}, True)

run(data)




















