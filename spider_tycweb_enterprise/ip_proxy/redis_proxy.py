# -*- coding: utf-8 -*-
from db.client_db import proxy_ip, admin_heap

class SetProxyAdmin:
    def __init__(self):
        self.proxy_pool = proxy_ip.lrange('proxy_pool', 0, -1)
        self.admin_pool = admin_heap.lrange('admin_heap', 0, -1)

    def set_proxy(self):
        for proxy_str in self.proxy_pool:
            proxy = str(proxy_str).split('-')[0]
            proxy_url = str(proxy_str).split('-')[1]
            print(proxy, proxy_url)



    def set_admin(self):
        for heap_user in self.admin_pool:

            return heap_user



admins_heap = admin_heap.lindex('admin_heap', 0).decode()
print(admins_heap)


