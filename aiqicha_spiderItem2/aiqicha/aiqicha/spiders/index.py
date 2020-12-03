# -*- coding: utf-8 -*-
import requests
import json
from tomorrow import threads


start_url = 'https://aiqicha.baidu.com/s/l?q=%E6%AD%A6%E6%B1%89%E5%B8%82&t=&s=10&p=3&o=0&f=%7B%7D'

header_form = {
    'Host':'aiqicha.baidu.com',
    'Connection':'keep-alive',
    'Accept':'application/json, text/plain, */*',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    'X-Requested-With':'XMLHttpRequest',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-Mode':'cors',
    'Sec-Fetch-Dest':'empty',
    'Referer':'https://aiqicha.baidu.com/s?q=%E6%AD%A6%E6%B1%89%E5%B8%82&t=3&p=5',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'zh-CN,zh;q=0.9',
}


# @threads(8)
def start_request():
    res_html = requests.get(
        url=start_url,
        headers=header_form,
        verify=False,
    )
    print(res_html.status_code)
    print(json.loads(res_html.text).get('data').keys())
    print(json.loads(res_html.text).get('data').get('resultList'))
    print(len(json.loads(res_html.text).get('data').get('resultList')))
    total = json.loads(res_html.text).get('data').get('totalNumFound')
    company_list = json.loads(res_html.text).get('data').get('resultList')
    if len(company_list) > 0 and int(total) > 0:
        list_item = {}
        for vals in company_list:
            list_item['title'] = vals.get('titleName')
            list_item['pid'] = vals.get('pid')
            list_item['source'] = 'aiqicha'
            list_item['source_url'] = start_url
            print(list_item)


# start_request()