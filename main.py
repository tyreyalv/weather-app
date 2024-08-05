import os
import logging
from dotenv import load_dotenv
from src.config import Config
from src.redis_service import RedisService
from src.weather_service import WeatherService
from src.notifier import Notifier
from src.window_controller import WindowController
from src.water import WateringScheduler

load_dotenv()

class TemperatureMonitor:
    def __init__(self, weather_service, window_controller):
        self.weather_service = weather_service
        self.window_controller = window_controller

    def run(self):
        logging.info("Script started.")
        temp, sunset, daily_high = self.weather_service.get_current_weather()
        if temp is None:
            logging.error("Could not retrieve temperature. Exiting script.")
            return

        logging.info(f"Current temperature: {temp} degrees. Daily high: {daily_high} degrees.")
        
        # Adjust thresholds based on daily high temperature
        if daily_high >= 90:
            open_threshold = 85
            close_threshold = 85
            logging.info(f"Daily high is {daily_high} degrees. Adjusting thresholds to {open_threshold} degrees.")
        else:
            open_threshold = Config.TEMP_THRESHOLD_OPEN
            close_threshold = Config.TEMP_THRESHOLD_CLOSE

        self.window_controller.check_and_update_window_state(temp, close_threshold, open_threshold)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        redis_service = RedisService(Config.REDIS_HOST, Config.REDIS_PORT, Config.REDIS_PASSWORD)
    except ConnectionError as e:
        logging.error(f"Could not connect to Redis. Exiting script. Error: {e}")
        exit(1)

    weather_service = WeatherService(Config.OPENWEATHERMAP_API_KEY, redis_service)
    notifier = Notifier(Config.DISCORD_WEBHOOK)
    window_controller = WindowController(redis_service, notifier)
    
    temperature_monitor = TemperatureMonitor(weather_service, window_controller)
    watering_scheduler = WateringScheduler(redis_service, notifier)

    temperature_monitor.run()
    #watering_scheduler.check_watering_time()