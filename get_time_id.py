#-*- coding:utf-8 -*-


import urllib2
import json
import time
import re

from scrapy.selector import Selector

search_name = '复仇者联盟'
a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=201653114572077108&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=0&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)

response = urllib2.urlopen(a)
data = response.read()
re_info = re.findall(r'(var result_201653114572077108 = )(.*?)(;var getSearchResult=result_201653114572077108;)', data)

deal_data = json.loads(re_info[0][1])
# print deal_data

for i in deal_data['value']['movieResult']['moreMovies']:
	print '\n'
	for j in i:
		print j, '\t\t\t', i[j]
			




