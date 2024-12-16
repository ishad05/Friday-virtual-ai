import enum
from typing import Annotated
from livekit.agents import llm
import logging
import os
import webbrowser
import psutil
import requests
import shutil
from datetime import datetime, timedelta


logger = logging.getLogger("temperature-control")
logger.setLevel(logging.INFO)


class Zone(enum.Enum):
    ROOM = "room"
    BEDROOM = "bedroom"
    KITCHEN = "kitchen"
    BATHROOM = "bathroom"
    OFFICE = "office"


class AssistantFnc(llm.FunctionContext):
    def __init__(self) -> None:
        super().__init__()

        self._temperature = {
            Zone.ROOM: 22,
            Zone.BEDROOM: 20,
            Zone.KITCHEN: 24,
            Zone.BATHROOM: 23,
            Zone.OFFICE: 21,
        }

    @llm.ai_callable(description="get the temperature in a specific room")
    def get_temperature(
        self, zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")]
    ):
        logger.info("get temp - zone %s", zone)
        temp = self._temperature[Zone(zone)]
        return f"The temperature in the {zone} is {temp}C"

    @llm.ai_callable(description="set the temperature in a specific room")
    def set_temperature(
        self,
        zone: Annotated[Zone, llm.TypeInfo(description="The specific zone")],
        temp: Annotated[int, llm.TypeInfo(description="The temperature to set")],
    ):
        logger.info("set temo - zone %s, temp: %s", zone, temp)
        self._temperature[Zone(zone)] = temp
        return f"The temperature in the {zone} is now {temp}C"

    @llm.ai_callable(description="Open YouTube in the default browser")
    def open_youtube(self):
        logger.info("Opening YouTube")
        webbrowser.open("https://www.youtube.com")
        return "YouTube has been opened in your browser."

    @llm.ai_callable(description="Open Google in the default browser")
    def open_google(self):
        logger.info("Opening Google")
        webbrowser.open("https://www.google.com")
        return "Google has been opened in your browser."

    @llm.ai_callable(description="Open Spotify application")
    def open_spotify(self):
        logger.info("Opening Spotify")
        os.system("spotify")
        return "Spotify has been opened."

    @llm.ai_callable(description="Open Firefox browser")
    def open_firefox(self):
        logger.info("Opening Firefox")
        os.system("firefox")
        return "Firefox has been opened."

    @llm.ai_callable(description="Get system CPU usage")
    def get_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        logger.info("CPU usage: %s%%", cpu_usage)
        return f"Current CPU usage is {cpu_usage}%."

    @llm.ai_callable(description="Get available disk space")
    def get_disk_space(self):
        total, used, free = shutil.disk_usage("/")
        logger.info("Disk space: total=%s, used=%s, free=%s", total, used, free)
        return (
            f"Disk space - Total: {total // (2 ** 30)} GB, "
            f"Used: {used // (2 ** 30)} GB, Free: {free // (2 ** 30)} GB"
        )

    @llm.ai_callable(description="Set a reminder")
    def set_reminder(
            self,
            reminder: Annotated[str, llm.TypeInfo(description="Reminder text")],
            time: Annotated[int, llm.TypeInfo(description="Time in minutes from now")],
    ):
        reminder_time = datetime.now() + timedelta(minutes=time)
        self.reminders.append((reminder, reminder_time))
        logger.info("Reminder set: %s at %s", reminder, reminder_time)
        return f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}."

    @llm.ai_callable(description="Check battery percentage")
    def get_battery_percentage(self):
        battery = psutil.sensors_battery()
        if battery:
            logger.info("Battery percentage: %s%%", battery.percent)
            return f"Battery percentage is {battery.percent}%."
        else:
            return "Battery information is not available."

    @llm.ai_callable(description="Fetch current weather information")
    def get_weather(
            self,
            city: Annotated[str, llm.TypeInfo(description="City name for weather information")],
            api_key: Annotated[str, llm.TypeInfo(description="API key for OpenWeatherMap")],
    ):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            temp = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            logger.info("Weather in %s: %s°C, %s", city, temp, description)
            return f"The current weather in {city} is {temp}°C with {description}."
        else:
            logger.error("Failed to fetch weather for city: %s", city)
            return "Could not fetch weather information. Please check the city name or API key."

    @llm.ai_callable(description="Search Wikipedia for a topic")
    def search_wikipedia(
            self, topic: Annotated[str, llm.TypeInfo(description="Topic to search on Wikipedia")]
    ):
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        logger.info("Searching Wikipedia for topic: %s", topic)
        webbrowser.open(url)
        return f"Searching Wikipedia for {topic}. The page has been opened in your browser."

    @llm.ai_callable(description="Shutdown the system")
    def shutdown_system(self):
        logger.info("Shutting down the system")
        os.system("shutdown /s /t 1")
        return "System is shutting down."

    @llm.ai_callable(description="Restart the system")
    def restart_system(self):
        logger.info("Restarting the system")
        os.system("shutdown /r /t 1")
        return "System is restarting."

