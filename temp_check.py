import os
import logging
import redis
import requests

# Constants
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
LATITUDE = os.getenv('LATITUDE', '40.410160')
LONGITUDE = os.getenv('LONGITUDE', '-105.104730')
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
TEMP_THRESHOLD_HIGH = float(os.getenv('TEMP_THRESHOLD_HIGH', 75))
TEMP_THRESHOLD_LOW = float(os.getenv('TEMP_THRESHOLD_LOW', 74.5))
STATE_KEY_HIGH = os.getenv('STATE_KEY_HIGH', 'state_high')
STATE_KEY_LOW = os.getenv('STATE_KEY_LOW', 'state_low')

logging.basicConfig(level=logging.INFO)

# Redis DB setup
redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

def get_current_temperature():
    try:
        weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
        response = requests.get(weather_api_endpoint)
        response.raise_for_status()
        data = response.json()
        temp = data['current']['temp']
        weather = data['current']['weather'][0]['description']
        logging.info(f"Current temperature: {temp} degrees. Weather: {weather}.")
        return temp
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

def check_temperature(temp, threshold, state_key, state, message):
    if temp > threshold and state != 'above':
        logging.info(message)
        send_to_discord(message)
        redis_db.set(state_key, 'above')
    elif temp <= threshold and state != 'below':
        redis_db.set(state_key, 'below')

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

    check_temperature(temp, TEMP_THRESHOLD_HIGH, STATE_KEY_HIGH, state_high, 
                      f"Temperature is now over {TEMP_THRESHOLD_HIGH} degrees. Current temperature: {temp} degrees.")
    check_temperature(temp, TEMP_THRESHOLD_LOW, STATE_KEY_LOW, state_low, 
                      f"Temperature is now below {TEMP_THRESHOLD_LOW} degrees. Current temperature: {temp} degrees.")

if __name__ == "__main__":
    main()