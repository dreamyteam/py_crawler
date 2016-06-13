#-*- coding:utf-8 -*-

#mongodb链接
import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.TVData


#豆瓣影视标签（热门影视来源）
douban_tag_list = [
					u'热门', u'最新', u'经典', u'可播放', u'豆瓣高分', u'冷门佳片', 
					u'华语', u'欧美', u'韩国', u'日本', u'动作', u'喜剧', u'爱情',
					u'科幻', u'悬疑', u'恐怖', u'成长',
				]
#豆瓣影视标签字段
def tags_field():

	data = dict()
	#电影名称
	data['title'] = str()
	#电影链接
	data['url'] = str()
	#海报链接
	data['cover'] = str()
	#豆瓣ID
	data['id'] = str()
	#豆瓣评分
	data['rate'] = str()
	#电影标签
	data['tag'] = str()
	#抓取时间（已抓过不更新）
	data['scrapy_time'] = str()
	#数据源
	data['source'] = str()

	return data



