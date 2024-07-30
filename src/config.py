import os
import logging

class Config:
    logging.basicConfig(level=logging.INFO)

    ENV = os.getenv('ENV', 'production')
    logging.info(f"Environment: {ENV}")

    # Redis configuration for production
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    # OpenWeatherMap API Key
    OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

    # Discord Webhook URL
    DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')

    # Temperature thresholds
    TEMP_THRESHOLD_CLOSE = float(os.getenv('TEMP_THRESHOLD_CLOSE', 79))
    TEMP_THRESHOLD_OPEN = float(os.getenv('TEMP_THRESHOLD_OPEN', 78))

    # Redis keys for window states
    WINDOWS_OPEN_KEY = 'windows_open'
    WINDOWS_CLOSED_KEY = 'windows_closed'

    logging.info(f"Redis Host: {REDIS_HOST}")
    logging.info(f"OpenWeatherMap API Key: {OPENWEATHERMAP_API_KEY}")