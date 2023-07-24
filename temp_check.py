import requests
import time
import urllib.parse
import os
from dotenv import load_dotenv
import redis

load_dotenv()

OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')  # renamed variable
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)

TEMP_THRESHOLD = 80
CITY_NAME = "Fort Collins"
STATE_CODE = "CO"
COUNTRY_CODE = "US"
STATE_KEY = 'state'
LATITUDE = 40.589820
LONGITUDE = -105.066320

redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


def get_current_temperature():
    weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
    response = requests.get(weather_api_endpoint)
    data = response.json()
    return data['current']['temp']

def send_to_discord(message):  # renamed function
    data = {
        "content": message  # changed key to 'content'
    }
    requests.post(DISCORD_WEBHOOK, json=data)  # changed variable to DISCORD_WEBHOOK

def main():
    temp = get_current_temperature()

    # Read the state from Redis
    state = redis_db.get(STATE_KEY)
    if state is not None:
        state = state.decode()

    if temp > TEMP_THRESHOLD and state != 'above':
        send_to_discord(f"Temperature in Fort Collins, CO is now over {TEMP_THRESHOLD} degrees. Current temperature: {temp} degrees.")  # changed function call
        redis_db.set(STATE_KEY, 'above')
    elif temp <= TEMP_THRESHOLD and state != 'below':
        send_to_discord(f"Temperature in Fort Collins, CO is now back under {TEMP_THRESHOLD} degrees. Current temperature: {temp} degrees.")  # changed function call
        redis_db.set(STATE_KEY, 'below')

if __name__ == "__main__":
    main()
