"""
 Data persistence
"""
import redis
from staticconf import schema
import urlparse

from rssdigest import config

class RedisConfig(schema.Schema):
    namespace = config.app_namespace
    config_path = ''

    url = schema.string(config_key='REDISCLOUD_URL')

    def get_parsed_url(self):
        return urlparse.urlparse(self.url)


class RedisConnection(object):

    config = RedisConfig()

    def __init__(self):
        self.inst = None

    def connect(self):
        url = self.config.get_parsed_url()
        self.inst = redis.StrictRedis(
            host=url.hostname,
            port=url.port,
            password=url.password)

    def get(self):
        if not self.inst:
            self.connect()
        return self.inst
        

single_conn = RedisConnection()

def get_conn():
    return single_conn.get()
