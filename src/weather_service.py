import logging
import requests
from datetime import datetime
import redis

LATITUDE = 40.41018434579078
LONGITUDE = -105.10478681459281

class WeatherService:
    def __init__(self, api_key, redis_service):
        self.api_key = api_key
        self.redis_service = redis_service

    def get_current_weather(self):
        logging.info("Getting current weather data...")
        try:
            weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={self.api_key}&units=imperial"
            logging.info(f"Sending request to {weather_api_endpoint}")
            response = requests.get(weather_api_endpoint)
            response.raise_for_status()
            data = response.json()
            temp = data['current']['temp']
            weather = data['current']['weather'][0]['description']
            sunset = data['current']['sunset']
            daily_high = data['daily'][0]['temp']['max']
            logging.info(f"Current temperature: {temp} degrees. Weather: {weather}. Sunset: {sunset}. Daily high: {daily_high} degrees.")

            aqi_api_endpoint = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={LATITUDE}&lon={LONGITUDE}&appid={self.api_key}"
            logging.info(f"Sending request to {aqi_api_endpoint}")
            aqi_response = requests.get(aqi_api_endpoint)
            aqi_response.raise_for_status()
            aqi_data = aqi_response.json()
            aqi = aqi_data['list'][0]['main']['aqi']
            logging.info(f"Current AQI: {aqi}")
            
            # Save data to Redis
            timestamp = datetime.now().isoformat()
            weather_info = {
                'temp': temp,
                'weather': weather,
                'sunset': sunset,
                'daily_high': daily_high,
                'aqi': aqi
            }
            logging.info(f"Saving weather data to Redis with key weather:{timestamp}")
            self.redis_service.set(f"weather:{timestamp}", weather_info)
            
            return temp, sunset, daily_high
        except Exception as e:
            logging.error(f"Failed to get weather data: {e}")
            return None, None, None