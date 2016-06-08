#-*- coding:utf-8 -*- 
import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

get_info = db.IpData.find({'source': 'douban'}).skip(0).limit(100)
import urllib2
from scrapy.selector import Selector
from config_constant import *
import bson
import time
#解析页面
# def html_parse(get_info):
# 	for i in get_info:
# 		# response = urllib2.urlopen(i['url'])
# 		# data = response.read()
# 		# sel = Selector(text=data)
# 		# print u'请求到的人物URL:%s' % response.url
# 		print u'人物:%s' % i['name']
# 		print u'读取的人物URL:%s' % i['url']
# 		print '--------' * 5

# html_parse(get_info)
# db.IpData.update({'url': 'https://movie.douban.com/search/%E9%9D%B3%E4%B8%9C'}, {'$set': {'url': 'https://movie.douban.com/celebrity/1314123/'}})

#mongodb中的搜索结果转人物URL
def search_to_douban_id(human_dict):

	if 'search/' in human_dict['url']:
		print u'旧的URL:%s' % human_dict['url']
		response = urllib2.urlopen(human_dict['url'])
		data = response.read()
		sel = Selector(text=data)
		new_url = sel.xpath('//*[@class="content"]/h3/a/@href').extract()
		if new_url:
			new_url = new_url[0].strip()
			print u'新的URL:%s' % new_url
			# db.IpData.update({'url': human_dict['url']}, {'$set': {'url': new_url}})
		print u'-----' * 5

# map_list = [i for i in get_info]
# map(search_to_douban_id, map_list)


#代理
def proxy_request(url):
	request = urllib2.Request(url)
	proxy = urllib2.ProxyHandler(
									{
										'http': 'http://127.0.0.1:8123',
										'https': 'https://127.0.0.1:8123',
									}
								)
	opener = urllib2.build_opener(proxy)
	urllib2.install_opener(opener)
	return opener.open(request).read()


def human_info(info_dict):
	data = proxy_request(info_dict['url'])
	sel = Selector(text=data)
	print u'URL:%s' % info_dict['url']
	get_dict = human_info_format()
	get_dict['human_url'] = info_dict['url']
	#照片
	get_dict['img_url'] = sel.xpath('//*[@id="headline"]//*[@class="pic"]/a/img/@src').extract()[0].strip()
	print u'照片URL:%s' % get_dict['img_url']
	get_dict['img_data'] = bson.Binary(urllib2.urlopen(get_dict['img_url']).read())
	#中文名和英文名
	name = sel.xpath('//*[@id="content"]/h1/text()').extract()[0].strip()
	print u'名字:%s' % name
	name_list = name.split(' ')
	get_dict['cn_name'] = name_list[0]
	print u'中文名:%s' % get_dict['cn_name']
	name_list.pop(0)
	get_dict['en_name'] = ' '.join(name_list)
	print u'英文名:%s' % get_dict['en_name']

	#其余信息
	for i in sel.xpath('//*[@id="headline"]//*[@class="info"]/ul/li'):
		for j in douban_human_dict:
			if i.xpath('./span/text()').extract()[0].strip() == douban_human_dict[j]:
				source_info = i.xpath('./text()').extract()
				if source_info:
					source_info = i.xpath('./text()').extract()[1].strip().split(':')[1].strip()
					get_dict[j] = source_info
					print u'{0}\t\t{1}'.format(j, get_dict[j])

					if i.xpath('./span/text()').extract()[0].strip() == u'imdb编号':
						get_dict['IMDB_ID'] = dict()
						get_dict['IMDB_ID']['name'] = i.xpath('./a/text()').extract()[0].strip()
						get_dict['IMDB_ID']['url'] = i.xpath('./a/@href').extract()[0].strip()
						print u'imdb编号:{0}链接:{1}'.format(get_dict['IMDB_ID']['name'], get_dict['IMDB_ID']['url'])
	#简介
	all_introduce = sel.xpath('//*[@class="all hidden"]/text()').extract()
	if all_introduce:
		introduce = ''.join(all_introduce)		
		print introduce
	else:
		introduce = str()
	get_dict['introduce'].append(introduce)
	# history_works_record(info_dict['url'])
	db.PeopleData.update({'url': get_dict['human_url']}, {'$set': get_dict}, True)

#历史作品暂时不请求
def history_works_record(url):
	new_url = url + 'movies?start=0&format=pic&sortby=time&'
	data = proxy_request(new_url)
	sel = Selector(text=data)
	all_count = sel.xpath('//*[@class="count"]/text()').extract()[0].strip()
	print u'一共的条数:%s' % all_count



# human_info({'name': u'姜文', 'url': 'https://movie.douban.com/celebrity/1021999/'})



for i in get_info:
	time.sleep(1.5)
	if 'celebrity' in i['url']:
		human_info(i)
		print '---------' * 5














