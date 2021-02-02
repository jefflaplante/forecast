#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import requests
import time
import traceback
import logging
from datetime import datetime

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from PIL import Image,ImageDraw,ImageFont
from netifaces import AF_INET
import netifaces as ni
from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.INFO)

my_ip = ni.ifaddresses('wlan0')[AF_INET][0]['addr']

# API Keys and zip code to drive forecast data
api_key = os.environ["OPEN_WEATHER_MAP_API_KEY"]
zip_code = os.environ["WEATHER_ZIP_CODE"]

days = 5 # Days to gather for forecast

font_file = os.path.join(picdir, 'Font.ttc')
font96 = ImageFont.truetype(font_file, 96)
font80 = ImageFont.truetype(font_file, 80)
font54 = ImageFont.truetype(font_file, 54)
font48 = ImageFont.truetype(font_file, 48)
font24 = ImageFont.truetype(font_file, 24)
font22 = ImageFont.truetype(font_file, 22)
font18 = ImageFont.truetype(font_file, 18)
font16 = ImageFont.truetype(font_file, 16)
font10 = ImageFont.truetype(font_file, 10)

pad = 10 # Element padding

# Return icon imabe based on forecast category
def get_icon(forecast):
    if forecast['category'] == 'Rain':
        pouring = Image.open(os.path.join(picdir, 'weather-pouring.jpg'))
        return pouring
    elif forecast['category'] == "Clouds":
        cloudy = Image.open(os.path.join(picdir, 'weather-cloudy.jpg'))
        return cloudy
    elif forecast['category'] == "Snow":
        snow = Image.open(os.path.join(picdir, 'weather-snowy.jpg'))
        return snow
    else:
        sunny= Image.open(os.path.join(picdir, 'weather-sunny.jpg'))
        return sunny

# Return the cardinal direction based on the wind direction degree
def cardinal_direction(degree):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(degree / (360. / len(dirs)))
    return dirs[ix % len(dirs)]

# Return a datetime object by parsing date string from forecast data
def get_datetime(date_str):
    datetime_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return datetime_object

# Return the string name of the week from the passed in date
def get_day_name(date):
     return date.strftime("%A")

# Get the 5 day forecast from openweathermap.org
def get_forecast(zip_code, days):
    cnt = days * 8
    params = (
        ('zip', f'{zip_code},us'),
        ('appid', api_key),
        ('cnt', cnt),
        ('units', 'imperial'),
    )
    response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=params)
    return response.json()

# Get the current weather conditions at given zip code
def get_weather(zip_code):
    params = (
        ('zip', f'{zip_code},us'),
        ('appid', api_key),
        ('units', 'imperial'),
    )
    response = requests.get('http://api.openweathermap.org/data/2.5/weather', params=params)
    return response.json()

# Draw a forecast day block from the x,y top left corner position for the block
def draw_day(image, forecast, x, y):
    wind = Image.open(os.path.join(picdir, 'wind.jpg'))

    # container size
    width = 156
    height = 250
    pad = 10

    y_offset = 0

    # drawing utility
    d = ImageDraw.Draw(image)

    # Container bounds
    d.rectangle((x, y, (x + width), (y + height)), outline = 255)

    # Day of week
    x_offset = x + pad
    y_offset = y + pad
    
    day_date = get_datetime(forecast['date_str'])
    day_str = f"{day_date.strftime('%a')} "
    date_str = f"{day_date.strftime('%m/%d')} "

    d.text(((x_offset + 10), y_offset), day_str, font = font22, fill = 0)
    d.text(((x_offset + 85), (y_offset + 6)), date_str, font = font16, fill = 0)

    y_offset += 35

    # Icon
    icon = get_icon(forecast)
    image.paste(icon, ((x + 55), y_offset))

    # Description
    x_offset += 15
    y_offset += 55
    d.text((x_offset, y_offset), f"{forecast['description']} ", font = font16, fill = 0)
 
    # Divider Line
    x_offset -= 10
    y_offset += 25
    d.line((x_offset, y_offset, (x_offset + width - pad - pad - pad), y_offset), fill = 0, width = 3)

    # Temp
    x_offset += 20
    y_offset += 15
    d.text((x_offset, y_offset), f"{forecast['temp']:3.0f}°", font = font54, fill = 0)

    # Wind Speed
    x_offset -= 15
    y_offset += 80
    d.text((x_offset, y_offset), f"{forecast['wind_speed']:2.1f} mph", font = font16, fill = 0)
    image.paste(wind, ((x_offset + 80), (y_offset - 5)))

    return image

