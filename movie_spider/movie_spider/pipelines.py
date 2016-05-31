# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

class MovieSpiderPipeline(object):
    def process_item(self, item, spider):
        print u'电影的ttid:%s' % item['ttid']
        print u'电影名称:%s' % item['title']
        print u'电影URL:%s' % item['movie_url']
        db.IMDB_ID.update({'_id': item['ttid']}, {'$set': item}, True)




         