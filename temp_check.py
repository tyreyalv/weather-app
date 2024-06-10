import requests
import os
import logging
from dotenv import load_dotenv
import redis

load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OPENWEATHERMAP_API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')
DISCORD_WEBHOOK = os.environ.get('DISCORD_WEBHOOK')
REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

TEMP_THRESHOLD_HIGH = 70
TEMP_THRESHOLD_LOW = 75

STATE_KEY_HIGH = 'state_high'
STATE_KEY_LOW = 'state_low'
LATITUDE = 40.410160
LONGITUDE = -105.104730

redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

def get_current_temperature():
    try:
        weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
        response = requests.get(weather_api_endpoint)
        response.raise_for_status()
        data = response.json()
        return data['current']['temp']
    except Exception as e:
        logging.error(f"Failed to get temperature: {e}")
        return None

def send_to_discord(message):  
    try:
        data = {
            "content": message  
        }
        response = requests.post(DISCORD_WEBHOOK, json=data)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to send Discord notification: {e}")

def main():
    logging.info("Script started.")
    
    temp = get_current_temperature()

    if temp is None:
        logging.error("Could not retrieve temperature. Exiting script.")
        return

    logging.info(f"Current temperature: {temp} degrees.")


    state_high = redis_db.get(STATE_KEY_HIGH)
    if state_high is not None:
        state_high = state_high.decode()

    state_low = redis_db.get(STATE_KEY_LOW)
    if state_low is not None:
        state_low = state_low.decode()

    logging.info(f"Current states from Redis DB: High threshold state: {state_high}, Low threshold state: {state_low}")

    if temp > TEMP_THRESHOLD_HIGH and state_high != 'above':
        logging.info(f"Temperature is now over {TEMP_THRESHOLD_HIGH} degrees.")
        send_to_discord(f"Temperature in Loveland, CO is now over {TEMP_THRESHOLD_HIGH} degrees. Current temperature: {temp} degrees.")
        redis_db.set(STATE_KEY_HIGH, 'above')
    elif temp <= TEMP_THRESHOLD_HIGH and state_high != 'below':
        redis_db.set(STATE_KEY_HIGH, 'below')

    if temp > TEMP_THRESHOLD_LOW and state_low != 'above':
        redis_db.set(STATE_KEY_LOW, 'above')
    elif temp <= TEMP_THRESHOLD_LOW and state_low != 'below':
        logging.info(f"Temperature is now back under {TEMP_THRESHOLD_LOW} degrees.")
        send_to_discord(f"Temperature in Loveland, CO is now back under {TEMP_THRESHOLD_LOW} degrees. Current temperature: {temp} degrees.")
        redis_db.set(STATE_KEY_LOW, 'below')

    logging.info("Script finished successfully.")

if __name__ == "__main__":
    main()
