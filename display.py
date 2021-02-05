import os
import logging
from datetime import datetime

import qrcode
from PIL import Image,ImageDraw,ImageFont
from netifaces import AF_INET
import netifaces as ni

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')

# Return a datetime object by parsing date string from forecast data
def get_datetime(date_str):
    datetime_object = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return datetime_object

# Return the string name of the week from the passed in date
def get_day_name(date):
     return date.strftime("%A")

# Generate QR Code
def generate_qr_code(input_data):
    logging.info("Generating QR code")

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

# text description for AQI index
def get_AQI_desc(i):    
    # Good: 0.0 – 12.0 (µg/m3
    # Moderate: 12.1 – 35.4 (µg/m3)
    # Unhealthy for Sensitive Groups: 35.5 – 55.4 (µg/m3)
    # Unhealthy: 55.5 – 150.4 (µg/m3)
    # Very Unhealthy: 150.5 – 250.4 (µg/m3)
    # Hazardous: 250.5 – 350.4 (µg/m3)
    # Extremely Hazardous: 350.5 – 500 (µg/m3)

    if i < 12.1:
        return 'good'
    elif i > 12.0 and i < 35.5:
        return 'moderate'
    elif i > 35.4 and i < 55.5:
        return 'unhealthy for sensitive groups'
    elif i > 55.4 and i < 150.5:
        return 'unhealthy'
    elif i > 150.4 and i < 250.5:
        return 'very unhealthy'
    elif i > 250.4 and i < 350.5:
        return 'hazardous'
    else:
        return 'very hazardous'

# text description for UVI index
def get_UVI_desc(i):
    # 0-2 low
    # 3-5 moderate
    # 6-7 high
    # 8-10 very high
    # 11+ extreme

    if i < 2:
        return 'low'
    elif i > 3 and i < 6:
        return 'moderate'
    elif i > 5 and i < 8:
        return 'high'
    elif i > 7 and i < 11:
        return 'very high'
    else:
        return 'extreme'

