import logging
import requests
from datetime import datetime

LATITUDE = 40.41018434579078
LONGITUDE = -105.10478681459281

class WeatherService:
    def __init__(self, api_key):
        self.api_key = api_key

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
            logging.info(f"Current temperature: {temp} degrees. Weather: {weather}. Sunset: {sunset}.")
            return temp, sunset
        except Exception as e:
            logging.error(f"Failed to get weather data: {e}")
            return None, None