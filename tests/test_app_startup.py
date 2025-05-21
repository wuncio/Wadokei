import subprocess
import time
import requests
import os
import sys
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Ścieżka do katalogu głównego
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def run_app():
    os.system("python backend.py")

def test_app_stability():
    # Start aplikacji Flask w osobnym wątku
    flask_thread = threading.Thread(target=run_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Poczekaj aż serwer się uruchomi
    time.sleep(3)

    # Selenium - opcje przeglądarki
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # bez otwierania okna
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Otwórz aplikację
        driver.get("http://localhost:5000")
        time.sleep(1)

        # Sprawdź, czy tytuł strony lub element HTML jest dostępny
        assert "html" in driver.page_source.lower()

        # Sprawdź błędy w konsoli JS
        logs = driver.get_log("browser")
        js_errors = [
            log for log in logs
            if log["level"] == "SEVERE" and "favicon.ico" not in log["message"]
]
        assert not js_errors, f"JS errors: {js_errors}"

        # Sprawdzenie działania zegara (czy czas się zmienia)
        response1 = requests.get("http://localhost:5000/time").json()
        time.sleep(2)
        response2 = requests.get("http://localhost:5000/time").json()

        t1 = f"{response1['hours']}:{response1['minutes']}:{response1['seconds']}"
        t2 = f"{response2['hours']}:{response2['minutes']}:{response2['seconds']}"
        assert t1 != t2, f"Czas nie zmienił się: {t1} == {t2}"

    finally:
        driver.quit()
