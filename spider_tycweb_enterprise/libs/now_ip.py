# -*- coding: utf-8 -*-
import requests
import re

header_form = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                  ') Chrome/83.0.4103.97 Safari/537.36',
}

def now_ip():

    res_ip = requests.get(url='https://202020.ip138.com/', headers=header_form)
    get_ip = (re.findall(r'target="_blank">(.*?)</a>]', res_ip.text))[0]
    return get_ip



now_ip()