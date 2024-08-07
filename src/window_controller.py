import logging
from src.config import Config
from src.redis_service import RedisService
from datetime import datetime, timedelta


class WindowController:
    def __init__(self, redis_service, notifier):
        self.redis_service = redis_service
        self.notifier = notifier

    def check_and_update_window_state(self, current_temp, close_threshold, open_threshold):
        logging.info("Checking window state...")
        windows_open = self.redis_service.get(Config.WINDOWS_OPEN_KEY)
        windows_closed = self.redis_service.get(Config.WINDOWS_CLOSED_KEY)

        logging.debug(f"Current temperature: {current_temp}")
        logging.debug(f"Close threshold: {close_threshold}, Open threshold: {open_threshold}")
        logging.debug(f"Windows open state from Redis: {windows_open}")
        logging.debug(f"Windows closed state from Redis: {windows_closed}")

        if current_temp >= close_threshold and windows_open == 'True':
            logging.info("Closing windows...")
            self.redis_service.set(Config.WINDOWS_CLOSED_KEY, True)
            self.redis_service.set(Config.WINDOWS_OPEN_KEY, False)
            message = (
                f"🌡️ **Temperature Alert!**\n\n"
                f"The current temperature is {current_temp}°F, which is above the close threshold of {close_threshold}°F.\n"
                f"🚪 **Action to take:** Close the window to keep the indoor environment cool and comfortable.\n"
                f"Stay cool! 😎"
            )
            self.notifier.send_to_discord(message)
            logging.info("Windows closed successfully.")
        elif current_temp <= open_threshold - Config.HYSTERESIS and windows_closed == 'True':
            logging.info("Opening windows...")
            self.redis_service.set(Config.WINDOWS_CLOSED_KEY, False)
            self.redis_service.set(Config.WINDOWS_OPEN_KEY, True)
            message = (
                f"🌡️ **Temperature Alert!**\n\n"
                f"The current temperature is {current_temp}°F, which is below the open threshold of {open_threshold - Config.HYSTERESIS}°F.\n"
                f"🚪 **Action to take:** Open the windows to let in the fresh air.\n"
                f"Enjoy the breeze! 🌬️"
            )
            self.notifier.send_to_discord(message)
            logging.info("Windows opened successfully.")
        else:
            logging.info("No change in window state required.")

    
    def check_aqi_and_notify(self):
        logging.info("Checking AQI...")
        weather_info = self.redis_service.get_latest_weather_data()
        if weather_info:
            aqi = weather_info.get('aqi', None)
            if aqi is not None:
                logging.debug(f"Current AQI: {aqi}")
                if aqi >= 3:
                    # Check the last notification time
                    last_notification_time_str = self.redis_service.get('last_aqi_notification_time')
                    if last_notification_time_str:
                        last_notification_time = datetime.fromisoformat(last_notification_time_str)
                    else:
                        last_notification_time = None

                    current_time = datetime.now()
                    notification_interval = timedelta(hours=1)  # Set the interval to 1 hour

                    if not last_notification_time or (current_time - last_notification_time) > notification_interval:
                        message = (
                            f"🌫️ **Air Quality Alert!**\n\n"
                            f"The current Air Quality Index (AQI) is {aqi}, which scaled is above the safe threshold of 80 or higher.\n"
                            f"🚪 **Action to take:** Keep windows closed to avoid poor air quality indoors.\n"
                            f"Stay safe! 😷"
                        )
                        self.notifier.send_to_discord(message)
                        logging.info("AQI alert sent successfully.")
                        
                        # Update the last notification time
                        self.redis_service.set('last_aqi_notification_time', current_time.isoformat())
                    else:
                        logging.info("AQI alert not sent to avoid spamming.")
                else:
                    logging.info("AQI is within safe limits.")
            else:
                logging.warning("AQI data not available.")
        else:
            logging.warning("Weather data not available.")