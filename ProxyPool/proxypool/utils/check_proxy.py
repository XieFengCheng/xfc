# -*- coding: utf-8 -*-
import requests
from proxypool.setting import TEST_URL, TEST_HEADERS
from proxypool.storages.redis import RedisClient
from requests.exceptions import ConnectionError, Timeout, HTTPError, ConnectTimeout

def checking(proxy):
    ocj = RedisClient()
    proxies = {
        'http': 'http://{}'.format(proxy),
        'https': 'https://{}'.format(proxy)
    }
    try:
        res_proxy = requests.get(TEST_URL, headers=TEST_HEADERS, proxies=proxies, verify=False, timeout=100)
        if res_proxy.status_code == 200:
            return proxy
        else:
            ocj.decrease(proxy)
            return None
    except ConnectionError and Timeout and HTTPError:
        ocj.decrease(proxy)
        return None
