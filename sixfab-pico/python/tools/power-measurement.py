import time
import utime
import machine
import network
import math

from pico_lte.core import PicoLTE
from pico_lte.utils.atcom import ATCom

def stress_cpu(duration_seconds):
    end_time = utime.time() + duration_seconds
    a, b = 0, 1
    while utime.time() < end_time:
        # Perform a calculation that requires CPU work
        c = a + b
        a, b = b, c

print("Will sleep for 5 seconds")
time.sleep(5)

print("Will stress CPU for ten seconds")
stress_cpu(10)

print("Will try to register LTE")
picoLTE = PicoLTE()
picoLTE.network.register_network()
picoLTE.network.get_pdp_ready()

print("Will sleep for 5 seconds")
time.sleep(5)

print("Will connect to WiFi")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

ssid = 'SSID'
password = 'PASSWORD'

wifi_attempt_count = 0
wifi_max_attempts = 50

try:
    wlan.connect(ssid, password)
except OSError as error:
    print("WiFi OS error")

while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
    
print("Connection to WiFi successful")

print("Will sleep for 5 seconds")
time.sleep(5)

print("Will stop modem and sleep for 5 seconds")
picoLTE.base.power_off()
atcom = ATCom()
atcom.send_at_comm("AT+QPOWD=0")
time.sleep(5)

print("Will stop WiFi and sleep for 5 seconds")
wlan = network.WLAN(network.STA_IF)
wlan.disconnect()
wlan.active(False)
time.sleep(5)

print("Will go to lightsleep for 10 seconds")
machine.lightsleep(10000)

#print("Will deep sleep in 5s")
#time.sleep(5)
#machine.deepsleep()