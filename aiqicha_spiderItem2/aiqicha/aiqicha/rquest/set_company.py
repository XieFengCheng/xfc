import redis
import sys
sys.path.append('/aiqicha_spiderItem2/')
from aiqicha.aiqicha.settings import bixiao_business


POOL = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=2)
REDIS_CLI = redis.Redis(connection_pool=POOL)

company_url = 'https://aiqicha.baidu.com/s/l?q={keys}&t=&s=10&o=0&f=%7B%7D'

def read_base():
    company_list = bixiao_business.find({})
    for keyword in company_list:
        url = company_url.format(keys=keyword.get('company_name'))
        set_keys(url)

def set_keys(name):
    vals = REDIS_CLI.lpush('SupplySpiders:start_urls', name)
    return vals

def get_keys():
    name = REDIS_CLI.rpop('SupplySpiders:start_urls')
    return name



if __name__ == '__main__':
    read_base()
