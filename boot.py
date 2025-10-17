import network
import options as options
#import bme280 as bme280
import time
import ntptime
import machine
import send as send

wlan = network.WLAN(network.STA_IF)
wlan.active(False)

"""def get_data_from_bme():
    send.send_data()
    machine.deepsleep(899000) # 14.98333 minutes"""

if not wlan.isconnected():
    wlan.active(True)
    print("Connecting...")
    wlan.connect(options.WIFI_SSID, options.WIFI_PASSWORD)
    while not wlan.isconnected():
        pass
    print("Connected")
    
try:
    ntptime.host = options.NTP_SERVER
    ntptime.settime()
except Exception as e:
    print("error: "+str(e))

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Sent from deepsleep")
    send.send_data()
else:
    rtc = machine.RTC()
    while rtc.datetime()[5] % 15 != 0:
        time.sleep(3)
    print("Sent from loop")
    send.send_data()
