from flask import Flask, jsonify, render_template
import time
from datetime import datetime
import webbrowser

from sys import exit
from sun_rise_set import sun_set_raise
from location_calc import lat_long
import ipapi
import math

try:
    ip = ipapi.location()
except:
    print("Brak internetu")
    exit(0)
city = ip["city"]
region = ip["region"]
country = ip["country_name"]
place = f"{city} {region} {country}"

coords = lat_long(place)
latitude = float(coords[1])
longitude = float(coords[2])
sun = sun_set_raise("", latitude, longitude)

day = sun[2]
night = sun[3]
sunrise = sun[6]
sunset = sun[7]

webbrowser.open('http://localhost:5000', new=0, autoraise=True) #Otwiera dwie strony

quarter = {
    "N": {"pi_s": 0, "pi_e": math.pi, "q_s": sunset, "q_e": sunrise},
    "D": {"pi_s": math.pi, "pi_e": math.pi * 2, "q_s": sunrise, "q_e": sunset}
}
app = Flask(__name__)

# Time scaling factor (for fast time simulation)
time_scale_factor = 1  # 10 minutes pass in 30 seconds (10 * 60) / 30


@app.route('/')
def index():
    return render_template('index.html')  # This will load the frontend HTML


@app.route('/time', methods=['GET'])
def get_time():
    global day, night
    # Get current time
    date = datetime.now()
    date_dec = int(format(date, '%H')) + int(format(date, '%M'))/60 + int(format(date, '%S'))/3600
    if sunrise <= date_dec <= sunset:
        temp = "D"
    else:
        temp = "N"
    print(temp)
    pi_start = quarter[temp]["pi_s"]
    pi_end = quarter[temp]["pi_e"]
    qt_start = quarter[temp]["q_s"]
    qt_end = quarter[temp]["q_e"]
    return jsonify({
        'hours': format(date, '%H'),
        'minutes': format(date, '%M'),
        'seconds': format(date, '%S'),
        "len_day": day,
        "len_night": night,
        "pi_start":pi_start,
        "pi_end": pi_end,
        "qt_start": qt_start,
        "qt_end": qt_end
    })

@app.route('/change', methods=['POST'])
def change_scale():
    global time_scale_factor
    time_scale_factor = 100
    return jsonify({'message': 'Wartość zmiennej została zmieniona', 'newValue': time_scale_factor})

if __name__ == "__main__":
    app.run(debug=False, threaded = False)
