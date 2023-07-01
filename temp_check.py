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

TEMP_THRESHOLD = 75
CITY_NAME = "Fort Collins"
STATE_CODE = "CO"
COUNTRY_CODE = "US"
STATE_KEY = 'state'

redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

def get_city_coordinates():
    city_name_encoded = urllib.parse.quote(CITY_NAME)
    geocoding_api_endpoint = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name_encoded},{STATE_CODE},{COUNTRY_CODE}&limit=1&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(geocoding_api_endpoint)
    data = response.json()
    print(f"Response from API: {data}")  
    return data[0]['lat'], data[0]['lon']

def get_current_temperature(lat, lon):
    weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
    response = requests.get(weather_api_endpoint)
    data = response.json()
    return data['current']['temp']

def send_to_discord(message):  # renamed function
    data = {
        "content": message  # changed key to 'content'
    }
    requests.post(DISCORD_WEBHOOK, json=data)  # changed variable to DISCORD_WEBHOOK

def main():
    lat, lon = get_city_coordinates()
    temp = get_current_temperature(lat, lon)

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
