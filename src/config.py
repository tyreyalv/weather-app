import os


class Config:
    ENV = os.getenv('ENV', 'production')

    # Redis configuration for production
    REDIS_HOST = os.getenv('PROD_REDIS_HOST')
    REDIS_PORT = int(os.getenv('PROD_REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('PROD_REDIS_PASSWORD', None)

    # OpenWeatherMap API Key
    OPENWEATHERMAP_API_KEY = os.getenv('PROD_OPENWEATHERMAP_API_KEY')

    # Discord Webhook URL
    DISCORD_WEBHOOK = os.getenv('PROD_DISCORD_WEBHOOK')

    # Temperature thresholds
    TEMP_THRESHOLD_CLOSE = float(os.getenv('TEMP_THRESHOLD_CLOSE', 75))
    TEMP_THRESHOLD_OPEN = float(os.getenv('TEMP_THRESHOLD_OPEN', 80))

    # Redis keys for window states
    WINDOWS_OPEN_KEY = 'windows_open'
    WINDOWS_CLOSED_KEY = 'windows_closed'