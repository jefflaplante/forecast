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
        w['zip_code'] = self.zip_code
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

        # Unique keys to Open Weather Map
        w['description'] = d['weather'][0]['description']
        w['category'] = d['weather'][0]['main']
        w['city'] = d['name']
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

    def sample_data_weather(self):
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
                'sunset': 1612401070
                },
            'timezone': -28800,
            'id': 0,
            'name': 'Arlington',
            'cod': 200
        }
        return w

    def sample_data_forecast(self):
        w = {   
            'city': {
                'coord': {'lat': 48.1829, 'lon': -122.1121},
                'country': 'US',
                'id': 0,
                'name': 'Arlington',
                'population': 0,
                'sunrise': 1612366406,
                'sunset': 1612401070,
                'timezone': -28800
            },
            'cnt': 8,
            'cod': '200',
            'list': [{   
                    'clouds': {'all': 1},
                    'dt': 1612386000,
                    'dt_txt': '2021-02-03 21:00:00',
                    'main': {   
                        'feels_like': 39.34,
                        'grnd_level': 1010,
                        'humidity': 70,
                        'pressure': 1021,
                        'sea_level': 1021,
                        'temp': 44.02,
                        'temp_kf': -0.23,
                        'temp_max': 44.44,
                        'temp_min': 44.02
                    },
                    'pop': 0,
                    'sys': {'pod': 'd'},
                    'visibility': 10000,
                    'weather': [{   
                        'description': 'clear sky',
                        'icon': '01d',
                        'id': 800,
                        'main': 'Clear'
                    }],
                    'wind': {'deg': 275, 'speed': 2.75}
                }],
            'message': 0
        }
        return w