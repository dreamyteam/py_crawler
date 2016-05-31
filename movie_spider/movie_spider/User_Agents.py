#-*- coding:utf-8 -*-

import random
import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.develop

#获取useragent池
get_info = db.userAgents.find()
USER_AGENTS = [i['userAgent'] for i in get_info]

class MyUserAgent(object):
	def process_request(self, request, spider):
		request.headers.setdefault('User-Agent', random.choice(USER_AGENTS))






