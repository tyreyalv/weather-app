import requests
import time
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
GOOGLE_CHAT_WEBHOOK = os.environ.get('GOOGLE_CHAT_WEBHOOK')

TEMP_THRESHOLD = 75
CITY_NAME = "Fort Collins"
STATE_CODE = "CO"
COUNTRY_CODE = "US"

def get_city_coordinates():
    city_name_encoded = urllib.parse.quote(CITY_NAME)
    geocoding_api_endpoint = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name_encoded},{STATE_CODE},{COUNTRY_CODE}&limit=1&appid={OPENWEATHERMAP_API_KEY}"
    response = requests.get(geocoding_api_endpoint)
    data = response.json()
    print(f"Response from API: {data}")  
    return data[0]['lat'], data[0]['lon']

def get_current_temperature(lat, lon):
    weather_api_endpoint = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
    response = requests.get(weather_api_endpoint)
    data = response.json()
    return data['main']['temp']

def send_to_google_chat(message):
    data = {
        "text": message
    }
    requests.post(GOOGLE_CHAT_WEBHOOK, json=data)

def main():
    lat, lon = get_city_coordinates()
    temp = get_current_temperature(lat, lon)

    if temp > TEMP_THRESHOLD:
        send_to_google_chat(f"Temperature in Fort Collins, CO is now over {TEMP_THRESHOLD} degrees. Current temperature: {temp} degrees.")
    elif temp <= TEMP_THRESHOLD:
        send_to_google_chat(f"Temperature in Fort Collins, CO is now back under {TEMP_THRESHOLD} degrees. Current temperature: {temp} degrees.")

if __name__ == "__main__":
    main()