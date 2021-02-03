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

import qrcode
from PIL import Image,ImageDraw,ImageFont
from netifaces import AF_INET
import netifaces as ni
from waveshare_epd import epd7in5_V2

from ambient import Ambient
from openweathermap import OpenWeatherMap 

logging.basicConfig(level=logging.INFO)

# Generate QR Code
def generate_qr_code(input_data):
    qr = qrcode.QRCode(
        version=1,
        box_size=1,
        border=0)
    qr.add_data(input_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    return img

# Get a display font to write with
def get_font(size):
    font_file = os.path.join(picdir, 'Font.ttc')
    f = ImageFont.truetype(font_file, size)
    return f

# Return icon image based on forecast category
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

# # Return the cardinal direction based on the wind direction degree
# def cardinal_direction(degree):
#     dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
#     ix = round(degree / (360. / len(dirs)))
#     return dirs[ix % len(dirs)]

# Return a datetime object by parsing date string from forecast data
def get_datetime(date_str):
    datetime_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return datetime_object

# Return the string name of the week from the passed in date
def get_day_name(date):
     return date.strftime("%A")

# Get the 5 day forecast from openweathermap.org
def get_forecast(api_key, zip_code, days):
    cnt = days * 8
    params = (
        ('zip', f'{zip_code},us'),
        ('appid', api_key),
        ('cnt', cnt),
        ('units', 'imperial'),
    )
    response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params = params)
    return response.json()

# # Get the current weather conditions at given zip code
# def get_weather(api_key, zip_code):
#     params = (
#         ('zip', f'{zip_code},us'),
#         ('appid', api_key),
#         ('units', 'imperial'),
#     )
#     response = requests.get('http://api.openweathermap.org/data/2.5/weather', params = params)
#     return response.json()

# Draw current weather information to the display image
def draw_current_weather(image, w):
        # Date and time
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")
        current_date_str = now.strftime("%b %d")

        logging.info(f"Current date: {now}")

        my_ip = ni.ifaddresses('wlan0')[AF_INET][0]['addr']

        title = f"{w['city']}, {w['zip_code']} "

        # Drawing utility
        draw = ImageDraw.Draw(image)

        # Element padding
        pad = 10

        # IP
        draw.text((670, pad), my_ip, font = get_font(10), fill = 0)
        qr = generate_qr_code(f'http://{my_ip}')
        image.paste(qr, (745, pad))

        # Title
        draw.text((pad, pad), title, font = get_font(24), fill = 0)

        # Date
        draw.text((40, 50), f"{current_day} ", font = get_font(80), fill = 0)
        draw.text((342, 105), f"{current_date_str} ", font = get_font(22), fill = 0)

        # Icon
        icon = get_icon(w)
        image.paste(icon, (540, 40))

        # Current Temp.    
        draw.text((600, 30), f"{w['temp']:3.0f}° ", font = get_font(96), fill = 0)

        # Description
        draw.text((480, 105), f"{w['description']} ", font = get_font(18), fill = 0)
        
        # Wind
        y_offset = 170
        x_offset = pad + 30
        draw.text((x_offset, y_offset), f"{w['wind']['speed']:2.1f} mph {w['wind']['direction']}", font = get_font(18), fill = 0)
        wind = Image.open(os.path.join(picdir, 'wind.jpg'))
        image.paste(wind, ((x_offset + 120), (y_offset - 3)))

        # Humidity
        x_offset += 160
        draw.text((x_offset, y_offset), f"{w['humidity']:3.0f} % Humidity ", font = get_font(18), fill = 0)
        
        # Pressure
        x_offset += 150
        draw.text((x_offset, y_offset), f"{w['pressure']:4.0f} mb ", font = get_font(18), fill = 0)

        # Rain
        x_offset += 95
        if 'rain_accum' in w:
            draw.text((x_offset, y_offset), f"{w['rain_accum']:2.2f} in/hr of rain ", font = get_font(18), fill = 0)

        # Update time
        x_offset += 200
        draw.text((x_offset, y_offset), f"updated: {current_time}", font = get_font(18), fill = 0)
        
        # Divider Line
        draw.line(((pad + 20) , 215, (image.width - pad - 20), 215), fill = 0, width = 3)

        return image

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

    d.text(((x_offset + 10), y_offset), day_str, font = get_font(22), fill = 0)
    d.text(((x_offset + 85), (y_offset + 6)), date_str, font = get_font(16), fill = 0)

    y_offset += 35

    # Icon
    icon = get_icon(forecast)
    image.paste(icon, ((x + 55), y_offset))

    # Description
    x_offset += 15
    y_offset += 55
    d.text((x_offset, y_offset), f"{forecast['description']} ", font = get_font(16), fill = 0)
 
    # Divider Line
    x_offset -= 10
    y_offset += 25
    d.line((x_offset, y_offset, (x_offset + width - pad - pad - pad), y_offset), fill = 0, width = 3)

    # Temp
    x_offset += 20
    y_offset += 15
    d.text((x_offset, y_offset), f"{forecast['temp']:3.0f}°", font = get_font(54), fill = 0)

    # Wind Speed
    x_offset -= 15
    y_offset += 80
    d.text((x_offset, y_offset), f"{forecast['wind_speed']:2.1f} mph", font = get_font(16), fill = 0)
    image.paste(wind, ((x_offset + 80), (y_offset - 5)))

    return image

