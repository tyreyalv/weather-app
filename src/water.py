from datetime import datetime, timedelta
import logging

class WateringScheduler:
    def __init__(self, redis_service, notifier):
        self.redis_service = redis_service
        self.notifier = notifier

    def log_watering_schedule(self, message):
        timestamp = datetime.now().isoformat()
        self.redis_service.set(f"watering_schedule:{timestamp}", message)
        logging.info(f"Logged watering schedule: {message}")

    def check_watering_time(self):
        logging.info("Checking watering time.")
        weather_data = self.redis_service.get_latest_weather_data()
        if not weather_data:
            logging.error("Could not retrieve weather data from Redis. Exiting check.")
            return
        
        temp = weather_data['current']['temp']
        sunset = weather_data['current']['sunset']
        
        logging.debug(f"Current temperature from weather data: {temp}")
        logging.debug(f"Sunset time from weather data: {sunset}")

        # Convert sunset from Unix timestamp to datetime if it's an integer
        if isinstance(sunset, int):
            sunset_time = datetime.fromtimestamp(sunset)
        else:
            sunset_time = datetime.strptime(sunset, '%Y-%m-%dT%H:%M:%S%z')

        current_time = datetime.now()
        time_until_sunset = sunset_time - current_time
        formatted_sunset_time = sunset_time.strftime('%Y-%m-%d %H:%M:%S')

        logging.debug(f"Current time: {current_time}")
        logging.debug(f"Time until sunset: {time_until_sunset}")
        logging.debug(f"Formatted sunset time: {formatted_sunset_time}")

        if temp <= 80:
            if time_until_sunset >= timedelta(hours=1):
                message = (
                    f"🌞 **Perfect Time to Water Your Lawn!**\n\n"
                    f"The temperature is currently {temp}°F, which is ideal for watering.\n"
                    f"🌅 **Sunset Time:** {formatted_sunset_time}\n"
                    f"⏳ **Time Left:** At least 1 hour of daylight remaining.\n"
                    f"Get your watering done now for the best results! 🌿"
                )
                self.notifier.send_to_discord(message)
                self.log_watering_schedule(message)
                logging.info("Sent notification and logged schedule for ideal watering time.")
            elif time_until_sunset >= timedelta(hours=3):
                message = (
                    f"🌞 **Good Time to Water Your Lawn!**\n\n"
                    f"The temperature is currently {temp}°F, which is suitable for watering.\n"
                    f"🌅 **Sunset Time:** {formatted_sunset_time}\n"
                    f"⏳ **Time Left:** Up to 3 hours of daylight remaining.\n"
                    f"Plan your watering within this window for optimal results! 🌿"
                )
                self.notifier.send_to_discord(message)
                self.log_watering_schedule(message)
                logging.info("Sent notification and logged schedule for 3-hour watering window.")
        elif time_until_sunset >= timedelta(hours=1):
            message = (
                f"🌞 **Time to Water Your Lawn!**\n\n"
                f"🌅 **Sunset Time:** {formatted_sunset_time}\n"
                f"⏳ **Time Left:** At least 1 hour of daylight remaining.\n"
                f"Make sure to water your lawn before the sun sets! 🌿"
            )
            self.notifier.send_to_discord(message)
            self.log_watering_schedule(message)
            logging.info("Sent notification and logged schedule for 1-hour watering window.")
        else:
            logging.info("No suitable watering time found.")