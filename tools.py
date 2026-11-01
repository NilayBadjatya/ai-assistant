import requests
import os
import smtplib
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.text import MIMEText

def get_current_time(country: str) -> str:
    """Returns the current time for a given time zone."""
    current_time = datetime.now(ZoneInfo(country))
    return current_time.strftime("%Y-%m-%d %H:%M:%S")

def get_user_city() -> str:
    return "Indore"

def get_weather(city: str) -> str:
    """Fetch current weather for a city."""

    # Step A: Convert city name into latitude and longitude
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    geo_response = requests.get(
        geo_url,
        params={"name": city, "count": 1},
        timeout=10
    )
    geo_response.raise_for_status()

    locations = geo_response.json().get("results", [])

    if not locations:
        return f"Could not find the city: {city}"

    location = locations[0]
    latitude = location["latitude"]
    longitude = location["longitude"]
    city_name = location["name"]
    country = location.get("country", "")

    # Step B: Fetch current weather
    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_response = requests.get(
        weather_url,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "apparent_temperature,"
                "is_day,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "timezone": "auto"
        },
        timeout=10
    )
    weather_response.raise_for_status()

    current = weather_response.json()["current"]

    return (
        f"Weather in {city_name}, {country}:\n"
        f"Temperature: {current['temperature_2m']}°C\n"
        f"Feels like: {current['apparent_temperature']}°C\n"
        f"Humidity: {current['relative_humidity_2m']}%\n"
        f"Wind speed: {current['wind_speed_10m']} km/h\n"
        f"Precipitation: {current['precipitation']} mm\n"
        f"Weather code: {current['weather_code']}"
    )

def send_email(to: str, subject: str, body: str):
    """Sends a mail to the given recipent"""
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [to], msg.as_string())

    return f"Email sent to {to}"


tools = [
    {
        "type" : "function",
        "function" : {
            "name" : "get_current_time",
            "description" : "Returns the current time as a string in the format 'YYYY-MM-DD HH:MM:SS'.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "country" : {
                        "type" : "string",
                        "description" : (
                            "IANA timezone name for the location, such as "
                            "Asia/Kolkata or America/New_York."
                        )
                    }
                },
                "required" : ["country"],
                "additionalProperties" : False,
            }
        }
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_weather",
            "description" : "Fetches the current weather for a given city. Use when user asks for weather       related information.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "city" : {
                        "type" : "string",
                        "description" : "Name of the city to fetch weather for."
                    }
                },
                "required" : ["city"]
            }
        }
    },
    {
        "type" : "function",
        "function" : {
            "name" : "get_user_city",
            "description" : "Returns the user's city. Use when user asks for their city.",
            "parameters" : {
                "type" : "object",
                "properties" : {}
            }
        }
    },
    {
        "type" : "function",
        "function" : {
            "name" : "send_email",
            "description" : "Sends an email to the given recipient.",
            "parameters" : {
                "type" : "object",
                "properties" : {
                    "to" : {
                        "type" : "string",
                        "description" : "Email address of the recipient."
                    },
                    "subject" : {
                        "type" : "string",
                        "description" : "Subject of the email."
                    },
                    "body" : {
                        "type" : "string",
                        "description" : "Body of the email."
                    }
                },
                "required" : ["to", "subject", "body"],
                "additionalProperties" : False
            }
        }
    }
]


function_map = {
    "get_weather" : get_weather,
    "get_current_time" : get_current_time,
    "get_user_city" : get_user_city,
    "send_email" : send_email
}  