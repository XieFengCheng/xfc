# -*- coding: utf-8 -*-
import requests


request_url = 'http://ifconfig.me/ip'

proxy = {
    'https': '',
}

res_html = requests.get(request_url, proxies=proxy, timeout=5).text

print(res_html)