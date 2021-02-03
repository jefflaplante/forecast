import os
import requests
import logging

from weatherprovider import WeatherProvider

class OpenWeatherMap(WeatherProvider):
    def __init__(self):
        logging.info("Loading OpenWeatherMap provider")
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
        w['city'] = d['sys']['name']
        w['zip_code'] = self.zip_code
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

        print(response.json())
        
        return response.json()

    def sample_data(self):
        w = {
        'coord': {
            'lon': -122.1121,
            'lat': 48.1829
            },
        'weather': [{
            'id': 800,
            'main': 'Clear',
            'description': 'clear sky',
            'icon': '01d'
            }], 
        'base': 'stations',
        'main': {
            'temp': 40.68,
            'feels_like': 35.33,
            'temp_min': 39,
            'temp_max': 42.01,
            'pressure': 1021,
            'humidity': 87
            }, 
        'visibility': 10000,
        'wind': {
            'speed': 4.61,
            'deg': 80}, 
            'clouds': {
                'all': 1
            },
        'dt': 1612379637, 
        'sys': {
            'type': 1,
            'id': 3363,
            'country': 'US',
            'sunrise': 1612366406,
            'sunset': 1612401070},
            'timezone': -28800,
            'id': 0,
            'name': 'Arlington',
            'cod': 200
        }
        return w