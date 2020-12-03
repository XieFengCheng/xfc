# -*- coding: utf-8 -*-
import requests
import redis
from proxypool.storages.redis import RedisClient
from requests.exceptions import ProxyError
from tomorrow import threads

class Checker(object):
    def __init__(self):
        """
        init redis
        """
        self.redis = RedisClient()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                          ') Chrome/83.0.4103.97 Safari/537.36'
        }

    def request_check(self, proxy):
        proxies = {
            'http': 'http://{}'.format(proxy),
            'https': 'https://{}'.format(proxy)
        }
        try:
            res_ip = requests.get('https://www.baidu.com', headers=self.headers, proxies=proxies, timeout=10)
            if res_ip.status_code == 200:
                return proxy
            else:
                return None
        except ProxyError:
            return None

    def read(self):
        get_vlas = self.redis.db.zrange('proxies:universal', 0, 100)
        print(get_vlas)
        print(len(get_vlas))
        for all_ip in get_vlas:
            vals = self.request_check(all_ip)
            if vals:
                print(all_ip, '&'*80)
            else:
                print('Q'*80)
                print(all_ip, 'P'*80)
                self.redis.db.zrem('proxies:universal', all_ip)


if __name__ == '__main__':
    while True:
        obj = Checker()
        obj.read()
