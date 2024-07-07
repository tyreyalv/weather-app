import logging
import requests

class Notifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_to_discord(self, message):
        logging.info("Sending message to Discord...")
        try:
            response = requests.post(self.webhook_url, json={"content": message})
            response.raise_for_status()
            logging.info("Message sent to Discord successfully.")
        except Exception as e:
            logging.error(f"Failed to send message to Discord: {e}")