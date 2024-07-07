import logging
from .config import Config

class WindowController:
    def __init__(self, redis_service, notifier):
        self.redis_service = redis_service
        self.notifier = notifier

    def check_and_update_window_state(self, temperature, close_threshold, open_threshold):
        windows_open = self.redis_service.get(Config.WINDOWS_OPEN_KEY)
        windows_closed = self.redis_service.get(Config.WINDOWS_CLOSED_KEY)

        logging.info(
            f"Current states from Redis DB: Windows open state: {windows_open}, Windows closed state: {windows_closed}")

        try:
            if temperature >= close_threshold and (windows_open is None or windows_open == 'True'):
                message = f"Temperature is now {temperature} degrees or higher. Close the windows."
                logging.info(message)
                self.notifier.send_to_discord(message)
                self.redis_service.set(Config.WINDOWS_OPEN_KEY, 'False')
                self.redis_service.set(Config.WINDOWS_CLOSED_KEY, 'True')
            elif temperature < open_threshold and (windows_closed is None or windows_closed == 'True'):
                message = f"Temperature is now below {open_threshold} degrees. Open the windows."
                logging.info(message)
                self.notifier.send_to_discord(message)
                self.redis_service.set(Config.WINDOWS_OPEN_KEY, 'True')
                self.redis_service.set(Config.WINDOWS_CLOSED_KEY, 'False')
        except Exception as e:
            logging.error(f"An error occurred while checking temperature and updating Redis DB: {e}")