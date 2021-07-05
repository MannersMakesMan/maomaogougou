import redis
from basic_configuration.settings import REDIS_CONF

# redis连接池
redis_pool = redis.ConnectionPool(**REDIS_CONF)
