import logging
from src.config import Config
from src.redis_service import RedisService

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
        elif current_temp <= open_threshold and windows_closed == 'True':
            logging.info("Opening windows...")
            self.redis_service.set(Config.WINDOWS_CLOSED_KEY, False)
            self.redis_service.set(Config.WINDOWS_OPEN_KEY, True)
            message = (
                f"🌡️ **Temperature Alert!**\n\n"
                f"The current temperature is {current_temp}°F, which is below the open threshold of {open_threshold}°F.\n"
                f"🚪 **Action to take:** Open the windows to let in the fresh air.\n"
                f"Enjoy the breeze! 🌬️"
            )
            self.notifier.send_to_discord(message)
            logging.info("Windows opened successfully.")
        else:
            logging.info("No change in window state required.")