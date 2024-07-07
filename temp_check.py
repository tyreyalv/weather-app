import os
import requests
import logging
import redis
import time
import json

class WeatherMonitor:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.latitude = 40.4104770332582
        self.longitude = -105.10477952532925
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        self.temp_threshold_high = float(os.getenv('TEMP_THRESHOLD_HIGH', 79))
        self.temp_threshold_low = float(os.getenv('TEMP_THRESHOLD_LOW', 78))
        self.redis_db = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        self.windows_open_key = 'windows_open'
        self.windows_closed_key = 'windows_closed'

    def fetch_weather_data(self):
        # Check if weather data exists in Redis and is still valid
        cached_weather_data = self.redis_db.get('weather_data')
        if cached_weather_data:
            self.weather_data = json.loads(cached_weather_data.decode('utf-8'))
            return

        weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}&units=imperial"
        try:
            response = requests.get(weather_api_endpoint)
            response.raise_for_status()
            self.weather_data = response.json()
            # Store the weather data in Redis with a TTL of 1800 seconds (30 minutes)
            self.redis_db.set('weather_data', json.dumps(self.weather_data), ex=1800)
        except Exception as e:
            logging.error(f"Failed to fetch weather data: {e}")
            self.weather_data = None

    def send_notification(self, message):
        try:
            data = {"content": message}
            response = requests.post(self.discord_webhook, json=data)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to send Discord notification: {e}")

    def update_window_state(self, open_state):
        self.redis_db.set(self.windows_open_key, 'True' if open_state else 'False')
        self.redis_db.set(self.windows_closed_key, 'False' if open_state else 'True')

    def check_temperature_and_notify(self):
        self.fetch_weather_data()  # Ensure weather data is fetched and stored
        if self.weather_data is None:
            logging.error("Could not retrieve weather data. Exiting script.")
            return None

        temp = self.weather_data['current']['temp']
        windows_open = self.redis_db.get(self.windows_open_key)
        windows_open = windows_open.decode() if windows_open else None

        if temp >= self.temp_threshold_high and (windows_open is None or windows_open == 'True'):
            self.send_notification(
                f"Temperature is now over {self.temp_threshold_high} degrees. Current temperature: {temp} degrees. Close the windows.")
            self.update_window_state(False)
        elif temp <= self.temp_threshold_low and (windows_open is None or windows_open == 'False'):
            self.send_notification(
                f"Temperature is now under {self.temp_threshold_low} degrees. Current temperature: {temp} degrees. Open the windows.")
            self.update_window_state(True)  # Return the fetched temperature

    def check_watering_conditions(self):
        if self.weather_data is None:
            logging.error("Weather data not available.")
            return

        current_temp = self.weather_data['current']['temp']
        sunset_time = self.weather_data['current']['sunset']
        current_time = time.time()
        time_until_sunset = sunset_time - current_time

        if abs(current_temp - 75) <= 5 and time_until_sunset >= 5400:  # 5400 seconds = 90 minutes
            self.send_notification(
                "It's a good time to water the grass. Temperature is close to 75 degrees with sufficient sunshine left.")
def main():
    logging.basicConfig(level=logging.INFO)
    weather_monitor = WeatherMonitor()
    temp = weather_monitor.check_temperature_and_notify()
    if temp is not None:
        print(f"Script ran successfully. Current temperature: {temp} degrees.")
    else:
        print("Script did not run successfully due to an error fetching the temperature.")

if __name__ == "__main__":
    main()