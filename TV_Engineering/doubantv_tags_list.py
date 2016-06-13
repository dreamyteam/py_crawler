#-*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


from configfile import *
import urllib2
import json
import threading
import time

class GetTVSource(threading.Thread):

	def __init__(self, tag, num):

		threading.Thread.__init__(self)
		self.num = num
		self.tag = tag

	def run(self):
		response = urllib2.urlopen('https://movie.douban.com/j/search_subjects?type=movie&tag={0}&sort=recommend&page_limit=20&page_start={1}'.format(self.tag, self.num,))
		data = json.loads(response.read())
		tag_dict = tags_field()
		for i in data['subjects']:
			tag_dict['tag'] = self.tag
			tag_dict['rate'] = i['rate']
			tag_dict['title'] = i['title']
			tag_dict['url'] = i['url']
			tag_dict['cover_x'] = i['cover_x']
			tag_dict['cover_y'] = i['cover_y']
			tag_dict['cover'] = i['cover']
			tag_dict['id'] = i['id']
			tag_dict['scrapy_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
			db.DoubanTagID.update({'url': i['url']}, {'$set': tag_dict}, True)

	@staticmethod
	def go():
		threads = list()
		for i in douban_tag_list:
			for j in range(0, 20):
				# print i, j
				thread_1 = GetTVSource(i, 20 + j * 20)
				thread_1.start()
				threads.append(thread_1)
		for t in threads:
			t.join()

		# print "That's over"


if __name__ == '__main__':

	GetTVSource.go()



