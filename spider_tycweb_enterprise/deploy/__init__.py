#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------
describe:
    

--------------------------------------------------------------
"""

# ------------------------------------------------------------
# usage: /usr/bin/python __init__.py
# ------------------------------------------------------------
import os
import sys

from deploy.config import NAME, VERSION, KEYS, DEBUG,\
    STORE_DB, STORE_EXCEL, OUTPUT_BASE_DIR, RUN_MODE, STORE_EXCEL
from deploy.utils.logger import logger as LOG
from deploy.utils.base_class import BASECLASS
from deploy.client.tianyancha import TianYanChaClient
# from request.get_company_list import GetCompanyList
# from request.checking import GetCompanyList
from deploy.utils.to_excel import ToExcel
from deploy.utils.utils import get_now, get_excel_folder
from deploy.services.enterprise import EnterpriseService


# 支持协程
# from gevent import monkey; monkey.patch_all()
# import gevent


MODES = ['single', 'gevent', 'process']
ATTRS_DICT = {
    'name': "名称",
    'email': "邮箱",
    'phone': "电话",
    'tyt_url': "天眼查URL",
    'company_url': "公司官网",
    'address': "地址",
    'register_funds': "注册资金",
    'paidin_funds': "实缴资金",
    'establish_date': "注册日期",
    'status': "经营状态",
    'credit_code': "信用代码",
    'registration_number': "工商注册号",
    'identification_number': "纳税人识别号",
    'organization_code': "organization_code",
    'company_type': "公司类型",
    'industry': "所属行业",
    'business_term': "营业期限",
    'taxpayer_qualification': "纳税人资质",
    'personnel_size': "人员规模",
    'insured_num': "参保人数",
    'resume': "简述",
    'registered_address': "注册地址",
    'business_scope': "经营范围",
}


class SpiderTYCClass(BASECLASS):
    """
    It is class
    to use spider tianyancha enterprise data
    """

    def __init__(self):
        self.name = NAME
        self.version = VERSION
        self.keys = KEYS
        if not self.keys:
            self._die('KEYS is null, exit')
        self.debug = DEBUG
        self.store_excel = STORE_EXCEL
        self.store_db = STORE_DB
        self.store_excel_dir = OUTPUT_BASE_DIR
        self.tyc_client = TianYanChaClient()
        # self.tyc_client = GetCompanyList()
        self.excel_client = ToExcel()
        self.enterprise_service = EnterpriseService()
        self.__init_return_res()

    def __init_return_res(self):
        self.ret_res_list = list()


    def _die(self, message: str = None):
        if message:
            LOG.critical(message)
        os._exit(0)

    def _print_info(self, message):
        LOG.info('=' * 20 + message + '=' * 20)

    def single_run(self):
        for key in self.keys:
            if not key:
                continue
            print(key, '&'*80)
            self._print_info(key)
            self.tyc_client.work_by_key(key)
            # self.ret_res_list.extend(self.tyc_client.work_by_key(key))

        # if STORE_EXCEL:
        #     to_excel_name = os.path.join(get_excel_folder(),
        #                                  '%s-%s.xls' % (get_now(), '_'.join(self.keys)))
        #     self.excel_client.to_excel(self.ret_res_list, ATTRS_DICT,
        #                                to_excel_name)
        #     LOG.info(to_excel_name)
        # print(self.ret_res_list, '@'*100)
        # if STORE_DB:
        #     self.enterprise_service.adds(datas=self.ret_res_list)
        #     LOG.info('DB is finished.......')



    def process_run(self):
        pass

    def gevent_run(self):
        jobs = list()
        for key in self.keys:
            if not key:
                continue
        #     jobs.append(gevent.spawn(self.service.aprv_new, content, pid))
        # gevent.joinall(jobs)

    def init_run(self):
        if not RUN_MODE or RUN_MODE not in MODES:
            self._die('run node nit in [single, gevent, process], '
                      'please to set run mode at etc/config.yaml file.')

        if RUN_MODE == 'gevent':
            self.gevent_run()
        elif RUN_MODE == 'process':
            self.process_run()
        else:
            self.single_run()


def start():
    LOG.info('%s start run......' % NAME)
    SpiderTYCClass().init_run()
    LOG.info('%s end run......' % NAME)


# start()