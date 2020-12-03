#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------
describe:


--------------------------------------------------------------
"""

# ------------------------------------------------------------
# usage: /usr/bin/python tianyancha.py
# ------------------------------------------------------------
from urllib import parse
from bs4 import BeautifulSoup
from bson import ObjectId

from deploy.config import RUN_MODE, TYC_DETAIL_API, \
    TYC_SEARCH_API, TYC_COOKIE
from deploy.utils.http import api_get
from deploy.utils.logger import logger as LOG
from deploy.utils.utils import random_sleep
from lxml import etree
from datetime import datetime

from db.mongo_set import (bixiao_business, bixiao_people, bixiao_shareholder,
                          bixiao_news, bixiao_product, bixiao_recruit, bixiao_record_icp)
from db.model_email_phone import _insert as email_phone_insert
from db.financing_model import _insert as financing_insert
from db.reports_model import _insert as reports_insert
from db.capital_model import _insert as capital_insert
from db.news_model import _insert as news_insert
from db.people_model import _insert as people_insert
from db.product_model import _insert as product_insert
from db.record_icp_model import _insert as record_icp_insert
from db.recruit_model import _insert as recruit_insert
from db.reports_model import _insert as reports_insert
from libs.get_cookies import cookies_get
import redis
import time
import requests


class TianYanChaClient(object):
    """
    tianyancha client
    """

    def __init__(self):
        super(object, self).__init__()
        self.MAX_PAGE = 2
        self._init_header()
        self.count = 1
        pool = redis.ConnectionPool(host='', port=6379, password='', db=15)
        self.conn = redis.Redis(connection_pool=pool)
        self.ss_request = requests.session()

    def _init_header(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'news.tianyancha.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                          ') Chrome/83.0.4103.97 Safari/537.36',
        }


    def detail_by_url(self, comp_url: str):
        detail_res = dict()
        if not comp_url:
            return detail_res
        search_resp = comp_url
        soup = BeautifulSoup(search_resp, 'lxml')

        # header: 详情页 公司名称
        title_list = soup.find_all('div', class_="header")
        et2 = etree.HTML(search_resp)
        # if not title_list:
        #     return -1
        try:
            company_name = (title_list[0].find_all('h1', class_="name"))[0].get_text()
        except:
            name = et2.xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[1]/h1/text()')
            company_name = ''.join(name)
        detail_res['company_name'] = company_name

        # 电话 更多联系方式
        # print(et2.xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[1]/span[3]/script/text()'), 'OK '*80)
        origin_phone = et2.xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[1]/span[3]/script/text()')

        # 邮箱 更多邮箱
        # print(et2.xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[2]/span[3]/script/text()'), 'EMAIL '*80)
        origin_email = et2.xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[2]/span[3]/script/text()')

        if origin_phone and origin_email:
            year_list = [i.get('showSource') for i in eval(origin_phone[0])]
            phone_item_vals = [i.get('phoneNumber') for i in eval(origin_phone[0])]
            email_list = eval(origin_email[0])
            contact_item = {}
            for contact in zip(year_list, phone_item_vals, email_list):
                contact_item['company_name'] = detail_res.get('company_name', '')
                contact_item['report_year'] = contact[0]
                contact_item['phone'] = contact[1]
                contact_item['email'] = contact[-1]
                contact_item['date_time'] = self.timestamp_to_strftime(time.time())
                print(contact_item, '@'*80)
                reslut = email_phone_insert(contact_item)
                if reslut.get('status', False):
                    print('插入成功')
                else:
                    print(reslut.get('msg'))

        # detail: 电话 邮箱 公司官网 地址 简介
        detail_div = soup.find_all('div', class_="detail")

        def while_req(url):
            sub_is_ok, sub_search_resp = api_get(url=url,
                                                 headers=self.headers,
                                                 data={},
                                                 resptype='text')
            return sub_is_ok, sub_search_resp

        # 添加手动验证功能
        if not detail_div:
            while 1:
                if detail_div:
                    break
                else:
                    LOG.critical('验证############### %s ###############' % comp_url)
                    random_sleep(20, 25)
                    self.headers['Cookie'] = cookies_get()
                    is_ok, search_resp = while_req(comp_url)
                    soup = BeautifulSoup(search_resp, 'lxml')
                    detail_div = soup.find_all('div', class_="detail")

        for div in detail_div[0].find_all('div'):
            if not div:
                continue

            # f0 电话 && 邮箱
            if div.get('class') == ['f0']:
                for big_index, big_child in enumerate(div):
                    if big_index == 0:
                        for index, child in enumerate(big_child.children):
                            if index == 1:
                                detail_res['phone'] = child.get_text().strip() or '-'
                                break
                    elif big_index == 1:
                        for index, child in enumerate(big_child.children):
                            if index == 1:
                                detail_res['email'] = child.get_text().strip() or '-'
                                break
                    else:
                        break
            # 公司官网 && 地址
            elif div.get('class') == ['f0', 'clearfix']:
                for big_index, big_child in enumerate(div):
                    if big_index == 0:
                        for index, child in enumerate(big_child.children):
                            if index == 1:
                                detail_res['company_url'] = child.get_text().strip() or '-'
                                break
                    elif big_index == 1:
                        for index, child in enumerate(big_child.children):
                            if index == 1:
                                for small_index, small_child in enumerate(child.children):
                                    if small_index == 0:
                                        detail_res['address'] = small_child.get_text().strip() or '-'
                                        break
                                break
                    else:
                        break
            # 简介
            elif div.get('class') == ['summary']:
                for big_index, big_child in enumerate(div):
                    if big_index == 0:
                        resume = big_child.string
                        if resume:
                            resume = resume.strip()
                        detail_res['resume'] = resume or '-'
                        break
                    else:
                        break
            else:
                continue

        # detail-list:
        detail_list_div = soup.find_all('div', class_="detail-list")
        if not detail_list_div:
            return detail_res

        etc = etree.HTML(search_resp)
        for div in detail_list_div[0].find_all('div'):
            if not div:
                continue

            # detail_res['source'] = '天眼查'
            # detail_res['created_time'] = self.timestamp_to_strftime(time.time())
            if div.get('tyc-event-ch') == 'CompangyDetail.gongshangxinxin':  # 工商信息
                registration_item = dict()
                for index_1, child_1 in enumerate(div.find_all('div', recursive=False)):
                    if index_1 == 1:
                        for index_1_1, child_1_1 in enumerate(child_1):
                            if index_1_1 == 2:
                                for index_tr, tr in enumerate(child_1_1.find_all('tr')):
                                    if index_tr == 0:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 注册资本
                                                detail_res['register_funds'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 实缴资金
                                                detail_res['paidin_funds'] = td.get_text().strip() or '-'
                                    elif index_tr == 1:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 成立日期
                                                detail_res['establish_date'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 经营状态
                                                detail_res['status'] = td.get_text().strip() or '-'
                                    elif index_tr == 2:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 统一社会信用代码
                                                detail_res['credit_code'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 工商注册号
                                                detail_res['registration_number'] = td.get_text().strip() or '-'
                                    elif index_tr == 3:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 纳税人识别号
                                                detail_res['identification_number'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 组织机构代码
                                                detail_res['organization_code'] = td.get_text().strip() or '-'
                                    elif index_tr == 4:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 公司类型
                                                detail_res['company_type'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 行业
                                                detail_res['industry'] = td.get_text().strip() or '-'
                                    elif index_tr == 6:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 营业期限
                                                detail_res['business_term'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 纳税人资质
                                                detail_res['taxpayer_qualification'] = td.get_text().strip() or '-'
                                    elif index_tr == 7:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 人员规模
                                                detail_res['personnel_size'] = td.get_text().strip() or '-'
                                            elif index_td == 3:  # 参保人数
                                                detail_res['insured_num'] = td.get_text().strip() or '-'
                                    elif index_tr == 9:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 注册地址
                                                detail_res['registered_address'] = td.get_text().strip() or '-'
                                    elif index_tr == 10:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 经营范围
                                                detail_res['business_scope'] = td.get_text().strip() or '-'

                        break
                continue

            elif div.get('tyc-event-ch') == 'CompangyDetail.zhuyaorenyuan':  # 主要人员
                people_item = {}
                people_item['company_name'] = detail_res.get('company_name', '')
                # 姓名
                name = etc.xpath('//*[@id="_container_staff"]/div/table/tbody/tr/td[2]/table/tbody/tr/td[2]/a/text()')
                # 职位
                position = etc.xpath('//*[@id="_container_staff"]/div/table/tbody/tr/td[3]/span/text()')
                # 详情地址
                doc_url = etc.xpath(
                    '//*[@id="_container_staff"]/div/table/tbody/tr[1]/td[2]/table/tbody/tr/td[3]/a/@href')

                for people in zip(name, position, doc_url):
                    people_item['name'] = people[0]
                    people_item['position'] = people[1]
                    people_item['doc_url'] = people[2]
                    people_item['created_time'] = self.timestamp_to_strftime(time.time())

                    result = people_insert(people_item)
                    if result.get('status', False):
                        print(result)
                    else:
                        LOG.debug(f'')

                    bixiao_people.find_one_and_update({'doc_url': detail_res.get('doc_url', '')},
                                                      {'$set': people_item}, upsert=True)
                    print(people_item)


            elif div.get('tyc-event-ch') == 'CompangyDetail.gudongxinxi':  # 股东信息
                capital_item = {}
                capital_item['company_name'] = detail_res.get('company_name', '')
                # 股东名称
                title = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr/td[2]/table/tbody/tr/td[2]/a/text()')
                # 标签
                label = etc.xpath(
                    '//*[@id="_container_holder"]/table/tbody/tr/td[2]/table/tbody/tr/td[2]/div/span/text()')
                # 持股比例
                has_rates = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr/td[3]/div/div/span/text()')
                # 认缴出资额
                subscribed_capital = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr/td[4]/div/span/text()')
                # 详情地址
                doc_url = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr/td[2]/table/tbody/tr/td[3]/a/@href')

                for capital in zip(title, label, has_rates, subscribed_capital, doc_url):
                    capital_item['title'] = ''.join(capital[0])
                    capital_item['label'] = ''.join(capital[1])
                    capital_item['has_rates'] = ''.join(capital[2])
                    capital_item['subscribed_capital'] = ''.join(capital[3])
                    capital_item['doc_url'] = capital[4]
                    capital_item['created_time'] = self.timestamp_to_strftime(time.time())
                    bixiao_shareholder.find_one_and_update({'doc_url': detail_res.get('doc_url', '')},
                                                           {'$set': capital_item}, upsert=True)
                    print(capital_item, 'C' * 80)


            elif div.get('tyc-event-ch') == 'CompangyDetail.findNewsCount':  # 新闻舆情
                news_item = {}
                news_item['company_name'] = detail_res.get('company_name', '')
                # 标题
                title = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div/div[1]/a/text()')
                # 内容地址
                info_url = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div/div[1]/a/@href')
                # 来源
                source = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div/div[3]/span[1]/text()')
                # 发布时间
                date_doc = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div/div[3]/span[2]/text()')
                for news_datas in zip(title, info_url, source, date_doc):
                    news_item['title'] = news_datas[0]
                    news_item['info_url'] = news_datas[1]
                    news_item['source'] = news_datas[2]
                    news_item['date_doc'] = news_datas[3]
                    news_item['content'] = self.request_doing(url=news_datas[1], headers=self.headers, params={})
                    news_item['created_time'] = self.timestamp_to_strftime(time.time())

                    print(news_item)
                    bixiao_news.update({'info_url': detail_res.get('info_url', '')}, {'$set': news_item}, upsert=True)


            elif div.get('tyc-event-ch') == 'CompangyDetail.chanpin':  # 产品信息
                product_item = {}
                product_item['company_name'] = detail_res.get('company_name', '')
                # 产品名称
                name = etc.xpath('//*[@id="_container_product"]/table/tbody/tr/td[2]/table'
                                 '/tbody/tr/td[2]/span/text()')
                # 产品简称
                short_name = etc.xpath('//*[@id="_container_product"]/table/tbody/tr/td[3]'
                                       '/span/text()')
                # 产品分类
                type = etc.xpath('//*[@id="_container_product"]/table/tbody/tr/td[4]/span'
                                 '/text()')
                # 领域
                domain = etc.xpath('//*[@id="_container_product"]/table/tbody/tr/td[5]'
                                   '/span/text()')
                # 详情地址
                doc_url = etc.xpath('//*[@id="_container_product"]/table/tbody/tr/td[6]/a/@href')

                for product in zip(name, short_name, type, domain, doc_url):
                    product_item['name'] = product[0]
                    product_item['short_name'] = product[1]
                    product_item['type'] = product[2]
                    product_item['domain'] = product[3]
                    product_item['doc_url'] = product[4]
                    product_item['doc_info'] = self.request_doing(url=product[4], headers=self.headers, params={})
                    product_item['created_time'] = self.timestamp_to_strftime(time.time())

                    print(product_item)
                    bixiao_product.find_one_and_update({'doc_url': detail_res.get('doc_url', '')},
                                                       {'$set': product_item}, upsert=True)


            elif div.get('tyc-event-ch') == 'CompangyDetail.zhaopin':  # 招聘信息
                recruit_item = {}
                recruit_item['company_name'] = detail_res.get('company_name', '')
                opd_date = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[2]'
                                     '/text()')
                position_ = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[3]'
                                      '/text()')
                month_salary = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[4]'
                                         '/text()')
                education = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[5]'
                                      '/text()')
                work_experience = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[6]'
                                            '/text()')
                address = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[7]'
                                    '/text()')
                opd_url = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr/td[8]/a/@href')

                for recruit in zip(opd_date, position_, month_salary, education, work_experience, address, opd_url):
                    recruit_item['opd_date'] = recruit[0]
                    recruit_item['position_'] = recruit[1]
                    recruit_item['month_salary'] = recruit[2]
                    recruit_item['education'] = recruit[3]
                    recruit_item['work_experience'] = recruit[4]
                    recruit_item['address'] = recruit[5]
                    recruit_item['opd_url'] = recruit[6]
                    recruit_item['created_time'] = self.timestamp_to_strftime(time.time())

                    print(recruit_item, 'P' * 80)
                    bixiao_recruit.find_one_and_update({'opd_url': detail_res.get('opd_url', '')},
                                                       {'$set': recruit_item}, upsert=True)


            elif div.get('tyc-event-ch') == 'CompangyDetail.lishiwangzhanbeian':  # ICP备案
                record_item = {}
                record_item['company_name'] = detail_res.get('company_name', '')
                # 审核日期
                opd_date = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[2]'
                                     '/span/text()')
                # 网站名称
                web_name = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[3]'
                                     '/span/text()')
                # 网站首页
                index_url = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[4]/div/'
                                      'a/@href')
                # 域名
                domain_name = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[5]'
                                        '/text()')
                # 网站备案/许可证号
                website_filing = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[6]/'
                                           'span/text()')

                for record in zip(opd_date, web_name, index_url, domain_name, website_filing):
                    record_item['opd_date'] = record[0]
                    record_item['web_name'] = record[1]
                    record_item['index_url'] = record[2]
                    record_item['domain_name'] = record[3]
                    record_item['website_filing'] = record[4]
                    record_item['created_time'] = self.timestamp_to_strftime(time.time())

                    res = record_icp_insert(record_item)
                    if res.get('status', False):
                        print(res)
                    else:
                        LOG.debug(f'企业年报入库异常: {res.get("msg")}...')

                    # print(record_item, 'M' * 80)
                    # bixiao_record_icp.find_one_and_update({'index_url': detail_res.get('index_url', '')},
                    #                                       {'$set': record_item}, upsert=True)

            elif div.get('tyc-event-ch') == 'CompangyDetail.rongzilishi':     # 融资历程
                financing_item = dict()
                financing_item['company_name'] = detail_res.get('company_name', '')
                # 披露日期
                opd_date = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[2]/text()')
                # 交易金额
                change_money = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[3]/text()')
                # 融资轮次
                financing_round = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[4]/div[1]/text()')
                # 估值
                valuation = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[5]/text()')
                # 比例
                proportion = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[6]/text()')
                # 投资方
                investor = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[7]/div/a/text()')
                # 新闻来源
                news_source = etc.xpath('//*[@id="_container_rongzi"]/table/tbody/tr/td[8]/div/text()')

                for financing in zip(opd_date, change_money, financing_round, valuation,
                                     proportion, investor, news_source):
                    financing_item['opd_date'] = financing[0]
                    financing_item['change_money'] = financing[1]
                    financing_item['financing_round'] = financing[2]
                    financing_item['valuation'] = financing[3]
                    financing_item['proportion'] = financing[4]
                    financing_item['investor'] = financing[5]
                    financing_item['news_source'] = financing[6]
                    financing_item['created_time'] = self.timestamp_to_strftime(time.time())

                    print(financing_item, 'F'*80)
                    res = financing_insert(financing_item)
                    if res.get('status', False):
                        print(res)
                    else:
                        LOG.debug(f'融资历程入库异常: {res.get("msg")}...')

            elif div.get('tyc-event-ch') == 'CompangyDetail.nianbao':     # 企业年报
                reports_item = dict()
                reports_item['company_name'] = detail_res.get('company_name', '')
                # 年报
                reports = etc.xpath('//*[@id="web-content"]/div/div/div[5]/div[1]/div/div[2]/div[1]/div[15]/div[2]'
                                    '/div/table/tbody/tr/td[2]/text()')
                # 详情地址
                operation = etc.xpath('//*[@id="web-content"]/div/div/div[5]/div[1]/div/div[2]/div[1]/div[15]/div[2]'
                                      '/div/table/tbody/tr/td[3]/a/@href')
                for annual in zip(reports, operation):
                    reports_item['reports'] = annual[0]
                    reports_item['operation'] = annual[1]
                    reports_item['reports_info'] = self.request_doing(url=operation, headers=self.headers, params={})
                    reports_item['created_time'] = self.timestamp_to_strftime(time.time())

                    print(reports_item, '?'*80)
                    res = reports_insert(reports_item)
                    if res.get('status', False):
                        print(res)
                    else:
                        LOG.debug(f'企业年报入库异常: {res.get("msg")}...')


        print(detail_res, '%' * 80)
        bixiao_business.find_one_and_update({'company_name': detail_res.get('company_name', '')},
                                            {'$set': detail_res}, upsert=True)



    def timestamp_to_strftime(self, timestamp, format='%Y-%m-%d %H:%M:%S'):

        """
        时间戳转日期
        timestamp：要转换的时间戳
        format：日期格式化字符串

        :return 返回日期格式字符串
        """
        ltime = time.localtime(timestamp)
        time_str = time.strftime(format, ltime)
        return time_str

    def request_doing(self, url: str = None, headers: dict = dict, Method: int = 1, data: dict = dict,
                      params: dict = dict):
        is_su = False
        for tes in range(6):
            if Method == 1:
                industry_list = self.ss_request.get(
                    url=url,
                    headers=headers,
                    params=params,
                    verify=False,
                    timeout=5
                )
            else:
                industry_list = self.ss_request.post(
                    url=url,
                    headers=headers,
                    data=data,
                    verify=False,
                    timeout=5
                )
            if industry_list.status_code == 200:
                is_su = True
                break

        if not is_su:
            return False
        return industry_list.text
