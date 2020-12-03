import requests

import redis

pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=12)
conn = redis.Redis(connection_pool=pool)


def get_proxy():
    ip_use = conn.rpop('proxy_pool')
    if ip_use:
        use_ips = str(ip_use.decode()).split('-')[0]
        proxies = {'https': 'https://{}'.format(use_ips)}
        header_form = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko'
                          ') Chrome/83.0.4103.97 Safari/537.36'}
        try:
            res_html = requests.get(
                'https://www.tianyancha.com', headers=header_form, proxies=proxies, verify=False)
        except:
            res_html = requests.get(
                'https://www.tianyancha.com', headers=header_form, verify=False)

        if res_html.status_code == 200:
            return proxies



func = get_proxy()
print(func, '#'*80)