import requests
from datetime import datetime, timedelta
from django.conf import settings

API_KEY = settings.OPENWEATHER_API_KEY


class CityNotFoundError(ValueError):
    pass


def get_current_weather(city):
    url = "https://api.openweathermap.org/data/2.5/weather"
    resp = requests.get(url, params={"q": city, "appid": API_KEY, "units": "metric"})
    if resp.status_code != 200:
        raise ValueError("City not found")
    data = resp.json()

    timezone_seconds = data["timezone"]
    utc_now = datetime.utcnow()
    local_time = (utc_now + timedelta(seconds=timezone_seconds)).strftime("%H:%M")

    return {
        "temperature": data["main"]["temp"],
        "local_time": local_time
    }


def get_forecast_for_date(city, target_date):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    resp = requests.get(url, params={"q": city, "appid": API_KEY, "units": "metric"})
    if resp.status_code != 200:
        raise CityNotFoundError("City not found")
    data = resp.json()

    temps = []
    for item in data["list"]:
        dt = datetime.fromtimestamp(item["dt"])
        if dt.date() == target_date:
            temps.append(item["main"]["temp"])

    if not temps:
        raise ValueError("No forecast data for this date")

    return {
        "min_temperature": min(temps),
        "max_temperature": max(temps)
    }