# Update e-paper display
def update_display(image, epd):
    logging.info("Updating e-paper display")
    epd.display(epd.getbuffer(image))
    epd.sleep()
    epd.Dev_exit()

def main():
    try:
        logging.info("Refreshing forecast")

        # Date and time
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")
        current_date_str = now.strftime("%b %d")

        logging.info(f"Current date: {now}")

        # get forecast data from API
        forecast = get_forecast(zip_code, days)
        weather = get_weather(zip_code)

        title = f"{forecast['city']['name']}, {zip_code} "

        # Current Weather Conditions from API response
        w = {'temp': weather['main']['temp']}
        w['description'] = weather['weather'][0]['description']
        w['category'] = weather['weather'][0]['main']
        w['wind'] = {'speed': weather['wind']['speed'], 'degree': weather['wind']['deg'], 'direction': cardinal_direction(weather['wind']['deg'])}
        w['pressure'] = weather['main']['pressure']
        w['humidity'] = weather['main']['humidity']

        if 'rain' in weather:
            w['rain_accum'] = weather['rain']['1h']

        # Initialize the display driver
        epd = epd7in5_V2.EPD()  # E-Paper display driver object
        epd.init()

        # Create a new image to draw our display on
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: white

        # Drawing utility
        draw = ImageDraw.Draw(Himage)

        # IP
        draw.text((710, pad), my_ip, font = font10, fill = 0)

        # Title
        draw.text((pad, pad), title, font = font24, fill = 0)

        # Date
        draw.text((40, 50), f"{current_day} ", font = font80, fill = 0)
        draw.text((342, 105), f"{current_date_str} ", font = font22, fill = 0)

        # Icon
        icon = get_icon(w)
        Himage.paste(icon, (540, 40))

        # Current Temp.    
        draw.text((600, 30), f"{w['temp']:3.0f}° ", font = font96, fill = 0)

        # Description
        draw.text((480, 105), f"{w['description']} ", font = font18, fill = 0)
        
        # Wind
        y_offset = 170
        x_offset = pad + 30
        draw.text((x_offset, y_offset), f"{w['wind']['speed']:2.1f} mph {w['wind']['direction']}", font = font18, fill = 0)
        wind = Image.open(os.path.join(picdir, 'wind.jpg'))
        Himage.paste(wind, ((x_offset + 110), (y_offset - 3)))

        # Humidity
        x_offset += 150
        draw.text((x_offset, y_offset), f"{w['humidity']:3.0f} % Humidity ", font = font18, fill = 0)
        
        # Pressure
        x_offset += 150
        draw.text((x_offset, y_offset), f"{w['pressure']:4.0f} mb ", font = font18, fill = 0)

        # Rain
        x_offset += 95
        if 'rain_accum' in w:
            draw.text((x_offset, y_offset), f"{w['rain_accum']:2.2f} in/hr of rain ", font = font18, fill = 0)

        # Update time
        x_offset += 200
        draw.text((x_offset, y_offset), f"updated: {current_time}", font = font18, fill = 0)
        
        # Divider Line
        draw.line(((pad + 20) , 215, (epd.width - pad - 20), 215), fill = 0, width = 3)

        # Iterate over forecast days in 'list' and draw widgets for each
        offset = pad
        day_vert = 225
        day_width = 156

        day_register = 'day'
        time_counter = 0

        for x in forecast['list']:
            temp = x['main']['temp']
            category = x['weather'][0]['main']
            description = x['weather'][0]['description']
            wind_speed = x['wind']['speed']
            date_str = x['dt_txt']
            day = get_day_name(get_datetime(date_str))

            f = {'date_str': date_str, 'temp': temp, 'category': category, 'description': description, 'wind_speed': wind_speed}

            # forecast data returns a dict for every 3 hours. We only want daily so find unique days and get third reporting for noon for that day.
            if day_register == day:
                if time_counter == 3:
                    Himage = draw_day(Himage, f, offset, day_vert) # Draw the day widget
                    offset += day_width
                time_counter += 1
            else:
                day_register = day
                time_counter = 0

        # Update e-paper display
        update_display(Himage, epd)

        # Write out image to disk as a jpeg
        Himage.save('display.jpg', "JPEG")

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
