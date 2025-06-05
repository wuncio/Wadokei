from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, timedelta
import timezonefinder, pytz
import datetime as dat
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
import json


def location_eph(name):
    name = name.lower()
    with open("loactions.json", "r", encoding="utf-8") as f:
        saved = json.load(f)

    if name in saved.keys():
        city = saved[name]["city"]
        country = saved[name]["country"]
        timezone_str = saved[name]["timezone"]
        latitude = saved[name]["latitude"]
        longitude = saved[name]["longitude"]
    else:
        try:
            geolocator = Nominatim(user_agent="myapp")
            location = geolocator.geocode(name, language="en")
            if location is None:
                return 2  # Lokalizacja nie mogła być znaleziona
            latitude = float(location.raw["lat"])
            longitude = float(location.raw["lon"])
            location_coords = geolocator.reverse((latitude, longitude), language="en")
        except GeocoderUnavailable or GeocoderTimedOut:
            return 3  # Błąd łączności z serwerem map
        except:
            return 4  # Nieznany błąd

        address = location_coords.raw['address']
        city = address.get('city', '')
        country = address.get('country', '')
        if city == "" or country == "":
            return 5  # Zbyt mało danych, proszę podać dokładniejsza lokalizację
        tf = timezonefinder.TimezoneFinder()
        timezone_str = tf.certain_timezone_at(lat=latitude, lng=longitude)

        data = {"city": city, "country": country, "timezone": timezone_str, "latitude": latitude,
                "longitude": longitude}
        saved[name] = data
        with open("loactions.json", "w", encoding="utf-8") as f:
            json.dump(saved, f, ensure_ascii=False, indent=4)

    print("Country:", country)
    print("City:", city)
    print("Time zone:", timezone_str)
    print("---------------------------------------")
    date = datetime.now()
    timezone = pytz.timezone(timezone_str)
    if int(format(datetime.now(timezone).date(), "%m")) == 12 and int(format(datetime.now(timezone).date(), "%d")) >= 7:
        days_past = datetime.now(timezone).date() - dat.date(datetime.now(timezone).date().year, 12, 7)
    else:
        days_past = datetime.now(timezone).date() - dat.date(datetime.now(timezone).date().year-1, 12, 7)

    place = LocationInfo(city, country, timezone_str, latitude, longitude)

    # Calculating sunrise and sunset
    try:
        s = sun(place.observer, date=date)
    except ValueError:
        return 6  # W tej lokacji nie zachodzi lub nie wschodzi słońce
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
    sun_hours_wadokei = sun_hours / 6

    # Calculating length of the night
    moon_sec = 86400 - sun_sec
    moon_hours = moon_sec / 3600
    moon_hours_wadokei = moon_hours / 6

    time_dec_sunrise = format(sunrise, '%H:%M:%S')
    (h, m, s) = time_dec_sunrise.split(":")
    sunrise_dec = int(h) + int(m) / 60 + int(s) / 3600

    time_dec_sunset = format(sunset, '%H:%M:%S')
    (h, m, s) = time_dec_sunset.split(":")
    sunset_dec = int(h) + int(m) / 60 + int(s) / 3600

    return [sunrise, sunset, sun_hours, moon_hours, sun_hours_wadokei, moon_hours_wadokei, sunrise_dec, sunset_dec,
            days_past.days]
