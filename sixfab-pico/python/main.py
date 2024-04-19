import json
import network
import time
import machine

from machine import Pin
from machine import Timer
from pico_lte.core import PicoLTE
from pico_lte.utils.atcom import ATCom
from pico_lte.common import debug

import clock
import temperature
import location

# Get this via "simple.umqtt"
from umqtt.simple import MQTTClient

debug.set_level(1)

picoLTE = PicoLTE()
atcom = ATCom()
user_led = Pin(22, mode=Pin.OUT)

def connect_lte():
    debug.debug("Registering network")
    picoLTE.network.register_network()

    debug.debug("PDP ready")
    picoLTE.network.get_pdp_ready()
    return True

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
        debug.critical("WiFi OS error")
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
        
    debug.info("Connection to WiFi successful")
    return True
    
def stop_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.disconnect()
    wlan.active(False)
    debug.info("Disconnected from WiFi")
    
def start_modem():
    picoLTE.base.power_on()
    debug.info("Activating modem")
    time.sleep(2)

def stop_modem():
    picoLTE.base.power_off()
    debug.info("Deactivated modem")
    time.sleep(2)
    
    atcom.send_at_comm("AT+QPOWD=0")
    debug.info("Modem powered down")
    time.sleep(2)
    
def publish_message_lte(payload):
    debug.debug("Publishing data to EMQX MQTT broker via LTE")
    
    try:
        picoLTE.mqtt.open_connection()
        picoLTE.mqtt.connect_broker()
        
        picoLTE.mqtt.publish_message(payload, 'batteryhub/status')
        return True
    except OSError as error:
        debug.critical("MQTT OS error (LTE)")

def publish_message_wifi(payload):
    debug.debug("Publishing data to EMQX MQTT broker via WiFi")

    try:
        client = MQTTClient('client100001', 'broker.emqx.io')
        client.connect()
        debug.debug("Connected to EMQX MQTT broker")
        client.publish(topic, payload)
        debug.info("Message published to " + 'batteryhub/status')
        client.disconnect()
        
        return True
    except OSError as error:
        debug.critical("MQTT OS error (WiFi)")
    
# Timeout functions - mainly needed to make sure that WiFi connection and
# MQTT publishing don't block the loop forever in case of issues
def on_timeout(timer):
    debug.info("Timeout of function LTE, WiFi or MQTT, will sleep for one minute and reboot")
    time.sleep(1)
    
    stop_modem()
    stop_wifi()
    
    machine.lightsleep(60000)
    machine.reset()
    
def start_task_with_timeout(task, task_name, timeout_ms, *args, **kwargs):
    debug.debug("Starting task " + task_name + " with timeout of " + str(timeout_ms) + "ms")
    # Initialize the timer. Only -1 supported (https://forums.raspberrypi.com/viewtopic.php?t=314700)
    timer = machine.Timer(-1)
    
    # Start the timer with the specified timeout duration and callback function
    timer.init(mode=machine.Timer.ONE_SHOT, period=timeout_ms, callback=on_timeout)
    
    # Start the long-running task with parameters (if supplied)
    returnVal = task(*args, **kwargs)
    
    # Task finished before timeout
    timer.deinit()
    
    debug.info("Task " + task_name + " finished before timeout")
    return returnVal

def run_all():
    debug.info("Starting procedure (again)")
    start_time = time.time()
    
    connect_network = "none"
    lte_success = False
    wifi_success = False
    
    user_led.value(1)
    
    machine_id = str(machine.unique_id().hex())
    current_time = clock.get_current_time()
    temperature_c = temperature.get_temperature()
    
    debug.info("Machine ID is " + machine_id + ", current time " + str(current_time) + ", temperature " + str(temperature_c))

    start_modem()
    loc = location.get_location()
    
    # First we try to connect via LTE
    lte_success = start_task_with_timeout(connect_lte, "lte", 90000)
    
    if(lte_success == True):
        connect_network = "lte"
    else:
        # Since LTE connect failed try with WiFi as fallback
        wifi_success = start_task_with_timeout(start_wifi, "wifi", 60000)
        if(wifi_success == True):
            connect_network = "wifi"
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    debug.info("Procedure execution time was " + str(elapsed_time) + "s")
    
    payload_json = {"i": machine_id, "n": connect_network, "t": current_time, "c": str(temperature_c), "la": loc[0], "lo": loc[1], "e": elapsed_time}
    payload = json.dumps(payload_json)
    debug.info(payload)
    
    if(lte_success == True):
        lte_mqtt_success= start_task_with_timeout(publish_message_lte, "mqtt-publish-lte", 90000, payload)
        
    if(wifi_success == True):
        wifi_mqtt_success = start_task_with_timeout(publish_message_wifi, "mqtt-publish-wifi", 60000, payload)
        stop_wifi()
    
    stop_modem()
    user_led.value(0)
    debug.info("Will sleep now")
    time.sleep(1)

    # Approach #1 - just sleep for 20mins before reboot. Used as baseline for power saving.
    # time.sleep(1200)
    
    # Approach #2 - light sleep mode with defined wakeup after 20mins
    machine.lightsleep(1200000)

    # Approach #3 - deep sleep mode with defined wakeup after 20mins
    #machine.deepsleep(60000)
    
    debug.info("Woke up, will reboot now")
    time.sleep(1)
    machine.reset()

# Start me up!
while True:
    run_all()