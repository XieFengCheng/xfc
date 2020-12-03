#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------
describe:
    

--------------------------------------------------------------
"""

# ------------------------------------------------------------
# usage: /usr/bin/python http.py
# ------------------------------------------------------------
import requests
import json
import time


from deploy.config import IS_PROXY_RUN, PROXY_API
from deploy.utils.utils import random_sleep
from deploy.utils.logger import logger as LOG
from libs.get_proxy import get_proxy


def api_post(url, headers={}, data={},
             retry=1, resptype='json', **kwargs):
    """
    http post
    :param url: url
    :param headers: headers
    :param data: data
    :return: response
    """
    if not url:
        return False, 'api_post url is not allow null'

    if isinstance(data, dict):
        data = json.dumps(data)
    if not isinstance(headers, dict):
        headers = json.dumps(headers)

    try:
        if not IS_PROXY_RUN:
            response = requests.post(url=url, headers=headers,
                                     data=data, timeout=5)
        else:
            random_ip = get_random_proxy()
            proxies = {'http': random_ip} if random_ip else {}
            response = requests.post(url=url, headers=headers,
                                     data=data, timeout=5, proxies=proxies)
    except Exception as e:
        if retry <= 3:
            random_sleep(1, 1.5)
            api_post(url=url,
                     headers=headers,
                     data=data,
                     retry=retry + 1,
                     resptype='json')
        else:
            raise Exception('http api_post error: %s' % e)
    else:
        respcode = response.status_code
        if respcode != 200:
            return False, 'api_post response status code is: %s' % respcode
        elif respcode == 200 and resptype == 'raw':
            return True, response.raw
        elif respcode == 200 and resptype == 'content':
            return True, response.content
        elif respcode == 200 and resptype == 'json':
            return True, response.json()
        else:
            return True, response.text


def api_get(url,  headers={}, data={},
            retry=1, resptype='json', **kwargs):
    """
    http get
    :param url: url
    :param headers: headers
    :param data: data
    :return: response
    """
    if not url:
        return False, 'api_get url is not allow null'

    if isinstance(data, dict):
        data = json.dumps(data)
    if not isinstance(headers, dict):
        headers = json.dumps(headers)

    try:

        # if response.status_code != 200:
        random_ip = get_proxy()
        proxies = random_ip if random_ip else {}
        response = requests.get(url=url, headers=headers,
                                data=data, timeout=5, proxies=proxies)
        # if not IS_PROXY_RUN:
        #     response = requests.get(url=url, headers=headers,
        #                             data=data, timeout=5)
        # else:
        #     random_ip = get_random_proxy()
        #     proxies = {'http': random_ip} if random_ip else {}
        #     response = requests.get(url=url, headers=headers,
        #                             data=data, timeout=5, proxies=proxies)
    except Exception as e:
        if retry <= 3:
            random_sleep(1, 1.5)
            api_get(url, headers, data, retry=retry + 1, resptype='json')
        else:
            raise Exception(u'api_get error: %s' % e)
    else:
        respcode = response.status_code
        if respcode != 200:
            return False, 'api_get response status code is: %s' % respcode
        elif respcode == 200 and resptype == 'raw':
            return True, response.raw
        elif respcode == 200 and resptype == 'content':
            return True, response.content
        elif respcode == 200 and resptype == 'json':
            return True, response.json()
        else:
            return True, response.text


def get_random_proxy():
    """
    get random proxy from proxypool
    :return: proxy
    """
    try:
        res = requests.get(PROXY_API)
        return res.text.strip() if res.status_code ==200 else ''
    except:
        return ''

