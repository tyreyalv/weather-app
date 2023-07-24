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

TEMP_THRESHOLD_HIGH = 80
TEMP_THRESHOLD_LOW = 78
STATE_KEY_HIGH = 'state_high'
STATE_KEY_LOW = 'state_low'
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
    state_high = redis_db.get(STATE_KEY_HIGH)
    if state_high is not None:
        state_high = state_high.decode()

    state_low = redis_db.get(STATE_KEY_LOW)
    if state_low is not None:
        state_low = state_low.decode()

    if temp > TEMP_THRESHOLD_HIGH and state_high != 'above':
        send_to_discord(f"Temperature in Fort Collins, CO is now over {TEMP_THRESHOLD_HIGH} degrees. Current temperature: {temp} degrees.")
        redis_db.set(STATE_KEY_HIGH, 'above')
    elif temp <= TEMP_THRESHOLD_HIGH and state_high != 'below':
        redis_db.set(STATE_KEY_HIGH, 'below')

    if temp > TEMP_THRESHOLD_LOW and state_low != 'above':
        redis_db.set(STATE_KEY_LOW, 'above')
    elif temp <= TEMP_THRESHOLD_LOW and state_low != 'below':
        send_to_discord(f"Temperature in Fort Collins, CO is now back under {TEMP_THRESHOLD_LOW} degrees. Current temperature: {temp} degrees.")
        redis_db.set(STATE_KEY_LOW, 'below')

if __name__ == "__main__":
    main()
