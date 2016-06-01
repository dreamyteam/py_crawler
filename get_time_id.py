#-*- coding:utf-8 -*-


import urllib2
import json
import time
import re

from scrapy.selector import Selector

search_name = "赛德克·巴莱(下)：彩虹桥"
# a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=201653114572077108&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=0&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)
a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=http://search.mtime.com/search/?q={0}&t=20166110313036717&Ajax_CallBackArgument0={1}&Ajax_CallBackArgument1=1&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'.format(search_name, search_name)
# a = 'http://service.channel.mtime.com/Search.api?Ajax_CallBack=true&Ajax_CallBackType=Mtime.Channel.Services&Ajax_CallBackMethod=GetSearchResult&Ajax_CrossDomain=1&Ajax_RequestUrl=shttp://search.mtime.com/search/?q=%E9%A5%A5%E9%A5%BF%E6%B8%B8%E6%88%8F3%EF%BC%9A%E5%98%B2%E7%AC%91%E9%B8%9F(%E4%B8%8B)&t=20166110313036717&Ajax_CallBackArgument0=%E9%A5%A5%E9%A5%BF%E6%B8%B8%E6%88%8F3%EF%BC%9A%E5%98%B2%E7%AC%91%E9%B8%9F(%E4%B8%8B)&Ajax_CallBackArgument1=1&Ajax_CallBackArgument2=290&Ajax_CallBackArgument3=0&Ajax_CallBackArgument4=1'
response = urllib2.urlopen(a)
data = response.read()
re_info = re.findall(r'(var result_20166110313036717 = )(.*?)(;var getSearchResult=result_20166110313036717;)', data)

deal_data = json.loads(re_info[0][1])
print re_info[0][1]

for i in deal_data['value']['movieResult']['moreMovies']:

	print '\n'
	print '\n'
	for j in i:
		print j, '\t\t\t', i[j]
		print '-------------' * 5





