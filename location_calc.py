from geopy.exc import GeocoderUnavailable
from geopy.geocoders import Nominatim



def lat_long(name):
    locations = {
        "TOKYO": {"latitude":35.652832, "longitude":139.839478},
        "TOKIO": {"latitude":35.652832, "longitude":139.839478},
        "KIOTO": {"latitude":35.011665, "longitude":135.768326},
        "KYOTO": {"latitude":35.011665, "longitude":135.768326},
        "NARA": {"latitude":34.29755280, "longitude":135.82797340},
        "WARSAW": {"latitude":52.237049, "longitude":21.017532},
        "WARSZAWA": {"latitude":52.237049, "longitude":21.017532}
    }
    name = name.upper()
    if name in locations.keys():
        latitude = locations[name]["latitude"]
        longitude = locations[name]["longitude"]
        show = name
    else:
        try:
            geolocator = Nominatim(user_agent='myapp')
            location = geolocator.geocode(name, language="pl")
            print(2, location)
        except GeocoderUnavailable:
            print(1)
            return 1

        if location is None:
            return 0
        latitude = location.raw["lat"]
        longitude = location.raw["lon"]
        show = location.raw["display_name"]
    return [show, latitude, longitude]

