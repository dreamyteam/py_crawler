#-*- coding:utf-8 -*-

'''豆瓣→IMDB→时光网为基础建IP池'''

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

all_info = db.MovieInfo.find({'source': 'douban'}).skip(101)


def map_ip(list_info):
	if list_info:
		for i in list_info:
			ip_dict = dict()
			ip_dict['source'] = 'douban'
			ip_dict['name'] = i['name']
			ip_dict['url'] = i['url']
			db.IpData.update({'url': i['url']}, {'$set': ip_dict}, True)

for i in all_info:
	map(map_ip, [i['main_actor'], i['director'], i['editor']])





















