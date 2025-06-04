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

# Funkcja podająca koordynaty (długość i szerekość geograficzna użytkownika) na postawie pobranego adresu ip
# Zwraca koordynaty jako listę zawierającą nazwę miejsca oraz szerokość i długość - w tej kolejności
def get_local_coors() -> [str, float, float]:
    try:
        ip = ipapi.location()
    except:
        exit(0)
    city = ip["city"]
    region = ip["region"]
    country = ip["country_name"]
    place = f"{city} {region} {country}"
    return lat_long(place)

# Funkcja zwraca koordynaty (długość i szerekość geograficzna użytkownika) na postawie nazwy strefy czaasowej
# Dodatkowo zapisuje do pliku tekstowego nazwę strefy czasowej do późniejszego odczytania
def get_time_zone_coords(time_zone: str) -> [str, float, float]:
    try:
        with open("data.txt", "w") as f:
            f.write(f"{time_zone}")
        return lat_long(time_zone)
    except:
        exit(0)

# Ogólna funkcja zwracająca koordynaty
def get_coords(time_zone: str) -> [str, float, float]:
    if time_zone.lower()=="local":
        return get_local_coors()
    else:
        return get_time_zone_coords(time_zone)

# Funkcja aktualizująca strefę czasową na taką, której nazwę podano w parametrze "location"
# Aktualizacja strefy czasowej oznacza również aktualizację związanych z nią wartości podawanych potem do zegara
def change_time_zone(location: str) -> None:
    global time_zone, latitude, longitude, day, night, sunrise, sunset, quarter, days
    time_zone = location

    coords = get_coords(location)

    if coords == 1 or coords == 0:
         coords = get_coords("local")

    latitude = float(coords[1])
    longitude = float(coords[2])

    #Oblicza i zwaraca charakterystki doby słonecznej (godzina wsocdu/zachodu, długość dnia/nocy) na podstawie koordynatów
    sun = sun_set_raise("", latitude, longitude)

    day = sun[2]
    night = sun[3]
    sunrise = sun[6]
    sunset = sun[7]
    days = sun[8]

    quarter["N"]["q_s"] = sun[7]
    quarter["N"]["q_e"] = sun[6]
    quarter["D"]["q_s"] = sun[6]
    quarter["D"]["q_e"] = sun[7]

#Inicjowanie globalnych zmiennych
latitude = None
longitude = None

day = None
night = None
sunrise = None
sunset = None

# Tablica przechowujące wartości o dobie słonecznej obecnej strefy czasowej
# N - noc, D - dzień
# deg_s - kąt zaczynający poręs doby na tarczy zegara
# deg_e - kąt kończący porę dnia na tarczy zegara
# q_s - godzina rozpoczęcia słonecznej pory doby (zachód słońca dla nocy, wschód słońca dla dnia)
# q_e - godzina zaończenia słonecznej pory doby (wschód słońca dla nocy, zachód słońca dla dnia)

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

# Wczytuje pierwszą strefę czasową z pliku tekstowego
with open('data.txt') as f:
    time_zone = f.readline()

# Zmienia strefę czasową na wartość wczytaną z pliku
change_time_zone(time_zone)

webbrowser.open('http://localhost:5000', new=0, autoraise=True) #Otwiera dwie strony

app = Flask(__name__)

# Czynnik skalowania czasu
time_scale_factor = 1  # 10 minutes pass in 30 seconds (10 * 60) / 30


@app.route('/')
def index():
    return render_template('zegar.html')  # This will load the frontend HTML

# Funkcja służaca do pobierania nazwy strefy czasowej z frontendu
# Wywoływana przez skrypt zegara
@app.route('/set_timezone', methods=['POST'])
def set_timezone():
    global time_zone
    data = request.get_json()

    # Wczytuje element "timezone" ze pliku HTML zegara
    new_tz = data.get('timezone')
    print("Timezone set via website to: " + new_tz)


    if new_tz and not new_tz == "":
        change_time_zone(new_tz)
        print("Timezone changed to: " + new_tz + " successfully.")
        return jsonify({"message": "Timezone updated", "time_zone": time_zone}), 200

    else:
        print("Wrong timezone value, either missing or empty. Dafaulting to: " + time_zone)
        return jsonify({"error": "No timezone provided"}), 400

# Funkcja przekazująca wyliczone informacje o dobie słonecznej do pliku HTML z zegarem
@app.route('/get_timezone_info', methods=['GET'])
def get_timezone_info():
    global night, day, time_zone, quarter

    if time_zone.lower() == "local":
        date = datetime.now()
        print("Collected data for timezone: local")

    else:
        try:
            tz = timezone(time_zone)
            print("Collected data for timezone:" + time_zone)
            date = datetime.now(tz)
            print("Date retrieved.")

        except Exception as e:
            coords = lat_long(time_zone)
            print("Coordinates calculated.")
            print(coords)

            if coords != 1 and coords != 0:
                latitude1 = float(coords[1])
                longitude1 = float(coords[2])
                obj = TimezoneFinder()
                print("Timezone at calculated coordinates: " + obj.timezone_at(lng=longitude1, lat=latitude1))
                date = datetime.now(timezone(obj.timezone_at(lng=longitude1, lat=latitude1)))
            else:
                date = datetime.now()

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

@app.route('/get_last_timezone', methods = ['GET'])
def get_last_timezone():
    try:
        with open('data.txt', 'r') as f:
            lines = f.readlines()
            print("Timezone read froma data.txt: " + lines[-1].strip())
            if lines:
                return jsonify({'timezone': lines[-1].strip()})
    except Exception as e:
        return jsonify({'error': str(e)})
    return jsonify({'timezone': None})

if __name__ == "__main__":
    app.run(debug=False, threaded = False)


