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
                          bixiao_news, bixiao_product, bixao_phone_emial,
                          bixiao_recruit, bixiao_record_icp)
from libs.get_cookies import cookies_get
from model_list.model import _insert


class TianYanChaClient(object):
    """
    tianyancha client
    """

    def __init__(self):
        super(object, self).__init__()
        self.MAX_PAGE = 2
        self._init_header()
        self.count = 1

    def _init_header(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko"
                          ") Chrome/83.0.4103.116 Safari/537.36",
            "version": "TYC-XCX-WX",
            "Host": "www.tianyancha.com",
            "Cookie": cookies_get(),
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document"
        }

    def work_by_key(self, key):
        print(key, '@'*100)
        ret_res = list()
        if not key:
            LOG.error("【%s】key is null, no work." % RUN_MODE)
            return ret_res


        # page
        is_page = False
        for ct in range(9):
            url = '%s/p%s?key=%s' % (TYC_SEARCH_API, 1, parse.quote(key))
            is_ok, search_resp = api_get(url=url,
                                         headers=self.headers,
                                         data={},
                                         resptype='text')
            self.headers['Cookie'] = cookies_get()
            if is_ok:
                is_page = True
                break
        page_vlas = 200
        if not is_page:
            page_vlas = 200
        else:
            et_late = etree.HTML(search_resp)
            page_num = [i.xpath('./li/a/text()')[-2] for i in et_late.xpath(
                '//div[@class="result-footer"]/div[@class=" search-pager"]/ul')]
            if page_num:
                page_vlas = str(page_num[0]).replace('.', '')

        LOG.critical(f'搜索关键词为：{key}, 总页面：{page_vlas}------------------------')
        print(f'搜索关键词为：{key}, 总页面：{page_vlas}------------------------')
        # 公司列表
        for page in range(1, int(page_vlas), 1):
            self.headers['Cookie'] = cookies_get()
            url = '%s/p%s?key=%s' % (TYC_SEARCH_API, page, parse.quote(key))
            print(url, 'Q'*80)
            is_ok, search_resp = api_get(url=url,
                                         headers=self.headers,
                                         data={},
                                         resptype='text')
            if not is_ok:
                continue
            soup = BeautifulSoup(search_resp, 'lxml')
            tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})

            def while_req(url):
                self.headers['Cookie'] = cookies_get()
                sub_is_ok, sub_search_resp = api_get(url=url,
                                         headers=self.headers,
                                         data={},
                                         resptype='text')
                return sub_is_ok, sub_search_resp

            HTNL = etree.HTML(search_resp)
            print(HTNL.xpath('//*[@id="web-content"]/div/div[1]/div[3]/div[2]/div[1]/div/div[3]/div[1]/a/text()'), 'A'*80)

            # 添加手动验证功能
            if len(tags) == 0:
                while 1:
                    if is_ok and len(tags) > 0:
                        break
                    else:
                        print(url)
                        LOG.critical('验证############### %s ###############' % url)
                        random_sleep(20,25)
                        self.headers['Cookie'] = cookies_get()
                        is_ok, search_resp = while_req(url)
                        soup = BeautifulSoup(search_resp, 'lxml')
                        tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})
            eto = etree.HTML(search_resp)
            user_name = eto.xpath('//div[@nav-type="user"]/a/text()')

            is_success = False
            for i in range(9):
                if not ''.join(user_name):
                    self.headers['Cookie'] = cookies_get()
                    is_ok, search_resp = while_req(url)
                    soup = BeautifulSoup(search_resp, 'lxml')
                    tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})
                    is_success = True
                    break
            if is_success:
                for tag in tags:
                    if not tag or not tag.attrs.get('href'):
                        continue

                    res_dict = dict()
                    res_dict['tyt_url'] = tag.get('href').strip()
                    res_dict['name'] = tag.get_text().strip()
                    res_dict['company_id'] = str(tag.get('href')).split('/')[-1]
                    res_dict['label_index'] = str(key)
                    res_dict['rquest_url'] = url
                    res_dict['source'] = '天眼查'
                    res_dict['created_time'] = str(datetime.now())
                    result = _insert(res_dict)
                    if result.get('status', False):
                        c_id = str(result.get('_id'))
                        try:
                            # detail_res = self.detail_by_url(res_dict.get('tyt_url'))

                            self.detail_by_url(res_dict.get('tyt_url'), c_id)
                        except:
                            try:
                                self.detail_by_url(res_dict.get('tyt_url'), c_id)
                            except:
                                pass

                    ret_res.append(res_dict)
                    random_sleep(1, 2.5)
            #     break
            # break
        return ret_res


    def get_detail_url(self, comp_url: str, index: str):
        detail_res = dict()
        if not comp_url:
            return detail_res

        is_ok, search_resp = api_get(url=comp_url,
                                     headers=self.headers,
                                     data={},
                                     resptype='text')
        with open('agan_demo{}.html'.format(index), 'w', encoding='utf-8') as wf:
            wf.write(search_resp)

    #
    def detail_by_url(self, comp_url: str, obj_id: str):
        print(self.count, comp_url, obj_id, '$'*80)
        detail_res = dict()
        if not comp_url:
            return detail_res

        is_ok, search_resp = api_get(url=comp_url,
                                     headers=self.headers,
                                     data={},
                                     resptype='text')
        if not is_ok:
            return detail_res


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
                contact_item['c_id'] = obj_id
                contact_item['company_name'] = detail_res.get('company_name', '')
                contact_item['report_year'] = contact[0]
                contact_item['phone'] = contact[1]
                contact_item['email'] = contact[-1]
                contact_item['date_time'] = datetime.now()
                bixao_phone_emial.find_one_and_update({'c_id': obj_id}, {'$set': contact_item}, upsert=True)

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
                if is_ok and detail_div:
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

        detail_res['c_id'] = obj_id
        etc = etree.HTML(search_resp)
        for div in detail_list_div[0].find_all('div'):
            if not div:
                continue

            if div.get('tyc-event-ch') == 'CompangyDetail.gongshangxinxin':     # 工商信息
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
                                            if index_td == 1:   # 人员规模
                                                detail_res['personnel_size'] = td.get_text().strip() or '-'
                                            elif index_td == 3:   # 参保人数
                                                detail_res['insured_num'] = td.get_text().strip() or '-'
                                    elif index_tr == 9:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:     # 注册地址
                                                detail_res['registered_address'] = td.get_text().strip() or '-'
                                    elif index_tr == 10:
                                        for index_td, td in enumerate(tr.find_all('td')):
                                            if index_td == 1:  # 经营范围
                                                detail_res['business_scope'] = td.get_text().strip() or '-'


                        break
                continue

            elif div.get('tyc-event-ch') == 'CompangyDetail.zhuyaorenyuan':       # 主要人员
                people_item = {}
                people_item['c_id'] = obj_id
                people_item['company_name'] = detail_res.get('company_name', '')
                # 姓名
                people_item['name'] = etc.xpath('//*[@id="_container_staff"]/div/table/tbody/tr[1]/td[2]/table/tbody/tr/td[2]/a/text()')[0]
                # 职位
                people_item['position'] = etc.xpath('//*[@id="_container_staff"]/div/table/tbody/tr[1]/td[3]/span/text()')[0]
                bixiao_people.find_one_and_update({'c_id': obj_id},
                                                  {'$set': people_item}, upsert=True)
                print(people_item)
                for people_vals in people_item:
                    if not people_item[people_vals]:
                        LOG.info(f'主要人员数据匹配异常：{people_item}, 请求地址：{comp_url}')

            elif div.get('tyc-event-ch') == 'CompangyDetail.gudongxinxi':     # 股东信息
                capital_item = {}
                capital_item['c_id'] = obj_id
                capital_item['company_name'] = detail_res.get('company_name', '')
                # 股东名称
                title = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[2]/a/text()')
                # 标签
                label = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr[1]/td[2]/table/tbody/tr/td[2]/div/span/text()')
                # 持股比例
                has_rates = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr[1]/td[3]/div/div/span/text()')
                # 认缴出资额
                subscribed_capital = etc.xpath('//*[@id="_container_holder"]/table/tbody/tr[1]/td[4]/div/span/text()')

                capital_item['title'] = ''.join(title)
                capital_item['label'] = ''.join(label)
                capital_item['has_rates'] = ''.join(has_rates)
                capital_item['subscribed_capital'] = ''.join(subscribed_capital)
                bixiao_shareholder.find_one_and_update({'c_id': obj_id},
                                                       {'$set': capital_item}, upsert=True)
                print(capital_item, 'C'*80)


            elif div.get('tyc-event-ch') == 'CompangyDetail.findNewsCount':     # 新闻舆情
                news_item = {}
                news_item['c_id'] = obj_id
                news_item['company_name'] = detail_res.get('company_name', '')
                # 标题
                news_item['title'] = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div[1]/div[1]/a/text()')[0]
                # 内容地址
                news_item['info_url'] = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div[1]/div[1]/a/@href')[0]
                # 来源
                news_item['source'] = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div[1]/div[3]/span[1]/text()')[0]
                # 发布时间
                news_item['date_doc'] = etc.xpath('//*[@id="_container_findNewsCount"]/div[1]/div[1]/div[1]/div[3]/span[2]/text()')[0]
                print(news_item)
                bixiao_news.update({'c_id': obj_id}, {'$set': news_item}, upsert=True)
                for news_vals in news_item:
                    if not news_item[news_vals]:
                        LOG.info(f'新闻舆情数据匹配异常：{news_item}, 请求地址：{comp_url}')

            elif div.get('tyc-event-ch') == 'CompangyDetail.chanpin':       # 产品信息
                product_item = {}
                product_item['c_id'] = obj_id
                product_item['company_name'] = detail_res.get('company_name', '')
                # 产品名称
                product_item['name'] = etc.xpath('//*[@id="_container_product"]/table/tbody/tr[1]/td[2]/table'
                                                 '/tbody/tr/td[2]/span/text()')[0]
                # 产品简称
                product_item['short_name'] = etc.xpath('//*[@id="_container_product"]/table/tbody/tr[1]/td[3]'
                                                       '/span/text()')[0]
                # 产品分类
                product_item['type'] = etc.xpath('//*[@id="_container_product"]/table/tbody/tr[1]/td[4]/span'
                                                 '/text()')[0]
                # 领域
                product_item['domain'] = etc.xpath('//*[@id="_container_product"]/table/tbody/tr[1]/td[5]'
                                                   '/span/text()')[0]
                print(product_item)
                bixiao_product.find_one_and_update({'c_id': obj_id},
                                                   {'$set': product_item}, upsert=True)
                for product_vals in product_item:
                    if not product_item[product_vals]:
                        LOG.info(f'产品信息数据匹配异常：{product_item}, 请求地址：{comp_url}')

            elif div.get('tyc-event-ch') == 'CompangyDetail.zhaopin':       # 招聘信息
                recruit_item = {}
                recruit_item['c_id'] = obj_id
                recruit_item['company_name'] = detail_res.get('company_name', '')
                recruit_item['opd_date'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[2]'
                                                     '/text()')[0]
                recruit_item['position_'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[3]'
                                                      '/text()')[0]
                recruit_item['month_salary'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[4]'
                                                         '/text()')[0]
                recruit_item['education'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[5]'
                                                      '/text()')[0]
                recruit_item['work_experience'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[6]'
                                                            '/text()')[0]
                recruit_item['address'] = etc.xpath('//*[@id="_container_baipin"]/table/tbody/tr[1]/td[7]'
                                                    '/text()')[0]
                print(recruit_item, 'P'*80)
                bixiao_recruit.find_one_and_update({'c_id': obj_id},
                                                   {'$set': recruit_item}, upsert=True)
                for recruit_vals in recruit_item:
                    if not recruit_item[recruit_vals]:
                        LOG.info(f'招聘信息数据匹配异常：{recruit_item}, 请求地址：{comp_url}')

            elif div.get('tyc-event-ch') == 'CompangyDetail.lishiwangzhanbeian':        # ICP备案
                record_item = {}
                record_item['c_id'] = obj_id
                record_item['company_name'] = detail_res.get('company_name', '')
                record_item['opd_date'] = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[2]'
                                                    '/span/text()')[0]
                record_item['web_name'] = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[3]'
                                                    '/span/text()')[0]
                record_item['index_url'] = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[4]/div/'
                                                     'a/@href')[0]
                record_item['domain_name'] = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[5]'
                                                       '/text()')[0]
                record_item['website_filing'] = etc.xpath('//*[@id="_container_pastIcpList"]/table/tbody/tr/td[6]/'
                                                          'span/text()')[0]
                print(record_item, 'M'*80)
                bixiao_record_icp.find_one_and_update({'c_id': obj_id},
                                                   {'$set': record_item}, upsert=True)
                for record_vals in record_item:
                    if not record_item[record_vals]:
                        LOG.info(f'ICP备案数据匹配异常：{record_item}, 请求地址：{comp_url}')


        print(detail_res, '%'*80)
        bixiao_business.find_one_and_update({'c_id': obj_id},
                                            {'$set': detail_res}, upsert=True)
        return detail_res
