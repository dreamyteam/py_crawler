#-*- coding:utf-8 -*-


import urllib2


from scrapy.selector import Selector
from config_constant import *
import json

def maoyan_info(url):
	response = urllib2.urlopen(url)
	sel = Selector(text=response.read())
	data = cateye_info()
	data['url'] = url
	print u'来源URL:%s' % data['url']
	data['all_box_office'] = sel.xpath('//*[@class="tags clearfix"]/span/text()').extract()[0].strip()
	print u'总票房:%s' % data['all_box_office']

	#日票房信息
	all_day = sel.xpath('//*[@id="ticketList"]//*[@id="ticket_tbody"]/ul')
	for i in all_day:
		date = i.xpath('./li[1]/span/b/text()').extract()[0].strip()
		print u'日期:%s' % date
		day_box_officce = i.xpath('./li[2]/text()').extract()[0].strip()
		print u'当日票房:%s' % day_box_officce
		day_box_officce_percent = i.xpath('./li[3]/text()').extract()[0].strip()
		print u'票房占比:%s' % day_box_officce_percent
		day_release_percent = i.xpath('./li[4]/text()').extract()[0].strip()
		print u'排片占比:%s' % day_release_percent
		day_people = i.xpath('./li[5]/text()').extract()[0].strip()
		print u'场均人次:%s' % day_people

		print '-------' * 5


#城市信息
def city_info(date):
	url = 'http://piaofang.maoyan.com/movie/78421/cityBox?date={0}'.format(date)

	json_data = json.loads(urllib2.urlopen(url).read())
	sel = Selector(text=json_data['html'])
	all_info = sel.xpath('//*[@class="m-table normal m-table-city"]/tbody/tr')
	for i in all_info:
		city = i.xpath('./td[1]/text()').extract()[0].strip()
		print u'城市:%s' % city
		box_office = i.xpath('./td[2]/text()').extract()[0].strip()
		print u'票房:%s' % box_office
		box_office_percent = i.xpath('./td[3]/text()').extract()[0].strip()
		print u'票房占比:%s' % box_office_percent
		release_percent = i.xpath('./td[4]/text()').extract()[0].strip()
		print u'排片占比:%s' % release_percent
		total_box_office = i.xpath('./td[5]/text()').extract()[0].strip()
		print u'累计票房:%s' % total_box_office
		position_percent = i.xpath('./td[6]/text()').extract()[0].strip()
		print u'排座占比:%s' % position_percent
		gold_percent = i.xpath('./td[7]/text()').extract()[0].strip()
		print u'黄金场占比:%s' % gold_percent
		per_people = i.xpath('./td[8]/text()').extract()[0].strip()
		print u'场均人次:%s' % per_people
		people = i.xpath('./td[9]/text()').extract()[0].strip()
		print u'人次:%s' % people
		times = i.xpath('./td[10]/text()').extract()[0].strip()
		print u'场次:%s' % times
		print '-------------' * 5



city_info('2016-06-11')


# maoyan_info('http://piaofang.maoyan.com/movie/78421')






















