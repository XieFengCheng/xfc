# -*- coding: utf-8 -*-
from db.client_db import proxy_ip, login_ip
import requests


dialer_url = 'http://'
def dialer_ip():
    get_proxy = requests.get(dialer_url, timeout=5)
    if get_proxy.status_code == 200:
        result = login_ip.lrem('login_ip', 1, 0)
        if result:
            proxy_ip.lrem('proxy_pool', 1, 0)
        return result
    else:
        dialer_ip()


if __name__ == '__main__':
    dialer_ip()
