#-*- coding:utf-8 -*-

'''将IMDB_ID中的豆瓣链接读取，抓取豆瓣中有的信息'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


import pymongo
# client = pymongo.MongoClient('112.74.106.159', 27017)
# db = client.MovieData

import urllib2
import random
from scrapy.selector import Selector
from config_constant import *
import bson

def proxy_request():
	proxy = urllib2.ProxyHandler(random.choice(proxy_list))
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)



# data = db.IMDB_ID.find().limit(20)

list1 = [
			'https://movie.douban.com/subject/10437779/', 
		]

list2 = [	
			'https://movie.douban.com/subject/10437779/',
			'https://movie.douban.com/subject/25820460/',
			'https://movie.douban.com/subject/2131940/',
			'https://movie.douban.com/subject/1421095/',
			'https://movie.douban.com/subject/26366465/',
			'https://movie.douban.com/subject/5205593/',
		]

#一次性数据部分
for i in list1:
	# print u'电影URL:%s' % i['movie_url']
	proxy_request()
	# response = urllib2.urlopen(i['movie_url'])
	response = urllib2.urlopen(i)
	html_data = response.read()
	info_dict = dict()
	sel = Selector(text=html_data)
	#豆瓣电影url
	info_dict['douban_movie_url'] = i
	#0
	info_dict['movie_pic_url'] = sel.xpath('//div[@id="mainpic"]/a/img/@src').extract()[0].strip()
	print u'影片图片地址:%s' % info_dict['movie_pic_url']
	#1
	info_dict['movie_name'] = sel.xpath('//*[@property="v:itemreviewed"]/text()').extract()[0].strip()
	print u'影片名称:%s' % info_dict['movie_name']
	info_dict['movie_time'] = sel.xpath('//*[@class="year"]/text()').extract()[0].strip()
	print u'影片年份:%s' % info_dict['movie_time']
	#13
	is_tags = sel.xpath('//div[@class="tags"]').extract()
	info_dict['tags'] = list()
	if is_tags:
		tags_body = sel.xpath('//div[@class="tags-body"]/a')
		tags_list = list()
		for j in tags_body:
			tag = j.xpath('./text()').extract()[0].strip()
			print u'标签:%s'  %tag
			info_dict['tags'].append(tag)

	# print u'标签列表:%s' % info_dict['tags']
	#12
	is_introduce = sel.xpath('//*[@id="link-report"]/span[1]/text()').extract()
	info_dict['introduce'] = ''
	if is_introduce:
		info_dict['introduce'] = sel.xpath('//*[@id="link-report"]/span[1]/text()').extract()[0].strip()
	
	# print u'影片简介:%s' % info_dict['introduce']
	#9
	is_actor = sel.xpath('//*[@rel="v:starring"]')
	info_dict['main_actor'] = list()
	if is_actor:
		for ac in is_actor:
			actor = ac.xpath('./text()').extract()[0].strip()
			print u'主演:%s' % actor
			info_dict['main_actor'].append(actor)

	# print u'主演列表:%s' % info_dict['main_actor']

	#8
	is_director = sel.xpath('//*[@rel="v:directedBy"]')
	info_dict['director'] = list()
	if is_director:
		for direc in is_director:
			director = direc.xpath('./text()').extract()[0].strip()
			info_dict['director'].append(director)
			print u'导演:%s' % director
	# print u'导演列表:%s' % info_dict['director']
	#10
	try:
		is_editor = sel.xpath('//div[@id="info"]/span[2]/span[1]/text()').extract()[0].strip()
	except Exception, e:
		is_editor = sel.xpath('//div[@id="info"]/span[2]/text()').extract()[0].strip()
	
	
	info_dict['editor'] = list()
	if is_editor == u'编剧':
		
		for edi in sel.xpath('//div[@id="info"]/span[2]/span[2]/a'):
			editor = edi.xpath('./text()').extract()[0].strip()
			print u'编剧:%s' % editor
			info_dict['editor'].append(editor)
	# print u'编剧列表:%s' % info_dict['editor']

	#11
	is_type = sel.xpath('//*[@property="v:genre"]')
	info_dict['type_type'] = list()
	if is_type:
		for t in is_type:
			type_type = t.xpath('./text()').extract()[0].strip()
			print u'类型:%s' % type_type
			info_dict['type_type'].append(type_type) 
	# print u'类型列表:%s' % info_dict['type_type']

	#5/6
	is_time = sel.xpath('//*[@property="v:initialReleaseDate"]')
	info_dict['release_time_area'] = list()

	if is_time:
		for rt in is_time:
			release_time = rt.xpath('./text()').extract()[0].strip()
			info_dict['release_time_area'].append(release_time)
			print u'上映时间:%s' % release_time

	# print u'上映时间和地区列表:%s' % info_dict['release_time_area']

	#7
	imdb_info = sel.xpath('//div[@id="info"]//*[@rel="nofollow"]')
	for imdb in imdb_info:
		imdb_id = imdb.xpath('./text()').extract()[0].strip()
		if ('tt' in imdb_id) and (len(imdb_id) == 9):
			info_dict['imdb_id'] = imdb_id
			print u'IMDB_编号:%s' % imdb_id
	#0 图片直接存入图片链接和将二进制流存入mongodb
	img_url = sel.xpath('//*[@id="mainpic"]/a/img/@src').extract()[0].strip()
	img_response = urllib2.urlopen(img_url)
	img_data = bson.Binary(img_response.read())
	info_dict['img_url'] = img_url
	print u'图片链接:%s' % img_url
	info_dict['img_data'] = img_data
	print '----------' * 8


def check_cn_en():
	pass

	




















