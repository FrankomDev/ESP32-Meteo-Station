import network
import options as options
import time
import ntptime
import machine
import send as send

wlan = network.WLAN(network.STA_IF)
wlan.active(False)

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