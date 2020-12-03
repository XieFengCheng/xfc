
import redis
import random


def client(db_name):
    pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=db_name)
    conn = redis.Redis(connection_pool=pool)
    return conn
#
#
# def eval_cks(get_cookie):
#     int_cookies = str(eval(get_cookie)).replace(': ', '=').replace("'", '').replace('{', '').\
#         replace('}', '').replace(',', ';')
#     return int_cookies
#
#
# def main():
#     get_cookie = client(10).lrange('cookies', 0, -1)
#     return eval_cks(random.choice(get_cookie))
#
#
# if __name__ == '__main__':
#
#     func = main()
#     print(func)


def get_cookies():
    cookies_list = client(9).lrange('tyc_cookies', 0, -1)
    return (random.choice(cookies_list)).decode()


cuin = get_cookies()
print(cuin)
