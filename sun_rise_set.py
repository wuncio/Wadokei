from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
import timezonefinder, pytz
from geopy.geocoders import Nominatim


def sun_set_raise(name, latitude, longitude):
    locations = {
        "TOKYO": {"city": "Tokyo", "country": "Japan", "timezone": "Asia/Japan", "latitude": 35.652832,
                  "longitude": 139.839478},
        "TOKIO": {"city": "Tokyo", "country": "Japan", "timezone": "Asia/Japan", "latitude": 35.652832,
                  "longitude": 139.839478},
        "KIOTO": {"city": "Kyoto", "country": "Japan", "timezone": "Asia/Japan", "latitude": 35.011665,
                  "longitude": 135.768326},
        "KYOTO": {"city": "Kyoto", "country": "Japan", "timezone": "Asia/Japan", "latitude": 35.011665,
                  "longitude": 135.768326},
        "NARA": {"city": "Nara", "country": "Japan", "timezone": "Asia/Japan", "latitude": 34.29755280,
                 "longitude": 135.82797340},
        "WARSAW": {"city": "Warsaw", "country": "Poland", "timezone": "Europ/Warsaw", "latitude": 52.237049,
                   "longitude": 21.017532},
        "WARSZAWA": {"city": "Warsaw", "country": "Poland", "timezone": "Europe/Warsaw", "latitude": 52.237049,
                     "longitude": 21.017532}
    }
    name = name.upper()
    if name in locations.keys():
        city = locations[name]["city"]
        country = locations[name]["country"]
    else:
        # Finds city and country by coordinates
        geolocator = Nominatim(user_agent="myapp")
        location = geolocator.reverse((latitude, longitude), language="en")
        address = location.raw['address']
        city = address.get('city', '')
        country = address.get('country', '')

    # Calculating timezone
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.certain_timezone_at(lat=latitude, lng=longitude)
    timezone = pytz.timezone(timezone_str)
    date = datetime.now()

    place = LocationInfo(city, country, timezone_str, latitude, longitude)

    # Calculating sunrise and sunset
    try:
        s = sun(place.observer, date=date)
    except ValueError:
        return False
    sunrise = s['sunrise'] + timezone.utcoffset(date)
    sunset = s['sunset'] + timezone.utcoffset(date)
    if sunrise.day != sunset.day:
        if sunrise.day - 1 == date.day:
            sunrise = sunrise - timedelta(days=1)
        elif sunset.day + 1 == date.day:
            sunset = sunset + timedelta(days=1)

    # Calculating length of the day
    sun_long = sunset - sunrise
    sun_sec = sun_long.total_seconds()
    sun_hours = sun_sec / 3600
    sun_hours_wadokei = sun_hours/6

    # Calculating length of the night
    moon_sec = 86400 - sun_sec
    moon_hours = moon_sec / 3600
    moon_hours_wadokei = moon_hours / 6

    time_dec_sunrise = format(sunrise, '%H:%M:%S')
    (h, m, s) = time_dec_sunrise.split(":")
    sunrise_dec = int(h) + int(m)/60 + int(s)/3600
    print(sunrise_dec)

    time_dec_sunset = format(sunset, '%H:%M:%S')
    (h, m, s) = time_dec_sunset.split(":")
    sunset_dec = int(h) + int(m) / 60 + int(s) / 3600
    print(sunset_dec)

    return [sunrise, sunset, sun_hours, moon_hours, sun_hours_wadokei, moon_hours_wadokei, sunrise_dec, sunset_dec]
