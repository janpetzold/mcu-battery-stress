import network
import time
from time import sleep
import machine
from machine import Pin, SoftI2C
from bme680 import *

machine_id = str(machine.unique_id().hex())
print("Machine ID is " + machine_id)

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    print("Woke from a deep sleep")

# ESP32 - Pin assignment
# COnnection: Sensor SCK > Board pin 2, Sensor SDI > Board pin 15
i2c = SoftI2C(scl=Pin(2), sda=Pin(15))

bme = BME680_I2C(i2c=i2c)

time.sleep(2)

# Read sensor - consumption ~0.04A
try:
    temp = str(round(bme.temperature, 2)) + ' C'
    hum = str(round(bme.humidity, 2)) + ' %'
    pres = str(round(bme.pressure, 2)) + ' hPa'
    gas = str(round(bme.gas/1000, 2)) + ' KOhms'

    print('Temperature:', temp)
    print('Humidity:', hum)
    print('Pressure:', pres)
    print('Gas:', gas)
    print('-------')
except OSError as e:
    print('Failed to read sensor.')

print("Will go to sleep now")
time.sleep(2)

# Enter deep sleep - consumption should go down to ~0.003A
machine.lightsleep(10000)

ssid = 'Telekom-130198'  # Replace 'YourSSID' with your WiFi network name
password = 'Qh2vSaUK'  # Replace 'YourPassword' with your WiFi network password

# Initialize the WiFi station
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

# Connect to the WiFi network
wifi.connect(ssid, password)

# Wait until connected
while not wifi.isconnected():
    pass

# Success
print("Connected to WiFi!")
print("Network config:", wifi.ifconfig())