# # -*- coding: utf-8 -*-
# from urllib import parse
# from bs4 import BeautifulSoup
# 
# from deploy.config import RUN_MODE, TYC_DETAIL_API, \
#     TYC_SEARCH_API, TYC_COOKIE
# from deploy.utils.http import api_get
# from deploy.utils.logger import logger as LOG
# from deploy.utils.utils import random_sleep
# 
# # from deploy.services.redis_client import main
# 
# 
# class GetCompanyList(object):
#     def __init__(self):
#         super(object, self).__init__()
#         self.MAX_PAGE = 5
#         self._init_header()
# 
#     def _init_header(self):
#         self.headers = {
#             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
#             "version": "TYC-XCX-WX",
#             "Host": "www.tianyancha.com",
#             "Cookie": TYC_COOKIE,
#             "Connection": "keep-alive",
#             "Sec-Fetch-Dest": "document"
#         }
# 
#     def work_by_key(self, key):
#         print(type(TYC_COOKIE), TYC_COOKIE, '@'*80)
#         print(type(main()), main(), '$'*80)
#         # ret_res = list()
#         # if not key:
#         #     LOG.error("【%s】key is null, no work." % RUN_MODE)
#         #     return ret_res
#         # url = 'https://antirobot.tianyancha.com/captcha/verify?return_url=https%3A%2F%2Fwww.tianyancha.com%2Fsearch%3Fkey%3D%25E5%25B7%25A5%25E7%25A8%258B%25E8%25A1%258C%25E4%25B8%259A&rnd='
#         #
#         # # page
#         # is_ok, search_resp = api_get(url=url,
#         #                              headers=self.headers,
#         #                              data={},
#         #                              resptype='text')
#         #
#         #
#         # with open('add_code.html', 'w', encoding='utf-8') as wf:
#         #     wf.write(search_resp)
#         # soup = BeautifulSoup(search_resp, 'lxml')
#         # tags = soup.find_all('a', attrs={"tyc-event-ch": "CompanySearch.Company"})
#         #
#         # def while_req(url):
#         #     sub_is_ok, sub_search_resp = api_get(url=url,
#         #                              headers=self.headers,
#         #                              data={},
#         #                              resptype='text')
#         #     return sub_is_ok, sub_search_resp
# 
# 
# 
