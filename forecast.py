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

        # get forecast data from APIs
        openWeather = OpenWeatherMap()
        w = openWeather.get_weather()
        f = openWeather.get_forecast(5)

        # merge data from ambient provider if environment variables are setup to use it
        if 'AMBIENT_DEVICE_MAC' in os.environ:
            amb = Ambient()
            wa = amb.get_weather()
            w.update(wa)

        # Initialize the display driver
        epd = epd7in5_V2.EPD()  # E-Paper display driver object
        epd.init()

        # Generate a new weather display image
        img = display.draw((epd.width, epd.height), w, f)

        # Write out image to disk as a jpeg
        img.save('display.jpg', "JPEG")

        # Update e-paper display
        update_display(img, epd)

    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    main()
