import urequests
import bme280 as bme280
import json
import options as options
import machine
import time
import watersensor as water

def send_data():
    url = options.WEB_URL
    bme=bme280.BME280()
    d = bme.get_data()
    rain = water.is_raining()

    data = {
        "temperature": d[0],
        "pressure": d[1],
        "humidity": d[2],
        "rain": rain
    }

    r=urequests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
    r.close()
    time.sleep_ms(200)
    machine.deepsleep(900000)