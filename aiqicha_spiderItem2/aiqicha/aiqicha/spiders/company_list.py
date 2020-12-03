# -*- coding: utf-8 -*-
from scrapy import Spider


class CompanyListSpiders(Spider):
    allowed_domains = ['aiqicha.baidu.com']
    start_url = ''