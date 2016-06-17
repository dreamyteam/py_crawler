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
	#更新时间
	data['update_time'] = str()

	'''更新历史信息'''
	data['history_info'] = list()



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
	
	return data

#历史记录数据存储格式
def history_formate():
	
	data = dict()
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
	#更新时间
	data['update_time'] = str()
	
	return data




#时光网演职员标签
staff_list = {
				'director': u'导演 Director', 
				'editor': u'编剧 Writer', 
				'produced_by': u'制作人 Produced by', 
				'Cinematography': u'摄影 Cinematography', 
				'film_editing': u'剪辑 Film Editing', 
				'music': u'原创音乐 Original Music', 
				'Visual_Effects_Supervisor': u'视觉特效 Visual Effects Supervisor',
				'art_design': u'美术设计 Art Direction by', 
				'Assistant_Director': u'副导演/助理导演 Assistant Director', 
				'Sound_Department': u'声音部门 Sound Department', 
				'Makeup_Department': u'化妆造型 Makeup Department', 
				'Choreographer': u'动作指导 Choreographer', 
				'cloth_design': '服装设计 Costume Design by'
			}
#时光网制作or发行公司标签
company_list = {
	
				'made_company': u'制作公司',
				'sale_company': u'发行公司'
			}



#代理
import urllib2
request_list = ['proxy', 'no']
def proxy_request(url):
	request = urllib2.Request(url)
	proxy = urllib2.ProxyHandler(
									{
										'http': 'http://127.0.0.1:8123',
										'https': 'https://127.0.0.1:8123',
									},
								)

	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	return opener.open(request)
	
def no_proxy(url):
	response = urllib2.urlopen(url)
	return  response