# Draw current weather information to the display image
def _draw_current_weather(image, w):
    logging.info("Drawing current weather widgets")

    # Date and time
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_day = now.strftime("%a")
    current_date_str = now.strftime("%b %d")

    logging.info(f"Current date: {now}")

    my_ip = ni.ifaddresses('wlan0')[AF_INET][0]['addr']
    qr = generate_qr_code(f'http://{my_ip}')
    title = f"{w['city']}, {w['zip_code']} "

    # Drawing utility
    draw = ImageDraw.Draw(image)

    # Element padding
    pad = 10

    # Title
    draw.text((pad, pad), title, font = get_font(24), fill = 0)

    # IP & QR Code for IP
    draw.text((685, pad), my_ip, font = get_font(10), fill = 0)
    image.paste(qr, (760, pad))

    # ---

    # Today's Date
    draw.text((30, 50), f"{current_day} ", font = get_font(80), fill = 0)
    draw.text((190, 105), f"{current_date_str} ", font = get_font(22), fill = 0)

    # Weather Icon
    if 'category' in w:
        icon = get_icon(w)
        image.paste(icon, (540, 40))

    # Temp.    
    draw.text((600, 60), f"{w['temp']:3.0f}° ", font = get_font(96), fill = 0)

    # Weather Description
    if 'description' in w:
        draw.text((480, 135), f"{w['description']} ", font = get_font(18), fill = 0)

    # AQI Warning
    if 'pm25_indoor' in w:
        aqi = get_AQI_desc(w['pm25_indoor'])
        if aqi != 'good':
            draw.text((50, 140), f"AQI is {aqi}! ", font = get_font(22), fill = 0)
    
    # ---

    item_width = 115
    icon_width = 25 
    y_offset = 180

    # UV Index
    x_offset = pad + 20
    if 'uv' in w:
        uv = Image.open(os.path.join(picdir, 'uv.jpg'))
        image.paste(uv, (x_offset , y_offset))
    x_offset += icon_width
    if 'uv' in w:
        draw.text((x_offset, y_offset), f"{w['uv']:2.0f} {get_UVI_desc(w['uv'])} ", font = get_font(18), fill = 0)
  
    # Dew Point
    x_offset += item_width
    if 'dew_point' in w:
        dew = Image.open(os.path.join(picdir, 'star.jpg'))
        image.paste(dew, (x_offset , y_offset))
    x_offset += icon_width
    if 'dew_point' in w:
        draw.text((x_offset, y_offset), f"{w['dew_point']:3.0f}° ", font = get_font(18), fill = 0)

    # pm25 Indoor
    x_offset += item_width
    if 'pm25_indoor' in w:
        air = Image.open(os.path.join(picdir, 'air-filter.jpg'))
        image.paste(air, (x_offset , y_offset))
    x_offset += icon_width
    if 'pm25_indoor' in w:
        draw.text((x_offset, y_offset), f"{w['pm25_indoor']:3.0f} µg/m³ I", font = get_font(18), fill = 0)

    # pm25 Outdoor
    x_offset += item_width
    if 'aqi' in w:
        air = Image.open(os.path.join(picdir, 'air-filter.jpg'))
        image.paste(air, (x_offset , y_offset))
    x_offset += icon_width
    if 'aqi' in w:
        draw.text((x_offset, y_offset), f"{w['aqi']['pm2_5']:3.0f} µg/m³ O", font = get_font(18), fill = 0)

    # Temp Indoor
    x_offset += item_width
    if 'temp_indoor' in w:
        home = Image.open(os.path.join(picdir, 'home.jpg'))
        image.paste(home, (x_offset , y_offset))
    x_offset += icon_width
    if 'temp_indoor' in w:
        draw.text((x_offset, y_offset), f"{w['temp_indoor']:3.0f}° ", font = get_font(18), fill = 0)

    # ---
     
    # Update time
    x_offset += 65
    y_offset += 4
    draw.text((x_offset, y_offset), f"updated: {current_time} ", font = get_font(14), fill = 0)

    # ---

    y_offset = 210

    # Wind
    x_offset = pad + 20
    wind = Image.open(os.path.join(picdir, 'wind.jpg'))
    image.paste(wind, (x_offset , y_offset))
    x_offset += icon_width
    draw.text((x_offset, y_offset), f"{w['wind']['speed']:3.1f} mph {w['wind']['direction']} ", font = get_font(18), fill = 0)
    
    # Humidity
    x_offset += item_width
    humidity = Image.open(os.path.join(picdir, 'humidity.jpg'))
    image.paste(humidity, (x_offset , y_offset))
    x_offset += icon_width
    draw.text((x_offset, y_offset), f"{w['humidity']:3.0f}% ", font = get_font(18), fill = 0)
    
    # Pressure
    x_offset += item_width
    pressure = Image.open(os.path.join(picdir, 'thermometer.jpg'))
    image.paste(pressure, (x_offset , y_offset))
    x_offset += icon_width
    if w['pressure_unit'] == 'mb':
        draw.text((x_offset, y_offset), f"{w['pressure']:4.0f} {w['pressure_unit']} ", font = get_font(18), fill = 0)
    else:
        draw.text((x_offset, y_offset), f"{w['pressure']:2.2f} {w['pressure_unit']} ", font = get_font(18), fill = 0)

    # Rain
    x_offset += item_width
    drop = Image.open(os.path.join(picdir, 'drop.jpg'))
    image.paste(drop, (x_offset , y_offset))
    x_offset += icon_width

    rain = {}
    if 'rain' in w:
        rain = w['rain']

    if 'rate' in rain:
        draw.text((x_offset, y_offset), f"{rain['rate']:2.2f} in/hr ", font = get_font(18), fill = 0)
    else:
        draw.text((x_offset, y_offset), "0.0 in/hr ", font = get_font(18), fill = 0)
    
    x_offset = 90
    if 'daily' in rain:
        draw.text((x_offset, y_offset), f"{rain['daily']:2.2f}\" today ", font = get_font(18), fill = 0)
    else:
        draw.text((x_offset, y_offset), "0.0 in today ", font = get_font(18), fill = 0)
    
    x_offset = 90
    if 'monthly' in rain:
        draw.text((x_offset, y_offset), f"{rain['monthly']:2.2f}\" month ", font = get_font(18), fill = 0)
    else:
        draw.text((x_offset, y_offset), "0.0\" month", font = get_font(18), fill = 0)

    # ---

    # Divider Line
    y_offset += 40
    draw.line(((pad + 20) , y_offset, (image.width - pad - 20), y_offset), fill = 0, width = 3)

    return image

