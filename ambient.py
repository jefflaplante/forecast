import os
import requests
import logging

from weatherprovider import WeatherProvider

class Ambient(WeatherProvider):
    def __init__(self):
        self.api_key = os.environ["AMBIENT_API_KEY"]
        self.app_key = os.environ["AMBIENT_APP_KEY"]
        self.device_mac = os.environ["AMBIENT_DEVICE_MAC"]

        self.endpoint = "https://api.ambientweather.net/v1/devices/"

    def _get(self):
        params = (
            ('applicationKey', self.app_key),
            ('apiKey', self.api_key),
        )
        response = requests.get(f'{self.endpoint}{self.device_mac}', params = params)
        return response.json()

    def get_weather(self):
        d = self._get()
        w = {}
        w['temp'] = d['tempf']
        w['pressure'] = d['baromrelin']
        w['pressure_unit'] = 'mb'
        w['humidity'] = d['humidity']
        
        return w

    def sample_weather(self):
        w = [
            {
                "dateutc": 1612332600000,
                "tempinf": 69.4,
                "battin": 1,
                "humidityin": 46,
                "baromrelin": 29.33,
                "baromabsin": 29.33,
                "tempf": 37.6,
                "humidity": 99,
                "winddir": 110,
                "winddir_avg10m": 156,
                "windspeedmph": 9.6,
                "windspdmph_avg10m": 5.1,
                "windgustmph": 16.1,
                "maxdailygust": 21.5,
                "hourlyrainin": 0.024,
                "eventrainin": 2.831,
                "dailyrainin": 0.52,
                "weeklyrainin": 2.453,
                "monthlyrainin": 1.209,
                "yearlyrainin": 7.559,
                "solarradiation": 0,
                "uv": 0,
                "temp1f": 68.9,
                "humidity1": 45,
                "batt1": 1,
                "pm25_in": 3,
                "pm25_in_24h": 3.6,
                "batt_25in": 1,
                "feelsLike": 30.85,
                "dewPoint": 37.34,
                "feelsLike1": 67.6,
                "dewPoint1": 46.7,
                "feelsLikein": 68.2,
                "dewPointin": 47.7,
                "lastRain": "2021-02-03T06:10:00.000Z",
                "loc": "ambient-prod-5",
                "date": "2021-02-03T06:10:00.000Z"
            }
        ]
        return w
