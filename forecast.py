#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import time
import traceback
import logging

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from PIL import Image,ImageDraw,ImageFont
from waveshare_epd import epd7in5_V2

from ambient import Ambient
from openweathermap import OpenWeatherMap 
import display

logging.basicConfig(level=logging.INFO)

# Update e-paper display
def update_display(image, epd):
    logging.info("Updating e-paper display")
    epd.display(epd.getbuffer(image))
    epd.sleep()
    epd.Dev_exit()

def main():
    try:
        logging.info("Refreshing forecast")

        # get forecast data from API
        openWeather = OpenWeatherMap()
        w = openWeather.get_weather()
        forecast = openWeather.get_forecast(5)

        # Initialize the display driver
        epd = epd7in5_V2.EPD()  # E-Paper display driver object
        epd.init()

        # Create a new image to draw our display on
        display_image = Image.new('1', (epd.width, epd.height), 255)  # 255: white

        # Draw current conditions to the display image
        display_image = display.draw_current_weather(display_image, w)

        # Draw the forecast to the display image
        display_image = display.draw_forecast(display_image, forecast)

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
