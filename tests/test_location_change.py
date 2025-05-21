import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
import time
import requests
from backend import app

# Wersja uproszczona – zakładamy, że zmiana lokalizacji wymaga restartu aplikacji z nową lokalizacją.
# W prawdziwej aplikacji lokalizacja powinna być zmieniana dynamicznie – np. z formularza.

def run_app_with_location(location_name):
    # Symulacja uruchomienia aplikacji z lokalizacją jako zmienną środowiskową
    import os
    os.environ["TEST_LOCATION"] = location_name
    app.run(port=5001, debug=False, use_reloader=False)


def test_change_location():
    # Uruchomienie aplikacji Flask z lokalizacją: Łódź
    location = "Łódź"
    flask_thread = threading.Thread(target=run_app_with_location, args=(location,))
    flask_thread.daemon = True
    flask_thread.start()
    time.sleep(3)

    # Pobierz dane czasu z aplikacji
    res1 = requests.get("http://localhost:5001/time").json()
    assert "hours" in res1

    # Uruchom aplikację Flask z inną lokalizacją (np. Tokio) – w innym porcie
    flask_thread_tokyo = threading.Thread(target=run_app_with_location, args=("Tokio",))
    flask_thread_tokyo.daemon = True
    flask_thread_tokyo.start()
    time.sleep(3)

    res2 = requests.get("http://localhost:5001/time").json()
    assert "hours" in res2

    # Sprawdź czy czasy się różnią (w uproszczeniu)
    assert res1 != res2, "Czas nie zmienił się po zmianie lokalizacji"

