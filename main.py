from sys import exit
from sun_rise_set import location_eph
from location_calc import lat_long
import ipapi

print("Wprowadź nazwę miejsca w którym się znajdujesz (Jeżeli chcesz wyszukać miejsce automatycznie wpisz 1)")
name = input("")
if name == "1":
    try:
        ip = ipapi.location()
    except:
        print("Brak internetu")
        exit(0)
    city = ip["city"]
    region = ip["region"]
    country = ip["country_name"]
    place = f"{city} {region} {country}"
else:
    place = name

sun = location_eph(name)
print(sun)
"""
if coords == 0:
    print("Podana lokalizacja nie może zostać wyszukana")
elif coords == 1:
    print("Brak internetu")
else:
    print(coords)
    latitude = float(coords[1])
    longitude = float(coords[2])
    sun = sun_set_raise(name, latitude, longitude)
    if not sun:
        print("W tej lokacji słońce nie wschodzi lub nie zachodzi") #Arrival Heights Laboratory, Zackenberg grenlandia
    else:
        print("Wschód słońca:", format(sun[0], '%H:%M:%S'))
        print("Zachód słońca:", format(sun[1], '%H:%M:%S'))
        print("Długość dnia (w godz):", sun[2])
        print("Długość nocy (w godz):", sun[3])
        print("Długość nocy (w godz):", sun[3]/2)
        print("Długość nocy (w godz):", 24 - sun[3] / 2)
        print("Długość godziny dziennej (wadoke):", sun[4])
        print("Długość godziny nocnej (wadoke):", sun[5])
"""