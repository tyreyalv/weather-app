import os
import requests
import logging
import redis

class WeatherMonitor:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        self.latitude = 40.4104770332582
        self.longitude = -105.10477952532925
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK')
        self.temp_threshold_high = float(os.getenv('TEMP_THRESHOLD_HIGH', 80))
        self.temp_threshold_low = float(os.getenv('TEMP_THRESHOLD_LOW', 70))
        self.redis_db = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        self.windows_open_key = 'windows_open'
        self.windows_closed_key = 'windows_closed'

    def get_current_temperature(self):
        weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={self.latitude}&lon={self.longitude}&appid={self.api_key}&units=imperial"
        try:
            response = requests.get(weather_api_endpoint)
            response.raise_for_status()
            data = response.json()
            return data['current']['temp']
        except Exception as e:
            logging.error(f"Failed to get temperature: {e}")
            return None

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
        temp = self.get_current_temperature()
        if temp is None:
            logging.error("Could not retrieve temperature. Exiting script.")
            return None  # Return None if temperature couldn't be fetched

        windows_open = self.redis_db.get(self.windows_open_key)
        windows_open = windows_open.decode() if windows_open else None

        if temp >= self.temp_threshold_high and (windows_open is None or windows_open == 'True'):
            self.send_notification(
                f"Temperature is now over {self.temp_threshold_high} degrees. Current temperature: {temp} degrees. Close the windows.")
            self.update_window_state(False)
        elif temp <= self.temp_threshold_low and (windows_open is None or windows_open == 'False'):
            self.send_notification(
                f"Temperature is now under {self.temp_threshold_low} degrees. Current temperature: {temp} degrees. Open the windows.")
            self.update_window_state(True)

        return temp  # Return the fetched temperature

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