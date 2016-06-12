#-*- coding:utf-8 -*-


import pymongo
client = pymongo.MongoClient('112.74.106.159', 27017)
db = client.MovieData

import urllib2
import re
import json
# get_info = db.PeopleData.find({'source': 'douban'}).skip(20).limit(10)

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

def search_human_info(name):
	
	# url = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=20166121103594698&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=0&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(name, name)
	url = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=20166121103594698&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=3&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(name, name)
	# print url
	response = urllib2.urlopen(url)
	# data = proxy_request(url)
	data = response.read()
	#数字池随机变化
	re_info = re.findall(r'(var result_20166121103594698 = )(.*?)(;var getSearchResult=result_20166121103594698;)', data)
	
	# print re_info[0][1]
	json_data = json.loads(re_info[0][1])
	keywords = ''.join([i['value'] for i in json_data['value']['words']])
	print u'搜索关键字:%s' % keywords
	
	if 'morePersons' in json_data['value']['personResult']:
		for i in json_data['value']['personResult']['morePersons']:
			is_in_list = list()
			is_in_other_list = list()
			for j in keywords:
				if j in i['personTitle'].lower():
					is_in_list.append('ok')
				else:
					is_in_list.append('no')
				if j in i['nameOthers'].lower():
					is_in_other_list.append('ok')
				else:
					is_in_other_list.append('no')

			norepid_list = list(set(is_in_list))
			norepid_list_2 = list(set(is_in_other_list))
			if (len(norepid_list) == 1) and (norepid_list[0] == 'ok'):
				print u'人物id:%s' % i['personId']
				return i['personId']
			else:
				if (len(norepid_list_2) == 1) and (norepid_list_2[0] == 'ok'):
					print u'从别名中找到的ID:%s' % i['personId']
					return i['personId']

	return 'nomatch'

# if search_human_info('trevor') == 'nomatch':
# 	search_human_info('Cody Horn')

# search_human_info('meganpark')


for i in get_info:
	# search_human_info('小罗伯特唐尼')
	search_word = i['cn_name']
	if ' ' in i['cn_name']:
		search_word = i['cn_name'].replace(' ', '%20')
	data = search_human_info(search_word.encode('utf-8'))
	if data == 'nomatch':
		search_word = i['en_name']
		if ' 'in i['en_name']:
			search_word = i['en_name'].replace(' ', '%20')
		data = search_human_info(search_word.encode('utf-8'))
		if data == 'nomatch':
			print i['cn_name']
			print i['human_url']
# 			break
# 	print '--------' * 5












