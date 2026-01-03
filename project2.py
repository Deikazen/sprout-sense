import time
import board
import busio
import adafruit_dht
import RPi.GPIO as GPIO
import requests
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn

# ===============================
# KONFIGURASI API
# ===============================
API_URL = "https://uncially-lithy-rubie.ngrok-free.dev/api/soil"   # GANTI IP SERVER

# ===============================
# GPIO SETUP
# ===============================
POMPA_PIN = 17   # GPIO17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(POMPA_PIN, GPIO.OUT)
GPIO.output(POMPA_PIN, GPIO.LOW)

# ===============================
# KONDISI IDEAL TOGE
# ===============================
SOIL_ON = 60
SOIL_OFF = 75

# ===============================
# SENSOR
# ===============================


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS1115(i2c)
soil_channel = AnalogIn(ads, 0)

# ===============================
# FUNGSI
# ===============================


def convert_soil(raw):
    min_val = 10000
    max_val = 30000
    percent = 100 - ((raw - min_val) / (max_val - min_val) * 100)
    return max(0, min(100, percent))


def post_soil_data(soil):
    payload = {
        "moisture": round(soil, 1)
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=5)
        print(f"POST API status: {response.status_code}")
    except requests.RequestException as e:
        print("POST API gagal:", e)


print("SYSTEM RUNNING (POMPA + POST API)...\n")

# ===============================
# MAIN LOOP
# ===============================
try:
    while True:
        raw = soil_channel.value
        soil = convert_soil(raw)

        # ===============================
        # LOGIKA POMPA
        # ===============================
        if soil < SOIL_ON:
            GPIO.output(POMPA_PIN, GPIO.HIGH)
            pompa_status = "ON"
        elif soil >= SOIL_OFF:
            GPIO.output(POMPA_PIN, GPIO.LOW)
            pompa_status = "OFF"
        else:
            pompa_status = "STANDBY"

        # ===============================
        # POST DATA KE API
        # ===============================
        post_soil_data(soil)

        # ===============================
        # OUTPUT
        # ===============================
        print("--------------------------------")
        print(f"Soil Moisture : {soil:.1f}%")
        print(f"Pompa         : {pompa_status}")
        print("Data dikirim ke API")

        # JEDA 1 MENIT
        time.sleep(60)

except KeyboardInterrupt:
    print("\nProgram dihentikan")

finally:
    GPIO.output(POMPA_PIN, GPIO.LOW)
    GPIO.cleanup()
