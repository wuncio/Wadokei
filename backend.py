from flask import Flask, jsonify, render_template, request
import time
from pytz import timezone
from datetime import datetime
import webbrowser

from sys import exit
from sun_rise_set import sun_set_raise
from location_calc import lat_long
import ipapi

from timezonefinder import TimezoneFinder
import os
import math

# Functions to set up timezone info
# Gests lat and long for local timezone based on ip adress
def get_local_coors():
    try:
        ip = ipapi.location()
    except:
        print("Brak internetu")
        exit(0)
    city = ip["city"]
    region = ip["region"]
    country = ip["country_name"]
    place = f"{city} {region} {country}"
    return lat_long(place)

# Gets lat and long for selected timezone given as a string:
def get_time_zone_coords(time_zone: str):
    try:
        with open("data.txt", "w") as f:
            f.write(f"{time_zone}")
        return lat_long(time_zone)
    except:
        print("Niepoprawna strefa czasowa - nie można znaleźć koordynatów")
        exit(0)
# Generalised method for getting coordinates
def get_coords(time_zone: str):
    if time_zone.lower()=="local":
        return get_local_coors()
    else:
        return get_time_zone_coords(time_zone)


def change_time_zone(location: str):
    global time_zone, latitude, longitude, day, night, sunrise, sunset, quarter, days
    time_zone = location
    print(time_zone)
    coords = get_coords(location)
    if coords == 1 or coords == 0:
        print("Błędna nazwa, przekierowanie do lokalizacji lokalnej")
        coords = get_coords("local")

    print(coords)
    latitude = float(coords[1])
    longitude = float(coords[2])
    sun = sun_set_raise("", latitude, longitude)

    day = sun[2]
    night = sun[3]
    sunrise = sun[6]
    sunset = sun[7]
    days = sun[8]
    print("A", days)

    quarter["N"]["q_s"] = sun[7]
    quarter["N"]["q_e"] = sun[6]
    quarter["D"]["q_s"] = sun[6]
    quarter["D"]["q_e"] = sun[7]




#Set up global timezone variables
latitude = None
longitude = None

day = None
night = None
sunrise = None
sunset = None

quarter = {
    "N": {"deg_s": 180, "deg_e": 360, "q_s": sunset, "q_e": sunrise},
    "D": {"deg_s": 0, "deg_e": 180, "q_s": sunset, "q_e": sunrise}
}

dates_prz = {
    "PZ":{"k_s":0-58.8, "d":89, "d_sum":89, "d_p":0},
    "RW":{"k_s":90-58.8, "d":93, "d_sum":182, "d_p":89},
    "PL":{"k_s":180-58.8, "d":93, "d_sum":275, "d_p":182},
    "RJ":{"k_s":270-58.8, "d":90, "d_sum":365, "d_p":275}
}

#Load initial timezone for loal time zone
with open('data.txt') as f:
    time_zone = f.readline()
change_time_zone(time_zone)


webbrowser.open('http://localhost:5000', new=0, autoraise=True) #Otwiera dwie strony

app = Flask(__name__)

# Time scaling factor (for fast time simulation)
time_scale_factor = 1  # 10 minutes pass in 30 seconds (10 * 60) / 30


@app.route('/')
def index():
    return render_template('zegar.html')  # This will load the frontend HTML

@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    global time_zone
    data = request.get_json()
    new_tz = data.get('timezone')

    if new_tz:
        change_time_zone(new_tz)
        return jsonify({"message": "Timezone updated", "time_zone": time_zone}), 200
    else:
        return jsonify({"error": "No timezone provided"}), 400 #Selects new time zone based on HTML dropdown input
@app.route('/get_timezone_info', methods=['GET'])
def get_timezone_info():
    global night, day, time_zone
    if time_zone == "local":
        date = datetime.now()
    else:
        time_zone = "Europe/Moscow"
        try:
            tz = timezone(time_zone)
            date = datetime.now(tz)
        except Exception as e:
            coords = lat_long(time_zone)
            if coords != 1 and coords != 0:
                print(coords)
                latitude1 = float(coords[1])
                longitude1 = float(coords[2])
                obj = TimezoneFinder()
                print(coords)
                print(obj.timezone_at(lng=longitude1, lat=latitude1))
                print(type(obj.timezone_at(lng=longitude1, lat=latitude1)))
                print(time_zone)
                print(type(time_zone))
                date = datetime.now(obj.timezone_at(lng=longitude1, lat=latitude1))
                print(date)
            print(f"Invalid timezone: {time_zone}. Falling back to local.")
            date = datetime.now()
    date_dec = int(format(date, '%H')) + int(format(date, '%M')) / 60 + int(format(date, '%S')) / 3600
    if sunrise <= date_dec <= sunset:
        temp = "D"
    else:
        temp = "N"
    print(temp)
    deg_start = quarter[temp]["deg_s"]
    deg_end = quarter[temp]["deg_e"]
    qt_start = quarter[temp]["q_s"]
    qt_end = quarter[temp]["q_e"]
    return jsonify({
        'hours': format(date, '%H'),
        'minutes': format(date, '%M'),
        'seconds': format(date, '%S'),
        "len_day": day,
        "len_night": night,
        "deg_start": deg_start,
        "deg_end": deg_end,
        "qt_start": qt_start,
        "qt_end": qt_end
    })

@app.route('/check_date', methods=['GET'])
def check_date():
    if 0 <= days < 89:
        temp = "PZ"
    elif 89 <= days < 182:
        temp = "RW"
    elif 182 <= days < 275:
        temp = "PS"
    else:
        temp = "RJ"
    return jsonify({
        "days": dates_prz[temp]["d_sum"] - days,
        "angle": dates_prz[temp]["k_s"]+ 90*(days - dates_prz[temp]["d_p"])/dates_prz[temp]["d"]
    })

@app.route('/change', methods=['POST'])
def change_scale():
    global time_scale_factor
    time_scale_factor = 100
    return jsonify({'message': 'Wartość zmiennej została zmieniona', 'newValue': time_scale_factor})

if __name__ == "__main__":
    app.run(debug=False, threaded = False)
