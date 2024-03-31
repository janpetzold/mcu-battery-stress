# Battery Stress test to Raspberry Pico
This is a project to benchmark Raspberry Pico with LTE connectivity in a basic IoT scenario to find out max. runtime when powered by battery. I did not find any tangible numbers on this so I decided to do my own testing here.

## Purpose
Find out how long a Raspberry Pico can be powered by a basic battery when it reads & sends some sensor data in periodic intervals. 

The sensor data that is transmitted is basically this JSON:

    {
        "i": ID of the device, 
        "t": Timestamp of the device, 
        "c": Temperature read out by Pico, 
        "la": Current GPS latitude, 
        "lo": Current GPS longitude,
        "e": Elapsed runtime of the script,
        "n": Network connection type (LTE or WiFi)
    }

The idea is that the device sends these values once every 20 minutes before sleeping & starting the cycle again (by rebooting).

## Building blocks
These are the HW+SW components used here:

1. [Sixfab Pico LTE with GPS antenna](https://sixfab.com/product/sixfab-pico-lte/): RP2040-based board with LTE modem (Quectel BG95-M3) and antenna onboard that also includes data volume at reasonable price 
2. [Powerboost 1000C Charger](https://www.adafruit.com/product/2465): Enables running the board via battery and also charge it while its running
3. [LiPo battery with 2500 mAh and 3.7V](https://www.adafruit.com/product/328): Typical battery that is reasonably priced (~$15), fits into a case and should be able to power the RP2040 for a few days
4. [Micropython](https://micropython.org/download/?mcu=rp2040): Easy to learn & build, definitely not  the most efficient language in the world but all tasks needed for this project can be built rather easily compared to C.
5. [Azure IoT Hub](https://azure.microsoft.com/en-us/products/iot-hub): MQTT endpoint in the Cloud that I used primarily because I'm comfortable with Azure. Provides a free tier with max. 8000 messages/day which is more than enough. Other options like [MQTTHQ](https://mqtthq.com/) may be simpler and also worked for me.
6. [Azure Blob Storage](https://azure.microsoft.com/en-us/products/storage/blobs): Simple way to store uploaded data reliably for all kinds of further processing. I simply stored each message from the device as a JSON file. The way the [Azure samples from Pico LTE SDK](https://docs.sixfab.com/docs/sixfab-pico-lte-micropython-sdk) work is that they update the Device Twin in IoT Hub each time so a dedicated route had to be set up to actually store the data/see changes somewhere. See https://stackoverflow.com/a/47893851/675454.

## Setup
Setup mainly follows the instructions given here:

https://docs.sixfab.com/docs/sixfab-pico-lte-getting-started
https://docs.sixfab.com/docs/pico-lte-azure-iot-hub-connection

Beside that you need to install

    umqtt.simple

via Thonny.

So essentially everything below the `/python` directory is what I had on my device. Of course your certificates will vary since you'll use your own IoT broker, the `/cert/user_key.pem` must be added anyway for the actual private key of the client.

My device had the issue that it was never able to connect to the MNO via LTE initially. I had to nuke the flash file once, afterwards connecting worked rather quickly and remained stable ever since:

https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html#resetting-flash-memory

## WiFi
As fallback in case of missing LTE connectivity a WiFi-based solution was built, see the `emqx` subdirectory. This uses the public broker from https://www.emqx.com/en/mqtt/public-mqtt5-broker.

For subscribing a simple Python script `subscriber.py` was added that stores all received messages in an Azure Blob Storage. This script should run as systemd service, see its definition there as well. To set it up (also for reboot):

    sudo systemctl enable mqtt_subscriber.service
    sudo systemctl start mqtt_subscriber.service

Get the logs

    sudo journalctl -u mqtt_subscriber.service -f

## Results
So in theory that should be the consumption based on the numbers I found in the [datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf / https://docs.sixfab.com/docs/sixfab-pico-lte-technical-details):

Raspberry Pico "normal": 25mA (so in theory using a 2500mAh battery the Pico should operate for 100 hours unoptimized)
Raspberry Pico "Sleep": 0.39mA
Raspberry Pico "Dormant": 0.18mA
Sixfab Pico LTE "max": 1.5A

Some other numbers of similar boards I found [here](https://www.crowdsupply.com/dptechnics/walter)

| Board      | Chip | Deep Sleep power consumption 
| -----------| ---- | -----------
| [Raspberry Pico](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) | RP2040 | 0.18mA
| [Sixfab Pico LTE](https://sixfab.com/product/sixfab-pico-lte) | RP2040 | TODO  
| [iLabs RP2040 Connectivity](https://ilabs.se/product/the-rp2040-connectivity-board/) | RP2040 | 0.26mA  
| [Walter](https://www.crowdsupply.com/dptechnics/walter) | ESP32 | 0.009mA
| [Pycom GPy](https://docs.pycom.io/datasheets/development/gpy/) | ESP32 | 0.017mA
| [AVR IoT Mini](https://www.microchip.com/en-us/development-tool/ev70n78a) | ESP32 | 0.07mA

The impact of WiFi on/off and modem on/off was TODO.

Beside that find the major findings here:

- Modem and GPS are not really reliable despite having dedicated antennas, sometimes reading GPS / getting LTE connection is a matter of seconds, sometimes it does not work after minutes. This was better when outside.
- lightsleep/deepsleep did not really work out of the box on the Sixfab Pico, the power consumption was around TODO but the system woke up rather randomly but not in the defined interval of 20 minutes. I got lightsleep to work be specifically shutting down WiFi and modem, modem I explicitly powered down via `AT+QPOWD=0` 
- Deepsleep did not work with a time expiration (as expected - wake-up from deepsleep usually only works via external signal)

As a baseline see this power consumption numbers I measured with my own hardware

| Scenario      | Raspberry Pi 4 | Raspberry Zero 2 WH | Sixfab Pico LTE
| ----------- | ----------- | ---- | --------
| Idle | TODO Ah | TODO Ah | TODO Ah |
| Endless loop to stress CPU (`yes > /dev/null &`) | TODO Ah | TODO Ah | TODO Ah |

Data consumption/week for one message every approx. 20 minutes (resulting in ~2150 status messages/week): TODO MB

Maximum runtime: 94 hours

| Device | Scenario      | Runtime | # of messages received | Message drop | Data consumption
| ------ | ----------- | ----------- | ---- | --- | --------
| Pico W | No Power saving | TODO | TODO | TODO | TODO |
| Pico W | Lightsleep WiFi | TODO | TODO | - | TODO |
| Pico W | Dormant WiFi | TODO | TODO | - | TODO |
| Sixfab Pico | No Power saving | ~1760 minutes = 30h | 82 | ? | 181kB* |
| Sixfab Pico | Lightsleep WiFi | ~960min = 14h | 51 | ? | - |
| Sixfab Pico | Lightsleep LTE | ~5667min = 94h | 265 | 0 | 135kB* |
| Sixfab Pico | Dormant LTE | TODO | TODO | TODO | TODO |

* based on SIM statistics in Sixfab portal