# Draw a forecast day block from the x,y top left corner position for the block
def _draw_day(image, forecast, x, y):
    logging.info("Drawing day widgets")

    wind = Image.open(os.path.join(picdir, 'wind.jpg'))

    # container size
    width = 156
    pad = 10

    y_offset = 0

    # drawing utility
    d = ImageDraw.Draw(image)

    # Day of week
    x_offset = x + pad
    y_offset = y + pad
    
    day_date = get_datetime(forecast['date_str'])
    day_str = f"{day_date.strftime('%a')} "
    date_str = f"{day_date.strftime('%m/%d')} "

    d.text(((x_offset + 10), y_offset), day_str, font = get_font(22), fill = 0)
    d.text(((x_offset + 85), (y_offset + 6)), date_str, font = get_font(16), fill = 0)

    y_offset += 30

    # Icon
    icon = get_icon(forecast)
    image.paste(icon, ((x + 55), y_offset))

    # Description
    x_offset += 15
    y_offset += 50
    d.text((x_offset, y_offset), f"{forecast['description']} ", font = get_font(16), fill = 0)
 
    # Divider Line
    x_offset -= 10
    y_offset += 25
    d.line((x_offset, y_offset, (x_offset + width - pad - pad - pad), y_offset), fill = 0, width = 3)

    # Temp
    x_offset += 20
    y_offset += 10
    d.text((x_offset, y_offset), f"{forecast['temp']:3.0f}°", font = get_font(54), fill = 0)

    # Wind Speed
    x_offset -= 15
    y_offset += 70
    d.text((x_offset, y_offset), f"{forecast['wind_speed']:2.1f} mph", font = get_font(16), fill = 0)
    image.paste(wind, ((x_offset + 80), (y_offset - 5)))

    return image

# Draw the forecast to the display image
def _draw_forecast(image, forecast):
    logging.info("Iterating Forecast Days")

    offset = 10
    day_vert = 245
    day_width = 156
    day_register = 'day'
    time_counter = 0

    # Iterate over forecast days in 'list' and draw widgets for each
    for x in forecast['list']:
        temp = x['main']['temp']
        category = x['weather'][0]['main']
        description = x['weather'][0]['description']
        wind_speed = x['wind']['speed']
        date_str = x['dt_txt']
        day = get_day_name(get_datetime(date_str))

        f = {
            'date_str': date_str, 
            'temp': temp, 
            'category': category, 
            'description': description, 
            'wind_speed': wind_speed
            }

        # forecast data returns a dict for every 3 hours. 
        # We only want daily so find unique days and get third reporting for noon for that day.
        if day_register == day:
            if time_counter == 3:
                image = _draw_day(image, f, offset, day_vert) # Draw the day widget
                offset += day_width
            time_counter += 1
        else:
            day_register = day
            time_counter = 0

    return image

# Create and draw the weather widgets onto a new display image
def draw(dims, weather, forecast):
    width, height = dims

    # Create a new image to draw our display on
    display_image = Image.new('1', (width, height), 255)  # 255: white

    # Draw current conditions to the display image
    display_image = _draw_current_weather(display_image, weather)

    # Draw the forecast to the display image
    display_image = _draw_forecast(display_image, forecast)

    return display_image
