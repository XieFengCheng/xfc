import redis


pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=14, decode_responses=True)
conn = redis.Redis(connection_pool=pool)


ck_pool = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=6, decode_responses=True)
ck_cli = redis.Redis(connection_pool=ck_pool)


account_number = redis.ConnectionPool(host='120.78.131.53', port=6379, password='tuoluo123123', db=5, decode_responses=True)
account_cli = redis.Redis(connection_pool=account_number)

