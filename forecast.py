#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
import time
import traceback
import logging
import pprint
import argparse

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

def parse_log_level():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", 
        "--log", 
        default="info",
        help=(
            "Provide logging level. "
            "Example --log debug', default='info'")
    )

    options = parser.parse_args()

    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    level = levels.get(options.log.lower())
    if level is None:
        raise ValueError(
            f"log level given: {options.log}"
            f" -- must be one of: {' | '.join(levels.keys())}")
    
    return level

def main():
    try:
        level = parse_log_level()
        logging.basicConfig(level=level)

        logging.info("Refreshing forecast")

        # get forecast data from APIs
        openWeather = OpenWeatherMap()
        w = openWeather.get_weather()
        f = openWeather.get_forecast(5)

        logging.debug(pprint.pprint(w))
        logging.debug(pprint.pprint(f))

        # merge data from ambient provider if environment variables are setup to use it
        if 'AMBIENT_DEVICE_MAC' in os.environ:
            amb = Ambient()
            wa = amb.get_weather()
            w.update(wa) # Ambient data will overlay Open Weather Maps data if it exists.

        # Initialize the display driver
        epd = epd7in5_V2.EPD()
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
