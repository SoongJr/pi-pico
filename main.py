# expose DHT sensor data (temp and humidity) via a webserver in prometheus syntax.
# last measurement of power consumption was 30mA in standby, 60mA while processing REST request, giving us about 4 days on a 5000mAh power bank.

# TODOs:
# - try lowering frequency and/or use power-saving mode, does WIFI still work?
# - other power-saving attempts, like running WIFI only until the first request comes in, then disabling it (or going to sleep) for 2 minutes.
#       Does this even reduce power consumtion? Looks like bootup is using quite a bit of power, not sure that's because of establishing wifi connection...
# - add audio module and raise alarm if there's a problem
#       (e.g. Temp outside desired range (either environment temp or CPU temp), file system over 90%)

import os
import dht
from machine import Pin, ADC
import json
from phew import server, connect_to_wifi, logging
import uasyncio

# name of the pico, this will show up in prometheus database
pico_name = "pico-temp-0"
# Pin mappings
ledRed = Pin(22, Pin.OUT, value=0)
dht_sensors = [  # the names need to be unique in your network, so we prefix generic names with the pico_name. Feel free to omit that when you change it to "bedroom cupboard" or whatever.
    dict(name="bedroom", pin=dht.DHT22(Pin(16))),
    dict(name="southside", pin=dht.DHT22(Pin(17))),
]
# system voltage (VSYS) to monitor battery charge
# Normally ADC channel 3 is connected to this internally, but this does not report correct values if WIFI connection is running.
# connecting it to a different channel compares it to VREF, so we have to calculate back from that (and will only notice any difference when VSYS falls below VREF).
vsys = ADC(2)

# temperature sensor inside the RP2040 chip (this cannot be modified)
temp_internal = ADC(4)
# factor for converting ADC reading to Volts (VERY roughly, not adjusting for ADC offset or VREF ripple!)
adc_to_volt_factor = 3.3 / (65535)

# response template for dht measurements:
response_dht = """# HELP temperature_celsius Room Temperature
# TYPE temperature_celsius gauge
temperature_celsius{{host="%s", room="{room}"}} {temperature:.2f}
# HELP humidity_percent Relative Humidity
# TYPE humidity_percent gauge
humidity_percent{{host="%s", room="{room}"}} {humidity}
""" % (pico_name, pico_name)
# response template for internal temperature measurement:
response_cpu_temp = """# HELP cpu_temperature On-Chip Temperature of the pico
# TYPE cpu_temperature gauge
cpu_temperature{{host="%s"}} {0:.2f}
""" % pico_name
# response template for system voltage:
response_VSYS = """# HELP system_voltage System Voltage provided by power supply
# TYPE system_voltage gauge
system_voltage{{host="%s"}} {0:.2f}
""" % pico_name
# response template for flash statistics:
response_flash = """# HELP flash_total total flash in system in Byte
# TYPE flash_total gauge
flash_total{{host="%s"}} {total}
# HELP flash_used used flash in system in Byte
# TYPE flash_used gauge
flash_used{{host="%s"}} {used}
# HELP flash_used_percent used flash in system in percent
# TYPE flash_used_percent gauge
flash_used_percent{{host="%s"}} {used_percent:.1f}
""" % (pico_name, pico_name, pico_name)


def get_dht_response(sensor):
    # take measurement
    sensor['pin'].measure()
    return response_dht.format(room=sensor['name'],
                               temperature=sensor['pin'].temperature(),
                               humidity=round(sensor['pin'].humidity()))


def get_cpu_temp_response():
    # The internal temperature sensor measures the Vbe voltage of a biased bipolar diode.
    # Typically, Vbe = 0.706V at 27 degrees C, with a slope of -1.721mV (0.001721) per degree.
    reading = 27 - ((temp_internal.read_u16() *
                    adc_to_volt_factor) - 0.706) / 0.001721
    return response_cpu_temp.format(reading)


def get_vsys_response():
    # take a reading and convert to Volts
    reading = vsys.read_u16() * adc_to_volt_factor
    # VSYS must be connected to ADC via a resistor or it will leak a lot of power.
    # using 47k Ohm to oppose the internal resistance (which is somewhere around 33k)
    # and compensating for the reduced voltage with a linear equation (measured at 4.9V and 3.6V:
    reading = (1.602 * reading) + 1.487
    return response_VSYS.format(reading)


def get_flash_response():
    statvfs = os.statvfs('/')
    f_frsize, f_blocks, f_bfree = (statvfs[1], statvfs[2], statvfs[3])
    total = (f_blocks * f_frsize)
    used = total-(f_bfree * f_frsize)
    used_percent = used * 100 / total
    return response_flash.format(total=total, used=used, used_percent=used_percent)


# set up phew! webserver to expose prometheus endpoint:
@ server.route("/metrics", methods=["GET"])
def metrics(request):
    ledRed.off()  # reset error LED

    try:
        # truncate logs on every request, workaround until phew 0.0.3 is released to pypi
        logging.truncate(8*1024)
    except:
        pass

    # gather response from different sensors but continue if any have issues
    response = ""

    for sensor in dht_sensors:
        try:
            response += get_dht_response(sensor)
        except Exception as inst:
            ledRed.on()  # something went wrong, turn on the error LED
            print(type(inst), inst)
            print("Unable to get {} measurement".format(sensor['name']))

    try:
        response += get_cpu_temp_response()
    except Exception as inst:
        ledRed.on()  # something went wrong, turn on the error LED
        print(type(inst), inst)
        print("Unable to get internal chip temperature")

    try:
        response += get_vsys_response()
    except Exception as inst:
        ledRed.on()  # something went wrong, turn on the error LED
        print(type(inst), inst)
        print("Unable to get system voltage measurement")

    try:
        response += get_flash_response()
    except Exception as inst:
        ledRed.on()  # something went wrong, turn on the error LED
        print(type(inst), inst)
        print("Unable to get flash statistics")

    # send REST response
    return response


# simple REST API endpoint to return a single temperature-humidity tuple. Takes "room" as input parameter.
@ server.route("/dht", methods=["GET"])
def dht_reading(request):
    ledRed.off()  # reset error LED

    # gather data and send REST response
    room = request.query.get("room", None)
    if not room:
        return "Missing mandatory parameter: room\n", 400

    # extract sensor with given room name:
    try:
        sensor = next((i for i in dht_sensors if i["name"] == room))
    except StopIteration:
        ledRed.on()  # something went wrong, turn on the error LED
        return "No sensor in room '{}'\n".format(room), 400

    try:
        # take measurement of requested room
        sensor['pin'].measure()
        return json.dumps({
            'temperature': sensor['pin'].temperature(),
            'humidity': sensor['pin'].humidity()
        })
    except Exception as inst:
        ledRed.on()  # something went wrong, turn on the error LED
        print(type(inst), inst)
        print("Unable to get {} measurement".format(room))
        return "Failed procuring data for '{}'\n".format(room), 500


@ server.catchall()
def catchall(request):
    return "Not found\n", 404


# reset the event loop (hoping this helps with soft-reboots)
loop = uasyncio.new_event_loop()


# start server loop
server.run()
# This runs the asyncio event loop and does not normally return.
# Any desired tasks have to have been added to the loop (with asyncio.create_task) before this point.

# we left the loop, something went wrong...
logging.info("Error: event loop stopped.")
ledRed.on()
