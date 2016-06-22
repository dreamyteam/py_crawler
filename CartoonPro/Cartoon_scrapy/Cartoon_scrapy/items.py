# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CartoonSourceItem(scrapy.Item):

	source = scrapy.Field()
	url = scrapy.Field()
	title = scrapy.Field()
	js_id = scrapy.Field()
	update_time = scrapy.Field()
	author = scrapy.Field()
	c_ticai = scrapy.Field()

class CartoonInfo(scrapy.Item):

	#一次性
	source = scrapy.Field()
	name = scrapy.Field()
	url = scrapy.Field()
	other_name = scrapy.Field()
	img_url = scrapy.Field()
	img_data = scrapy.Field()
	area = scrapy.Field()
	author = scrapy.Field()
	c_type = scrapy.Field()
	c_ticai = scrapy.Field()
	introduce = scrapy.Field()

	#每月
	popular = scrapy.Field()
	update_time = scrapy.Field()
	status = scrapy.Field()

	all_click = scrapy.Field()#有妖气
	all_tickts = scrapy.Field()#有妖气
	all_tags = scrapy.Field()#有妖气
	relate_animation = scrapy.Field()#动漫之家
	relate_animation_status = scrapy.Field()#动漫之家

	#每天
	all_theme = scrapy.Field()
	all_response = scrapy.Field()
	scrapy_time = scrapy.Field()
	all_comments = scrapy.Field()#动漫之家，有妖气
	rss_num = scrapy.Field()#订阅人数
	collect = scrapy.Field()#有妖气

	return_status = scrapy.Field()#返回状态 有妖气 有不存在的情况

class DmzjInfo(scrapy.Item):

	#一次性
	source = scrapy.Field()
	name = scrapy.Field()
	url = scrapy.Field()
	other_name = scrapy.Field()
	img_url = scrapy.Field()
	area = scrapy.Field()
	author = scrapy.Field()
	c_type = scrapy.Field()
	c_fenlei = scrapy.Field()
	c_ticai = scrapy.Field()
	introduce = scrapy.Field()

	#每月
	popular = scrapy.Field()
	update_time = scrapy.Field()
	status = scrapy.Field()

	relate_animation = scrapy.Field()
	relate_animation_status = scrapy.Field()

	#每天
	all_theme = scrapy.Field()
	all_response = scrapy.Field()
	scrapy_time = scrapy.Field()
	rss_num = scrapy.Field()
	





class UInfo(scrapy.Item):
	#一次性
	#动漫源
	source = scrapy.Field()
	#名称
	name = scrapy.Field()
	#链接
	url = scrapy.Field()
	#图片链接
	img_url = scrapy.Field()
	#图片数据
	img_data = scrapy.Field()
	#作者
	author = scrapy.Field()
	#类别
	c_leibie = scrapy.Field()
	#类型
	c_leixing = scrapy.Field()
	#标签
	tags = scrapy.Field()
	#简介
	introduce = scrapy.Field()

	#每月

	#最近更新时间
	update_time = scrapy.Field()
	#状态
	status = scrapy.Field()
	#总点击
	all_click = scrapy.Field()
	#总月票
	all_tickts = scrapy.Field()

	#每天
	#抓取时间
	scrapy_time = scrapy.Field()
	#总评论数
	all_comments = scrapy.Field()
	#收藏
	collect = scrapy.Field()
	#判断有此作品在有妖气是否下家或者删除
	return_status = scrapy.Field()#返回状态 有不存在的情况 pass

class AcqqInfo(scrapy.Item):
	#一次性

	#动漫源
	source = scrapy.Field()
	#名称
	name = scrapy.Field()
	#链接
	url = scrapy.Field()
	#图片链接
	img_url = scrapy.Field()
	#图片数据
	img_data = scrapy.Field()
	
	#标签
	tags = scrapy.Field()
	#作者
	author = scrapy.Field()
	#类别
	c_leibie = scrapy.Field()
	#类型
	c_leixing = scrapy.Field()
	
	#简介
	introduce = scrapy.Field()

	#每月

	#最近更新时间
	update_time = scrapy.Field()
	#评分
	score = scrapy.Field()
	#评级人数
	grade_people = scrapy.Field()
	#收藏数量
	collect = scrapy.Field()
	#红票数量
	red_tickts = scrapy.Field()
	#状态
	status = scrapy.Field()
	#人气
	popular = scrapy.Field()
	#本月月票
	month_tickts = scrapy.Field()
	#本月排名
	rank = scrapy.Field()
	#总评论数
	all_comments = scrapy.Field()

	#每天
	#抓取时间
	scrapy_time = scrapy.Field()
	#今日月票
	today_tickts = scrapy.Field()

	




