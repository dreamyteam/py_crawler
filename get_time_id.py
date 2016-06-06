#-*- coding:utf-8 -*-

import urllib2
import json
import time
import re

from scrapy.selector import Selector

# import pymongo
# client = pymongo.MongoClient('112.74.106.159', 27017)
# db = client.MovieData

# get_info = db.MovieInfo.find().skip(15).limit(10)

def search_movie(search_name, movie_time):
	# search_name = "叶问"
	a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=1&i=0&c=290&t=20166612441087539&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=1&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)
	# print '-----%s' % a
	response = urllib2.urlopen(a)
	data = response.read()
	# print data
	re_info = re.findall(r'(var result_1,20166612441087539 = )(.*?)(;var getSearchResult=result_1,20166612441087539;)', data)
	# print u'匹配结果:%s' % re_info
	deal_data = json.loads(re_info[0][1])
	# print re_info[0][1]

	keywords = ''.join([i['value'] for i in deal_data['value']['words']])
	print u'检索出来的关键字:%s' % keywords

	#检索和判断
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
		print '\n'

	return 'nomatch'


def time_id(movie_dict):
	name_list = movie_dict['movie_name'].split(' ')
	# print u'列表:%s' % name_list
	movie_name = '**'.join(name_list)
	print movie_name, movie_dict['movie_time']
	result_first = search_movie(name_list[0].encode('utf-8'), movie_dict['movie_time'])
	if result_first == 'nomatch':
		name_list.pop(0)
		if name_list:
			new_search_word = '%20'.join(name_list)
			print u'第二次检索关键词:%s' % new_search_word
			result_second = search_movie(new_search_word.encode('utf-8'), movie_dict['movie_time'])
			print u'第二次返回的时光网ID:%s' % result_second
			return result_second

		else:
			print u'暂时从时光网搜索不到或者是我太菜没检索到，改进检索' 
			return 'nofind'
	else:
		print u'第一次返回的时光网ID:%s' % result_first
		return result_first

	

# for i in get_info:
# 	time_id(i)
# 	print '---------' * 5
	# break
















