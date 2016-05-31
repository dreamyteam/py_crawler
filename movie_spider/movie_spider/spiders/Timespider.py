# -*- coding: utf-8 -*-
import scrapy


class TimeSpider(scrapy.Spider):
    name = "Timespider"
    start_urls = (
        'http://www.ti/',
    )

    def parse(self, response):
        pass
