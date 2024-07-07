import redis

class RedisService:
    def __init__(self, host, port, password):
        self.client = redis.Redis(host=host, port=port, password=password)

    def get(self, key):
        value = self.client.get(key)
        return value.decode() if value else None

    def set(self, key, value):
        self.client.set(key, value)