import json
import network
import time
import utime
import ubinascii
import machine

from machine import RTC
from pico_lte.core import PicoLTE
from pico_lte.utils.status import Status
from pico_lte.common import debug

debug.set_level(1)

picoLTE = PicoLTE()

id = ubinascii.hexlify(machine.unique_id()).decode()
debug.info("Machine ID is " + id)

debug.debug("Registering network")
picoLTE.network.register_network()

debug.debug("PDP ready")
picoLTE.network.get_pdp_ready()

debug.debug("Getting current device time")
rtc = RTC()

def get_iso8601_timestamp():
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    # Format the timestamp as ISO8601 - this assumes the RTC is set to UTC time
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(year, month, day, hour, minute, second)

timestamp = get_iso8601_timestamp()
debug.info("Timestamp is " + timestamp)

debug.debug("Getting temperature")
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
raw_temperature = sensor_temp.read_u16() * conversion_factor

# Convert raw temperature to Celsius
temperature_c = 27 - (raw_temperature - 0.706) / 0.001721
debug.info("Temperature is " + str(temperature_c) + "°C")

debug.debug("Getting GPS position (50m)")
picoLTE.gps.turn_on(accuracy=3)

latitude = 0
longitude = 0

for _ in range(0, 30):
    result = picoLTE.gps.get_location()
    debug.debug(result)

    if result["status"] == Status.SUCCESS:
        debug.debug("GPS fixed. Getting location data...")

        loc = result.get("value")
        debug.info("GPS position determined:", loc)
        latitude = loc[0]
        longitude = loc[1]
        
        picoLTE.gps.turn_off()
        break
    time.sleep(2)  # 30*2 = 60 seconds timeout for GPS fix. Usually takes 5-25s for me.

payload_json = {"i": id, "t": timestamp, "c": str(temperature_c), "la": latitude, "lo": longitude}

debug.debug("Publishing data to Azure IoT Hub")
payload = json.dumps(payload_json)
debug.debug("Payload is")
debug.debug(payload)

result = picoLTE.azure.publish_message(payload)
debug.info("Message published to IoT hub with result", result)

# Sleep for 20mins before reboot - just used as baseline for power saving
utime.sleep(1200)

# After pausing reboot device to start cycle again
machine.reset()