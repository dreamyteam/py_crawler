#-*- coding:utf-8 -*-

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

import urllib2
import json
import re
import time
from scrapy.selector import Selector
from config_constant import *

def human_info(time_id):
	url = 'http://people.mtime.com/{0}/'.format(time_id)
	url2 = url + 'details.html'
	response = urllib2.urlopen(url2)
	data = response.read()
	sel = Selector(text=data)
	human_info_dict = human_info_format()
	name_list = list()
	for i in sel.xpath('//*[@class="per_header"]//*[@href="http://people.mtime.com/{0}/"]'.format(time_id)):
		name_list.append(i.xpath('./text()').extract()[0].strip())
		# print i.xpath('./text()').extract()[0].strip()
	human_info_dict['cn_name'] = name_list[0]
	print u'中文名:%s' % human_info_dict['cn_name']
	if len(name_list) > 1:
		human_info_dict['en_name'] = name_list[1]	
		print u'英文名:%s' % human_info_dict['en_name']

	#其余基本信息
	other_base_info = sel.xpath('//*[@class="per_info_cont"]/dt')
	info_list = list()
	for i in other_base_info:
		info_list.append(i.xpath('./strong/text()').extract()[0].strip())
		print u'***%s' % i.xpath('./strong/text()').extract()[0].strip()

	for i in time_human_info_dict:
		for j in other_base_info:
			if j.xpath('./strong/text()').extract()[0].strip() == time_human_info_dict[i]:
				if j.xpath('./text()').extract():
					human_info_dict[i] = j.xpath('./text()').extract()[0].strip()
					print i, human_info_dict[i]

	# other_info_list = list()
	# other_info = sel.xpath('//*[@class="per_info_cont"]/dd')

	# if other_info:
	# 	for i in other_info:
	# 		other_info_list.append(i.xpath('./text()').extract()[0].strip())

	# one_to_one_list = info_list[-len(other_info_list):]

	# for i in range(0, len(other_info_list)):
	# 	print one_to_one_list[i]
	# 	for j in time_human_info_dict:
	# 		if time_human_info_dict[j] == one_to_one_list[i]:
	# 			print u'匹配的结果:%s' % j
	# 			human_info_dict[j] = other_info_list[i]
	# 			print j, human_info_dict[j]



human_info('967567')

# history_works_info('967567')


