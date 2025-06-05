# PACKAGE INSTALLATION -------------------------------------------------------------------------------------------------
from subprocess import check_call
from sys import executable

try:
    from flask import Flask, jsonify, render_template, request
except ImportError:
    check_call([executable, "-m", "pip", "install", "flask"])
try:
    from pytz import timezone
except ImportError:
    check_call([executable, "-m", "pip", "install", "pytz"])
try:
    import ipapi
except ImportError:
    check_call([executable, "-m", "pip", "install", "ipapi"])
try:
    from astral import LocationInfo
    from astral.sun import sun
except ImportError:
    check_call([executable, "-m", "pip", "install", "astral"])
try:
    import timezonefinder
except ImportError:
    check_call([executable, "-m", "pip", "install", "timezonefinder"])
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
except ImportError:
    check_call([executable, "-m", "pip", "install", "geopy"])

from flask import Flask, jsonify, render_template, request
from pytz import timezone
from datetime import datetime
import webbrowser as wb
import ipapi
from json import load
from logging import ERROR, getLogger
from sun_rise_set import location_eph

# APP ------------------------------------------------------------------------------------------------------------------
log = getLogger('werkzeug')
log.setLevel(ERROR)
app = Flask(__name__)
wb.open('http://localhost:5000', new=0, autoraise=True)

# CONSTATNTS -----------------------------------------------------------------------------------------------------------
latitude = None
longitude = None
day = None
night = None
sunrise = None
sunset = None
custom_location = "europe/warsaw"

quarter = {
    "N": {"deg_s": 180, "deg_e": 360, "q_s": sunset, "q_e": sunrise},
    "D": {"deg_s": 0, "deg_e": 180, "q_s": sunset, "q_e": sunrise}
}

dates_zodiak = {
    "rat": {"k_s": 0 - 58.8 - 15, "d": 30, "d_sum": 30, "d_p": 0},
    "ox": {"k_s": 30 - 58.8 - 15, "d": 29, "d_sum": 59, "d_p": 30},
    "tiger": {"k_s": 60 - 58.8 - 15, "d": 30, "d_sum": 89, "d_p": 59},
    "rabbit": {"k_s": 90 - 58.8 - 15, "d": 29, "d_sum": 119, "d_p": 89},
    "dragon": {"k_s": 120 - 58.8 - 15, "d": 32, "d_sum": 150, "d_p": 119},
    "snake": {"k_s": 150 - 58.8 - 15, "d": 31, "d_sum": 181, "d_p": 150},
    "horse": {"k_s": 180 - 58.8 - 15, "d": 31, "d_sum": 212, "d_p": 181},
    "goat": {"k_s": 210 - 58.8 - 15, "d": 32, "d_sum": 244, "d_p": 212},
    "monkey": {"k_s": 240 - 58.8 - 15, "d": 31, "d_sum": 275, "d_p": 244},
    "rooster": {"k_s": 270 - 58.8 - 15, "d": 30, "d_sum": 305, "d_p": 275},
    "dog": {"k_s": 300 - 58.8 - 15, "d": 30, "d_sum": 335, "d_p": 305},
    "pig": {"k_s": 330 - 58.8 - 15, "d": 30, "d_sum": 365, "d_p": 335}
}


# PYTHON FUNCTIONS -----------------------------------------------------------------------------------------------------
def change_time_zone(location: str):
    global time_zone, latitude, longitude, day, night, sunrise, sunset, quarter, days

    if location.lower() == "local":
        coords = get_local_coors()
    else:
        coords = location_eph(location)

    if coords == 2:
        print("!!!ERROR: Location unknown. Switching to local location!!!")
        coords = get_local_coors()
    elif coords == 3:
        print("!!!ERROR: Can't connect to the internet. Switching to local location!!!")
        coords = get_local_coors()
    elif coords == 4:
        print("!!!ERROR: Unknown error. Switching to local location!!!")
        coords = get_local_coors()
    elif coords == 5:
        print("!!!ERROR: Not enough informations about location. Switching to local location!!!")
        coords = get_local_coors()
    elif coords == 6:
        print("!!!ERROR: in this location there are no sunsets or sunrises. Switching to local location!!!")
        coords = get_local_coors()
    else:
        with open("data.txt", "w") as f:
            f.write(f"{location}")

    sun = coords

    day = sun[2]
    night = sun[3]
    sunrise = sun[6]
    sunset = sun[7]
    days = sun[8]
    quarter["N"]["q_s"] = sun[7]
    quarter["N"]["q_e"] = sun[6]
    quarter["D"]["q_s"] = sun[6]
    quarter["D"]["q_e"] = sun[7]


def get_local_coors():
    try:
        ip = ipapi.location()
    except:
        print(f"!!!ERROR: No internet. Location will be set to default: {custom_location}!!!")
        return location_eph(custom_location)
    with open("data.txt", "w") as f:
        f.write("local")
    city = ip["city"]
    region = ip["region"]
    country = ip["country_name"]
    place = f"{city} {region} {country}"
    return location_eph(place)


# =================================================================================================
# OTHER ----------------------------------------------------------------------------------------------------------------
with open('data.txt', "r") as f:
    time_zone = f.readline()
change_time_zone(time_zone)


# JAVASCRIPT FUNCTIONS -------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('zegar.html')  # This will load the frontend HTML


@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    global time_zone
    data = request.get_json()
    new_tz = data.get('timezone')
    time_zone = new_tz
    if new_tz:
        change_time_zone(new_tz)
        return jsonify({"message": "Timezone updated", "time_zone": time_zone}), 200
    else:
        return jsonify({"error": "No timezone provided"}), 400  # Selects new time zone based on HTML dropdown input


@app.route('/get_timezone_info', methods=['GET'])
def get_timezone_info():
    global night, day, time_zone
    with open('data.txt') as f:
        name = f.readline().lower()
    if name == "local":
        date = datetime.now()
    else:
        with open("loactions.json", "r", encoding="utf-8") as f:
            saved = load(f)
        tz = timezone(saved[name]["timezone"])
        date = datetime.now(tz)
    date_dec = int(format(date, '%H')) + int(format(date, '%M')) / 60 + int(format(date, '%S')) / 3600
    if sunrise <= date_dec <= sunset:
        temp = "D"
    else:
        temp = "N"
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
    if 0 <= days < 30:
        temp = "rat"
    elif 30 <= days < 59:
        temp = "ox"
    elif 59 <= days < 89:
        temp = "tiger"
    elif 89 <= days < 119:
        temp = "rabbit"
    elif 119 <= days < 150:
        temp = "dragon"
    elif 150 <= days < 181:
        temp = "snake"
    elif 181 <= days < 212:
        temp = "horse"
    elif 212 <= days < 244:
        temp = "goat"
    elif 244 <= days < 275:
        temp = "monkey"
    elif 275 <= days < 305:
        temp = "rooster"
    elif 305 <= days < 335:
        temp = "dog"
    else:
        temp = "pig"
    print(temp, dates_zodiak[temp]["d_sum"] - days, dates_zodiak[temp]["k_s"] + 30 * (days - dates_zodiak[temp]["d_p"]) / dates_zodiak[temp]["d"])
    return jsonify({
        "days": dates_zodiak[temp]["d_sum"] - days,
        "angle": dates_zodiak[temp]["k_s"] + 30 * (days - dates_zodiak[temp]["d_p"]) / dates_zodiak[temp]["d"]
    })


if __name__ == "__main__":
    app.run(debug=False, threaded=False)
