#-*- coding:utf-8 -*-

import urllib2
import json
import time
import re

from scrapy.selector import Selector

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData


get_info = db.DoubanTagID.find().limit(20)

# for i in get_info:
# 	print i['title']
# 	print i['url']
# 	print '\n'


def search_movie(search_name):
	# search_name = "赛德克·巴莱(下)：彩虹桥"

	a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=20166110313036717&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=1&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)
	
	response = urllib2.urlopen(a)
	data = response.read()
	re_info = re.findall(r'(var result_20166110313036717 = )(.*?)(;var getSearchResult=result_20166110313036717;)', data)

	deal_data = json.loads(re_info[0][1])
	print re_info[0][1]

	for i in deal_data['value']['movieResult']['moreMovies']:
		print i['movieTitle']
		print '\n'
		# print '\n'
		# print '\n'
		# for j in i:
		# 	print j, '\t\t\t', i[j]
		# 	print '-------------' * 5



for i in get_info:
	
	search_movie(i['title'].encode('utf-8'))
	print i['title']
	print i['url']
	print '\n'
	break


