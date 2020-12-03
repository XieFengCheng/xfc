# -*- coding: utf-8 -*-
# import warnings
#
# from aiohttp import signals
# from scrapy import Spider
# from scrapy.exceptions import ScrapyDeprecationWarning

from scrapy_redis.spiders import RedisSpider
from scrapy.http import Request
from urllib import parse

import json
import hashlib
import re
from ..settings import bixiao_business, bixiao_news, bixiao_aiqicha_list
from ..untils.request import timestamp_to_strftime, request_doing
from ..untils.header_set import post_login
from ..db.info_list_model import _insert as list_insert
from ..db.news_model import _insert as news_info_insert



class SupplySpiders(RedisSpider):
    name = 'SupplySpiders'
    redis_key = 'SupplySpiders:start_urls'
    # start_url = 'https://aiqicha.baidu.com/index/suggest'
    company_url = 'https://aiqicha.baidu.com/s/l?q={keys}&t=&s=10&o=0&f=%7B%7D'
    info_url = 'https://aiqicha.baidu.com/detail/basicAllDataAjax?pid={pid}'
    news_url = 'https://aiqicha.baidu.com/yuqing/topicAjax?pid={pid}&p=1'
    product_url = 'https://aiqicha.baidu.com/detail/compDevelopAjax?pid={}'


    def parse(self, response):
        """ 公司列表 """
        json_response = json.loads(response.text)

        total = json_response.get('data').get('totalNumFound')
        if json_response.get('data') and int(total) > 0:
            company_list = json_response.get('data').get('resultList')[0]
            pid = company_list['pid']
            title = company_list['titleName']
            print(pid, title, 'A'*80)
            info_links = self.info_url.format(pid=pid)
            yield Request(
                info_links,
                callback=self.parse_info,
                meta={
                    'pid': pid,
                    'title': title,
                    'info_links': info_links
                }
            )


    def parse_info(self, response):
        """ 公司基本信息 """
        aiqicha_list_item = {}
        news_item = dict()
        json_response = json.loads(response.text)
        if json_response['data']:
            aiqicha_list_item['version'] = json_response
            aiqicha_list_item['pid'] = response.meta['pid']
            aiqicha_list_item['title'] = response.meta['title']
            aiqicha_list_item['info_links'] = response.meta['info_links']
            aiqicha_list_item['md5_vals'] = self.md5_convert(str(json_response))
            insert_res = list_insert(aiqicha_list_item)
            if insert_res.get('status', False):
                print(aiqicha_list_item, '&'*80)
                print(insert_res, '%'*80)

            # print(json_response['data'])
            # print(json_response['data']['annualReportData']['list'])        # 年报
            # print(json_response['data'].keys())
                year_list = json_response['data']['annualReportData']['list']
                print(len(year_list), 'A'*80)
                for year_info in year_list:
                    news_item['name'] = year_info['name']
                    news_item['links'] = year_info['link']
                    content_url = 'https://aiqicha.baidu.com'+year_info['link']
                    news_item['content_url'] = content_url
                    # print(news_item, '*'*80)
                    news_insert = news_info_insert(news_item)
                    if news_insert.get('status', False):
                        print(news_item, '@'*80)
                        print(news_insert, '#'*80)
                    else:
                        print(news_insert.get('msg'), 'Q'*80)
                        continue
            else:
                return insert_res.get('msg'), 'P'*80

    def write_file(self, name_file, info_vals):
        with open(name_file, 'a', encoding='utf-8') as wf:
            wf.write(str(info_vals)+'\n')

    def md5_convert(self, string):
        """
        计算字符串md5值
        """
        m = hashlib.md5()
        m.update(string.encode())
        return m.hexdigest()