# Draw the forecast to the display image
def draw_forecast(image, forecast):
    # Iterate over forecast days in 'list' and draw widgets for each
    offset = 10
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
                image = draw_day(image, f, offset, day_vert) # Draw the day widget
                offset += day_width
            time_counter += 1
        else:
            day_register = day
            time_counter = 0

    return image

# # Gather elements we want from larger dict
# def gather_weather_data(weather):
#     w = {'temp': weather['main']['temp']}
#     w['description'] = weather['weather'][0]['description']
#     w['category'] = weather['weather'][0]['main']
#     w['wind'] = {'speed': weather['wind']['speed'], 'degree': weather['wind']['deg'], 'direction': cardinal_direction(weather['wind']['deg'])}
#     w['pressure'] = weather['main']['pressure']
#     w['humidity'] = weather['main']['humidity']

#     if 'rain' in weather:
#         w['rain_accum'] = weather['rain']['1h']

#     return w

# Update e-paper display
def update_display(image, epd):
    logging.info("Updating e-paper display")
    epd.display(epd.getbuffer(image))
    epd.sleep()
    epd.Dev_exit()

def main():
    try:
        logging.info("Refreshing forecast")

        # API Keys and zip code to drive forecast data
        api_key = os.environ["OPEN_WEATHER_MAP_API_KEY"]
        zip_code = os.environ["WEATHER_ZIP_CODE"]

        # get forecast data from API
        days = 5 # Days to gather for forecast
        forecast = OpenWeatherMap().get_forecast(days)
        # forecast = get_forecast(api_key, zip_code, days)

        w = OpenWeatherMap().get_weather()
        # weather = get_weather(api_key, zip_code)
        # # Current Weather Conditions from API response
        # w = gather_weather_data(weather)

        w['zip_code'] = zip_code
        w['city'] = forecast['city']['name']

        # Initialize the display driver
        epd = epd7in5_V2.EPD()  # E-Paper display driver object
        epd.init()

        # Create a new image to draw our display on
        display_image = Image.new('1', (epd.width, epd.height), 255)  # 255: white

        # Draw current conditions to the display image
        display_image = draw_current_weather(display_image, w)

        # Draw the forecast to the display image
        display_image = draw_forecast(display_image, forecast)

        # Update e-paper display
        update_display(display_image, epd)

        # Write out image to disk as a jpeg
        display_image.save('display.jpg', "JPEG")

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
