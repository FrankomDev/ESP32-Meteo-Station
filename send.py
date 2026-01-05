from umqtt.simple import MQTTClient
import bme280 as bme280
import json
import options as options
import machine
import time
import watersensor as water
import json

def send_data():
    bme=bme280.BME280()
    d = bme.get_data()
    rain = water.is_raining()

    data = {
        "temperature": d[0],
        "pressure": d[1],
        "humidity": d[2],
        "rain": rain
    }

    c = MQTTClient("esp32-client", server=options.MQTT_ADDRESS, port=options.MQTT_PORT)
    c.connect()
    c.publish(b"messages", json.dumps(data).encode())
    c.disconnect()
    
    time.sleep_ms(200)
    machine.deepsleep(900000)