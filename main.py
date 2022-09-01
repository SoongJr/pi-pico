from machine import Pin, ADC
import json
import dht
from phew import server, connect_to_wifi

# Pin mappings
sensor = dht.DHT22(Pin(22))
# temperature sensor inside the RP2040 chip
temp_internal = ADC(4)
# system voltage (VSYS) to monitor battery charge
# Normally ADC channel 3 is connected to this internally, but this does not report correct values if WIFI connection is running.
# connecting it to a different channel compares it to VREF, so we have to calculate back from that (and will only notice any difference when VSYS falls below VREF).
vsys = ADC(2)

# factor for converting ADC reading to Volts (VERY roughly, not adjusting for ADC offset or VREF ripple!)
adc_to_volt_factor = 3.3 / (65535)

# read WIFI configuration from file system
wifiConfigFile = '/.wifi/connections.json'
# Opening JSON file
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    # for future compatibility we get a list of connections, though we only use the first one.
    connections = json.load(f)
print(connect_to_wifi(connections[0]['ssid'], connections[0]['password']))

# name of the pico, this will show up in prometheus database
pico_name = "pico-temp-0"
# response template for dht measurements:
response_dht = """# HELP temperature_celsius Room Temperature
# TYPE temperature_celsius gauge
temperature_celsius{{room="%s"}} {temperature:.2f}
# HELP humidity_percent Relative Humidity
# TYPE humidity_percent gauge
humidity_percent{{room="%s"}} {humidity}
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


def get_dht_response():
    # take measurement
    sensor.measure()
    return response_dht.format(temperature=sensor.temperature(),
                               humidity=round(sensor.humidity()))


def get_cpu_temp_response():
    # The internal temperature sensor measures the Vbe voltage of a biased bipolar diode.
    # Typically, Vbe = 0.706V at 27 degrees C, with a slope of -1.721mV (0.001721) per degree.
    reading = 27 - ((temp_internal.read_u16() *
                    adc_to_volt_factor) - 0.706) / 0.001721
    # BUG: as soon as I connect ADC2 or ADC1 to VSYS in order to measure it,
    # the internal temperature is being reported around -80°C. Without the connection, it is around 30°C.
    # Do a sanity check and don't report values outside a reasonable range.
    if reading <= -50 or reading >= 100:
        raise RuntimeError(
            "reading outside sane range: {0:.2f}".format(reading))
    return response_cpu_temp.format(reading)


def get_vsys_response():
    # take a reading and convert to Volts
    reading = vsys.read_u16() * adc_to_volt_factor
    # BUG: as soon as I connect ADC2 or ADC1 to VSYS in order to measure it,
    # the internal temperature is being reported around -80°C. Without the connection, it is around 30°C.
    # There seems to be an internal pull-down resistor of between 47k and 22k so pulling ADC (no matter which one!) to VSYS creates a minor short circuit.
    # Trying to circumvent the issue by using a 47k resistor to pull AC to VSYS,
    # hence reducing the current but also getting a reduced reading due to voltage division.
    # Correcting for this error (and any others, so long as they're linear) with a linear equation (measured at 5V and 3.6V):
    reading = (1.602 * reading) + 1.487
    # Do a sanity check and don't report values outside a reasonable range.
    # if reading <= 1 or reading >= 6:
    #     raise RuntimeError(
    #         "reading outside sane range: {0:.2f}".format(reading))
    return response_VSYS.format(reading)


# set up phew! webserver to expose prometheus endpoint:
@ server.route("/metrics", methods=["GET"])
def metrics(request):
    # gather response from different sensors but continue if any have issues
    response = ""
    try:
        response += get_dht_response()
    except Exception as inst:
        print(type(inst), inst)
        print("Unable to get DHT measurement")
    try:
        response += get_cpu_temp_response()
    except Exception as inst:
        print(type(inst), inst)
        print("Unable to get internal chip temperature")
    try:
        response += get_vsys_response()
    except Exception as inst:
        print(type(inst), inst)
        print("Unable to get system voltage measurement")
    # send REST response
    return response


@ server.catchall()
def catchall(request):
    return "Not found\n", 404


# start server loop
server.run()
