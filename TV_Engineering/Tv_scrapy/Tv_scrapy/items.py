# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TvScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass





#IMDB演职人员标签
IMDB_staff_list = {
					'director': 'Directed by', 
					'editor': 'Writing Credits', 
					'produced_by': 'Produced by', 
					'Cinematography': 'Cinematography by', 
					'film_editing': 'Film Editing by', 
					'music': 'Music by', 
					'Visual_Effects_Supervisor': 'Visual Effects by',
					'art_design': 'Art Direction by', 
					'Assistant_Director': 'Second Unit Director or Assistant Director', 
					'Sound_Department': 'Sound Department', 
					'Makeup_Department': 'Makeup Department', 
					'Choreographer': 'Stunts', 
					'cloth_design': 'Costume Design by',
				}

#mongodb中影视数据的存储格式
def data_formate():

	data = dict()
	'''一次性数据'''
	#图片流数据
	data['img_data'] = str()
	#图片链接
	data['img_url'] = str()
	#外文名称
	data['foreign_name'] = str()
	#别名
	data['other_name'] = list()
	#语言
	data['language'] = list()
	#片长
	data['runtime'] = str()
	#上映地区和时间（二维列表[地区, 时间]）
	data['release_info'] = list()
	#制作公司（字典:名称和URL）
	data['production_company'] = list()
	#发行公司（字典:名称和URL）
	data['distributors'] = list()
	#IMDB编号（没有就不要IMDB编号）
	data['IMDB_ID'] = str()
	#导演（字典:名称和URL）
	data['director'] = list()
	#主演（豆瓣独有，可能对搜索猫眼票房有帮助）（字典:名称和URL）
	data['main_actor'] = list() 
	#编剧（字典:名称和URL）
	data['editor'] = list()
	#制作人（字典:名称和URL）
	data['produced_by'] = list()
	#剪辑（字典:名称和URL）
	data['film_editing'] = list()
	#音乐（字典:名称和URL）
	data['music'] = list()
	#美术设计（字典:名称和URL）
	data['art_design'] = list()
	#服装设计（字典:名称和URL）
	data['cloth_design'] = list()
	#视觉特效（字典:名称和URL）
	data['Visual_Effects_Supervisor'] = list()
	#动作指导（字典:名称和URL）
	data['Choreographer'] = list()
	#摄影（字典:名称和URL）
	data['Cinematography'] = list()
	#助理导演（字典:名称和URL）
	data['Assistant_Director'] = list()
	#化妆部门（字典:名称和URL）
	data['Makeup_Department'] = list()
	#声音部门（字典:名称和URL）
	data['Sound_Department'] = list()
	#演员对照表（二维列表[{演员名+URL}，角色]）
	data['actor_charactor'] = list()
	#电影类型
	data['film_type'] = list()
	#电影简介（分段）
	data['introduce'] = list()
	#电影标签（豆瓣独有， 存字典， 保存URL）
	data['tags'] = list()

	'''更新数据'''
	#评分（每月）
	data['average'] = str()
	#评分人数（每月）
	data['votes'] = int()
	#短评数量（每月）
	data['all_short'] = int()
	#长评数量（每月）
	data['all_long'] = int()
	#新闻数量（每月）
	data['all_news'] = int()
	#排名（时光和IMDB独有， 每天）
	data['rank'] = str()
	#提名次数（每月）
	data['nominations'] = int()
	#获奖次数（每月）
	data['wins'] = int()
	#获奖提名具体信息记录（每月）
	data['award_nominate'] = list()

	'''自加字段'''
	#豆瓣时光IMDB关联ID，用豆瓣ID关联
	data['Relate_ID'] = str()
	#各自网站的ID
	data['movie_id'] = str()
	#电影名称
	data['movie_name'] = str()
	#电影URL
	data['movie_url'] = str()
	#电影来源 就三个 douban，IMDB， time
	data['source'] = str()
	#制作国家和地区
	data['area'] = str()
	#影片年份
	data['movie_time'] = str()
	#更新时间
	data['update_time'] = str()

	return data










	