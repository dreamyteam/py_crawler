# -*- coding: utf-8 -*-

import pymongo 
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.CartoonData


get_info = db.CartoonInfo.find({'source': 'acqq'})
get_info = [i for i in get_info]

for i in get_info:
	new_id = i['source'] + i['url'].split('id/')[1].strip()
	db.CartoonInfo.update({'url': i['url']}, {'$set': {'c_id': new_id}})

