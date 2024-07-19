import redis

class RedisService:
    def __init__(self, host, port, password):
        try:
            self.client = redis.Redis(host=host, port=port, password=password, socket_connect_timeout=5)
            self.client.ping()  # Attempt to connect and ping Redis
        except (redis.ConnectionError, redis.TimeoutError) as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")

    def get(self, key):
        try:
            value = self.client.get(key)
            return value.decode() if value else None
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None

    def set(self, key, value):
        try:
            self.client.set(key, value)
        except redis.RedisError as e:
            print(f"Redis error: {e}")