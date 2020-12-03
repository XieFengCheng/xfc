import redis
import random

pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=10)
conn = redis.Redis(connection_pool=pool)

def cookies_get():
    # cookey = conn.lpop('tyc_cookies')
    cookey = conn.lrange('tyc_cookies', 0, -1)
    # cookey = conn.lindex('tyc_cookies', 0)
    if cookey:
        # new_cookies = cookey.decode()
        # return new_cookies
        new_cookies = cookey
        get_cookies = random.choice(new_cookies)
        return get_cookies.decode()


fun = cookies_get()
print(fun)