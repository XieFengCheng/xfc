
import redis
from deploy.config import REDIS_HOST, REDIS_PORT, REDIS_PD

def create_redis_conn(db_num):
    """
    创建 redis 数据库连接

    :param db_num: 数据库编号
    :return: 返回公众号 redis 处理的对象
    """
    try:
        pool_ = redis.ConnectionPool(host=REDIS_HOST,
                                     port=REDIS_PORT,
                                     password=REDIS_PD,
                                     db=db_num,
                                     retry_on_timeout=True,)
        redis_client = redis.Redis(connection_pool=pool_)
        return redis_client
    except:
        return dict()


proxy_ip = create_redis_conn(12)  #代理池
admin_heap = create_redis_conn(13)  #账号池
tyc_cookies = create_redis_conn(10)    #天眼查cooikes
login_ip = create_redis_conn(11)    #登录使用代理
