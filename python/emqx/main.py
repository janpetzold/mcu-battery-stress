import json
import network
import time
import utime
import ubinascii
import machine

from machine import RTC
from machine import Pin
from machine import Timer
from pico_lte.core import PicoLTE
from pico_lte.utils.status import Status
from pico_lte.common import debug

# Get this via "micropython-umqtt.simple2"
from umqtt.simple import MQTTClient

debug.set_level(1)

picoLTE = PicoLTE()
user_led = Pin(22, mode=Pin.OUT)

def get_machine_id():
    id = ubinascii.hexlify(machine.unique_id()).decode()
    debug.info("Machine ID is " + id)
    return id

def get_current_time():
    debug.debug("Getting current device time")
    rtc = RTC()
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    # Format the timestamp as ISO8601 - this assumes the RTC is set to UTC time
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, hour, minute, second)

def get_temperature():
    debug.debug("Getting temperature")
    sensor_temp = machine.ADC(4)
    conversion_factor = 3.3 / (65535)
    raw_temperature = sensor_temp.read_u16() * conversion_factor

    # Convert raw temperature to Celsius
    temperature_c = 27 - (raw_temperature - 0.706) / 0.001721
    debug.info("Temperature is " + str(temperature_c) + "°C")

    return temperature_c

def get_location():
    debug.info("Getting GPS position (50m)")
    picoLTE.gps.turn_on(accuracy=3)

    for _ in range(0, 30):
        result = picoLTE.gps.get_location()
        debug.debug(result)

        if result["status"] == Status.SUCCESS:
            debug.debug("GPS fixed. Getting location data...")

            loc = result.get("value")
            debug.info("Latitude is " + str(loc[0]) + ", longitude " + str(loc[1]))
            
            picoLTE.gps.turn_off()
            return loc
        time.sleep(2)  # 30*2 = 60 seconds timeout for GPS fix. Usually takes 5-25s for me.
    return [0,0]

def start_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    ssid = 'SSID'
    password = 'PASSWORD'

    wifi_attempt_count = 0
    wifi_max_attempts = 50

    debug.info("Connecting to WiFi")
    
    try:
        wlan.connect(ssid, password)
    except OSError as error:
        debug.info("WiFi OS error")
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)

    debug.info("Connection to WiFi successful")

def publish_message(payload):
    debug.debug("Publishing data to EMQX MQTT broker")
    
    mqtt_broker = 'broker.emqx.io'
    client_id = 'client100001'
    topic = 'batteryhub/status'

    client = MQTTClient(client_id, mqtt_broker)
    client.connect()
    debug.debug("Connected to broker " + mqtt_broker)
    client.publish(topic, payload)
    debug.info("Message published to " + topic)
    client.disconnect()

# Timeout functions - mainly needed to make sure that WiFi connection and
# MQTT publishing don't block the loop forever in case of issues
def on_timeout(timer):
    debug.info("Timeout of function WiFi or MQTT, will sleep for five minutes and reboot")
    machine.lightsleep(300000)
    machine.reset()
    
def start_task_with_timeout(task, task_name, timeout_ms, *args, **kwargs):
    debug.debug("Starting task " + task_name + " with timeout of " + str(timeout_ms) + "ms")
    # Initialize the timer. Only -1 supported (https://forums.raspberrypi.com/viewtopic.php?t=314700)
    timer = machine.Timer(-1)
    
    # Start the timer with the specified timeout duration and callback function
    timer.init(mode=machine.Timer.ONE_SHOT, period=timeout_ms, callback=on_timeout)
    
    # Start the long-running task with parameters (if supplied)
    task(*args, **kwargs)
    
    # Task finished before timeout
    timer.deinit()
    debug.info("Task " + task_name + " finished before timeout")

def run_all():
    user_led.value(1)
    machine_id = get_machine_id()
    current_time = get_current_time()
    temperature = get_temperature()
    location = get_location()
    
    payload_json = {"i": machine_id, "t": current_time, "c": str(temperature), "la": location[0], "lo": location[1]}
    payload = json.dumps(payload_json)
    debug.debug("Payload is")
    debug.debug(payload)

    start_task_with_timeout(start_wifi, "wifi", 60000)
    start_task_with_timeout(publish_message, "mqtt-publish", 60000, payload)
    user_led.value(0)
    
    debug.info("Will sleep now")
    time.sleep(1)

    # Approach #1 - just sleep for 20mins before reboot. Used as baseline for power saving.
    # time.sleep(1200)

    # Approach #2 - sleep mode with defined wakeup after 20mins
    machine.lightsleep(60000)

# Start me up!
while True:
    run_all()