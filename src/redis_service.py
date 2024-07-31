import redis
import json

class RedisService:
    def __init__(self, host, port, password):
        try:
            self.client = redis.Redis(host=host, port=port, password=password, socket_connect_timeout=5)
            self.client.ping()  # Attempt to connect and ping Redis
        except (redis.ConnectionError, redis.TimeoutError) as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}") from e

    def get(self, key):
        try:
            value = self.client.get(key)
            if value:
                value = value.decode()
                try:
                    return json.loads(value)  # Attempt to deserialize JSON
                except json.JSONDecodeError:
                    return value  # Return as string if not JSON
            return None
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None

    def set(self, key, value):
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)  # Serialize to JSON
            elif isinstance(value, bool):
                value = str(value)  # Convert boolean to string
            self.client.set(key, value)
        except redis.RedisError as e:
            print(f"Redis error: {e}")

    def get_latest_weather_data(self):
        try:
            keys = self.client.keys("weather:*")
            if not keys:
                return None
            latest_key = max(keys)
            value = self.client.get(latest_key)
            if value:
                return json.loads(value.decode())  # Deserialize JSON
            return None
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None