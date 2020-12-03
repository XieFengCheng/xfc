# -*- coding: utf-8 -*-
from urllib import parse
from bs4 import BeautifulSoup

from deploy.config import RUN_MODE, TYC_DETAIL_API, \
    TYC_SEARCH_API, TYC_COOKIE
from deploy.utils.http import api_get
from deploy.utils.logger import logger as LOG
from deploy.utils.utils import random_sleep
from libs.get_cookies import cookies_get



class GetCompanyList(object):
    def __init__(self):
        super(object, self).__init__()
        self.MAX_PAGE = 30
        self._init_header()

    def _init_header(self):
        self.headers = {
            # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "version": "TYC-XCX-WX",
            "Host": "www.tianyancha.com",
            "Cookie": cookies_get(),
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document"
        }

    from tomorrow import threads
    @threads(2)
    def work_by_key(self, key):
        ret_res = list()
        if not key:
            LOG.error("【%s】key is null, no work." % RUN_MODE)
            return ret_res

        # page
        for page in range(1, self.MAX_PAGE, 1):
            url = '%s/p%s?key=%s' % (TYC_SEARCH_API, page, parse.quote(key))
            print(url)
            print(cookies_get())
            self.headers['Cookie'] = cookies_get()
            is_ok, search_resp = api_get(url=url,
                                         headers=self.headers,
                                         data={},
                                         resptype='text')
            if not is_ok:
                continue

            with open('company_list.html', 'w', encoding='utf-8') as wf:
                wf.write(search_resp)
            soup = BeautifulSoup(search_resp, 'lxml')
            tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})

            def while_req(url):
                sub_is_ok, sub_search_resp = api_get(url=url,
                                         headers=self.headers,
                                         data={},
                                         resptype='text')
                return sub_is_ok, sub_search_resp

            # 添加手动验证功能
            if len(tags) == 0:
                while 1:
                    if is_ok and len(tags) > 0:
                        break
                    else:
                        LOG.critical('验证############### %s ###############' % url)
                        random_sleep(20,25)
                        self.headers['Cookie'] = cookies_get()
                        is_ok, search_resp = while_req(url)
                        soup = BeautifulSoup(search_resp, 'lxml')
                        tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})

            for tag in tags:
                if not tag or not tag.attrs.get('href'):
                    continue

                res_dict = dict()
                res_dict['tyt_url'] = tag.get('href').strip()
                res_dict['name'] = tag.get_text().strip()

                self.save_list(tag.get('href').strip()+'-'+tag.get_text().strip())
                # print(res_dict['name'], res_dict['tyt_url'], str(True if res_dict else False))
                print(res_dict)
                ret_res.append(res_dict)
                random_sleep(1, 2.5)

    def save_list(self, url_link):
        import redis

        pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=15)
        conn = redis.Redis(connection_pool=pool)
        link_list = conn.lrange('company_list', 0, -1)
        utf_list = [i.decode() for i in link_list]
        if url_link not in utf_list:
            return conn.lpush('company_list', url_link)



keywords = ['工程行业','安防行业','家居装饰行业','室内设计','摄影拍摄','制造业/仪器表行业',
            '物流行业','IT软件/互联网','金融行业','房地产','传媒行业','旅游行业','房地产/建筑/装修行业']
for i in keywords:
    func = GetCompanyList().work_by_key(i)
    print(func)