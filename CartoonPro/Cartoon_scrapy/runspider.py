#-*- coding:utf -*-

import scrapy

from scrapy.crawler import CrawlerProcess
from Cartoon_scrapy.spiders.acqq import *


process = CrawlerProcess()
process.crawl(AcqqSpider)
process.start()

