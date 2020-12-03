from proxypool.storages.redis import RedisClient

def clien():
    client = RedisClient()
    return client.random()


func = clien()
print(func)