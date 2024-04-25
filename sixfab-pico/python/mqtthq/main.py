# Only added this as reference since it is a simple & straightforward alternative
# to IoT Hub. I could not get this to work out-of-the-box, umqtt had to be installed
# at the Raspberry Pico. See https://www.donskytech.com/umqtt-simple-micropython-tutorial/#htoc-h.

import network
import machine
import ubinascii
import time
from umqtt.simple import MQTTClient

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Fill in your network name (ssid) and password here:
ssid = 'SSID'
password = 'PASSWORD'
wlan.connect(ssid, password)

while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)

print("Connection to WiFi successful")

# MQTT Configuration
mqtt_broker = 'public.mqtthq.com'
client_id = 'client100001'
topic = 'foobar'
message = 'Hello MQTT'

# Function to connect and publish a message with authentication
def connect_and_publish():
    client = MQTTClient(client_id, mqtt_broker)
    client.connect()
    print(f"Connected to {mqtt_broker}")
    client.publish(topic, message)
    print(f"Message '{message}' published to {topic}")
    client.disconnect()

# Execute the function
connect_and_publish()