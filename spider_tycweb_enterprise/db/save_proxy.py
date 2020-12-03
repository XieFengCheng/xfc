# -*- coding: utf-8 -*-
import requests
import random
import json
import os
import sys
sys.path.append('/spider_tycweb_enterprise/')
from db.client_db import proxy_ip, admin_heap, login_ip
from db.get_path import get_path



class Proxy(object):
    def __init__(self):
        # self.get_proxy = 'http://47.103.37.73:8001/v1/info?username=zmhttp829052&remark=dx320301_2'
        self.get_proxy = 'http://47.103.37.73:8001/v1/info?username=tuoluo&remark=dx341701_3'
        # self.dial_set = 'http://47.103.37.73:8001/v1/dialer?username=zmhttp829052&remark=dx320301_2'
        self.dial_set = 'http://47.103.37.73:8001/v1/dialer?username=tuoluo&remark=dx341701_3'
        self.proxy = {
            'https': 'https://{}'
        }


    def index_request(self):
        get_proxy = requests.get(self.get_proxy, timeout=5)
        print(type(json.loads(get_proxy.text)))


        if (json.loads(get_proxy.text)) and ((json.loads(get_proxy.text)).get('success', False)):
            ip_u = [f'{i["s5_ip"]}:{i["s5_port"]}-{i["ipid"]}' for i in (json.loads(get_proxy.text)).get('data')]
            print(ip_u)
            # for ip_proxy in ip_u:
            #     vals = proxy_ip.lpush('proxy_pool', ip_proxy)
            #     if vals:
            #         login_ip.lpush('login_ip', ip_proxy.split('-')[0])
            # return True




class VipUser(object):
    def __init__(self):
        pass


    def read_file(self):
        print(get_path, '#'*80)
        # with open(r'D:\tyc_project\spider_tycweb_enterprise-master\db\vip_user_pd.txt', 'r') as rf:
        with open(get_path, 'r') as rf:
            info_user = rf.read()
        user_list = [i.replace('鍙凤細', '') for i in info_user.split('\n') if '鍙凤細' in i]
        pd_list = [i.replace('瀵嗭細', '') for i in info_user.split('\n') if '瀵嗭細' in i]
        vip_item = dict(map(lambda x,y:[x,y],user_list,pd_list))
        print(vip_item)
        # for vip_admin in vip_item:
        #     admin_heap.lpush('admin_heap', vip_admin+'-'+vip_item[vip_admin])
        # return True


def main():
    obj = Proxy()
    proxy = obj.index_request()

    obj = VipUser()
    vip_user = obj.read_file()

    return proxy, vip_user



if __name__ == '__main__':
    import time
    while True:
        func = main()
        print(func)
        time.sleep(20)

