import os
import requests
import logging
import redis

# Constants
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
LATITUDE = 40.410160
LONGITUDE = -105.104730
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK')
TEMP_THRESHOLD_HIGH = float(os.getenv('TEMP_THRESHOLD_HIGH', 80))
TEMP_THRESHOLD_LOW = float(os.getenv('TEMP_THRESHOLD_LOW', 79.5))
WINDOWS_OPEN_KEY = 'windows_open'
WINDOWS_CLOSED_KEY = 'windows_closed'

# Redis DB setup
redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

logging.basicConfig(level=logging.INFO)

def get_current_temperature():
    logging.info("Getting current temperature...")
    try:
        weather_api_endpoint = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
        logging.info(f"Sending request to {weather_api_endpoint}")
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
    logging.info("Sending message to Discord...")
    try:
        response = requests.post(DISCORD_WEBHOOK, json={"content": message})
        response.raise_for_status()
        logging.info("Message sent to Discord successfully.")
    except Exception as e:
        logging.error(f"Failed to send message to Discord: {e}")

def check_temperature():
    try:
        temp = get_current_temperature()
        if temp is None:
            logging.error("Failed to get current temperature.")
            return
    except Exception as e:
        logging.error(f"An error occurred while getting the current temperature: {e}")
        return

    logging.info(f"Current temperature: {temp} degrees.")

    try:
        windows_open = redis_db.get(WINDOWS_OPEN_KEY)
        if windows_open is not None:
            windows_open = windows_open.decode()

        windows_closed = redis_db.get(WINDOWS_CLOSED_KEY)
        if windows_closed is not None:
            windows_closed = windows_closed.decode()
    except Exception as e:
        logging.error(f"An error occurred while getting window states from Redis DB: {e}")
        return

    logging.info(f"Current states from Redis DB: Windows open state: {windows_open}, Windows closed state: {windows_closed}")

    try:
        if temp > TEMP_THRESHOLD_HIGH and (windows_open is None or windows_open == 'True'):
            message = f"Temperature is now over {TEMP_THRESHOLD_HIGH} degrees. Current temperature: {temp} degrees. Close the windows."
            logging.info(message)
            send_to_discord(message)
            redis_db.set(WINDOWS_OPEN_KEY, 'False')
            redis_db.set(WINDOWS_CLOSED_KEY, 'True')
        elif temp < TEMP_THRESHOLD_LOW and (windows_closed is None or windows_closed == 'True'):
            message = f"Temperature is now under {TEMP_THRESHOLD_LOW} degrees. Current temperature: {temp} degrees. Open the windows."
            logging.info(message)
            send_to_discord(message)
            redis_db.set(WINDOWS_OPEN_KEY, 'True')
            redis_db.set(WINDOWS_CLOSED_KEY, 'False')
    except Exception as e:
        logging.error(f"An error occurred while checking temperature and updating Redis DB: {e}")


def main():
    logging.info("Script started.")
    
    temp = get_current_temperature()

    if temp is None:
        logging.error("Could not retrieve temperature. Exiting script.")
        return

    logging.info(f"Current temperature: {temp} degrees.")

    windows_open = redis_db.get(WINDOWS_OPEN_KEY)
    if windows_open is not None:
        windows_open = windows_open.decode()

    windows_closed = redis_db.get(WINDOWS_CLOSED_KEY)
    if windows_closed is not None:
        windows_closed = windows_closed.decode()

    logging.info(f"Current states from Redis DB: Windows open state: {windows_open}, Windows closed state: {windows_closed}")

    if temp > TEMP_THRESHOLD_HIGH and (windows_open is None or windows_open == 'True'):
        message = f"Temperature is now over {TEMP_THRESHOLD_HIGH} degrees. Current temperature: {temp} degrees. Close the windows."
        logging.info(message)
        send_to_discord(message)
        redis_db.set(WINDOWS_OPEN_KEY, 'False')
        redis_db.set(WINDOWS_CLOSED_KEY, 'True')
    elif temp < TEMP_THRESHOLD_LOW and (windows_closed is None or windows_closed == 'True'):
        message = f"Temperature is now under {TEMP_THRESHOLD_LOW} degrees. Current temperature: {temp} degrees. Open the windows."
        logging.info(message)
        send_to_discord(message)
        redis_db.set(WINDOWS_OPEN_KEY, 'True')
        redis_db.set(WINDOWS_CLOSED_KEY, 'False')

if __name__ == "__main__":
    main()