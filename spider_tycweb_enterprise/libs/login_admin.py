# -*- coding: utf-8 -*-
from db.client_db import login_ip, admin_heap
import requests
# from ip_proxy.save_proxy import main
# from db.save_proxy import main


def login_proxy():
    ip_proxy = login_ip.rpop('login_ip')
    # if not ip_proxy:
    #     main()
    proxy_ = {'https': 'https://%s' % ip_proxy.decode()}
    if proxy_:
        return ip_proxy.decode()


def login_user():
    user_pd = admin_heap.rpop('admin_heap')
    if user_pd:
        print(user_pd)
        user_login = str(user_pd.decode()).split('-')
        user_num = user_login[0]
        password = user_login[1]
        return [user_num, password]
    # else:
    #     main()





if __name__ == '__main__':

    func = login_proxy()
    # func = login_user()
    print(func)
