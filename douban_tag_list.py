#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import threading
import urllib2
import json
import random
from config_constant import *
import time

import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
# client = pymongo.MongoClient('localhost', 27017)
db = client.MovieData

class MyThread (threading.Thread):
    
    def __init__(self, tag, num):

        threading.Thread.__init__(self)
        self.num = num
        self.tag = tag

    def run(self):

        proxy = urllib2.ProxyHandler(random.choice(proxy_list))
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        response = urllib2.urlopen('https://movie.douban.com/j/search_subjects?type=movie&tag={0}&sort=recommend&page_limit=20&page_start={1}'.format(self.tag, self.num,))
        data = json.loads(response.read())
        movie_dict = dict()
        for i in data['subjects']:
            movie_dict['tag'] = self.tag
            movie_dict['rate'] = i['rate']
            movie_dict['title'] = i['title']
            movie_dict['url'] = i['url']
            movie_dict['cover_x'] = i['cover_x']
            movie_dict['cover_y'] = i['cover_y']
            movie_dict['cover'] = i['cover']
            movie_dict['id'] = i['id']
            movie_dict['is_new'] = i['is_new']
            movie_dict['update_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            db.DoubanTagID.update({'_id': i['id']}, {'$set': movie_dict}, True)


threads = []
for i in tag_list:
	#每个标签取100个
	for j in range(0,8):
	    print i,j
	    thread_1 = MyThread(i, 20+j*20)
	    thread_1.start()
	    threads.append(thread_1)
print u'几个线程%s' % len(threads)
for t in threads:
    t.join()

print "Exiting Main Thread"



