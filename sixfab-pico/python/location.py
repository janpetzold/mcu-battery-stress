import time

from pico_lte.core import PicoLTE
from pico_lte.common import debug

def get_location():
    debug.info("Getting GPS position (50m)")
    picoLTE = PicoLTE()
    picoLTE.gps.set_priority(0)
    time.sleep(3)
    picoLTE.gps.turn_on(accuracy=3)

    for _ in range(0, 30):
        result = picoLTE.gps.get_location()
        debug.debug(result)

        if result["status"] == 0:
            debug.debug("GPS fixed. Getting location data...")

            loc = result.get("value")
            debug.info("Latitude is " + str(loc[0]) + ", longitude " + str(loc[1]))
            
            picoLTE.gps.set_priority(1)
            picoLTE.gps.turn_off()
            return loc
        time.sleep(2)  # 30*2 = 60 seconds timeout for GPS fix. Usually takes 5-25s for me.
    picoLTE.gps.set_priority(1)
    picoLTE.gps.turn_off()
    debug.info("No GPS fix received")
    return [0,0]