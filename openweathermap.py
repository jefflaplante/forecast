import os
import requests
import logging

from weatherprovider import WeatherProvider

class OpenWeatherMap(WeatherProvider):
    def __init__(self):
        self.api_key = os.environ["OPEN_WEATHER_MAP_API_KEY"]
        self.zip_code = os.environ["WEATHER_ZIP_CODE"]

        self.endpoint = "http://api.openweathermap.org/data/2.5/"

    def _get(self):
        params = (
            ('zip', f'{self.zip_code},us'),
            ('appid', self.api_key),
            ('units', 'imperial'),
        )
        response = requests.get(f'{self.endpoint}weather', params = params)
        return response.json()

    # Get the current weather conditions at given zip code
    def get_weather(self):
        d = self._get()
        w = {}
        w['temp'] = d['main']['temp']
        w['pressure'] = d['main']['pressure']
        w['pressure_unit'] = 'rel. in.'
        w['humidity'] = d['main']['humidity']

        if 'rain' in d:
            w['rain_accum'] = d['rain']['1h']

        w['wind'] = {
            'speed': d['wind']['speed'], 
            'degree': d['wind']['deg'], 
            'direction': self.cardinal_direction(d['wind']['deg'])
            }

        w['description'] = d['weather'][0]['description']
        w['category'] = d['weather'][0]['main']

        return w
    
    # Get the 5 day forecast from openweathermap.org
    def get_forecast(self, days):
        cnt = days * 8 # API returns 8 data points for each day (3 hour intervals)
        params = (
            ('zip', f'{self.zip_code},us'),
            ('appid', self.api_key),
            ('cnt', cnt),
            ('units', 'imperial'),
        )
        response = requests.get(f'{self.endpoint}forecast', params = params)
        return response.json()
