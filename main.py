from machine import Pin
import json
import dht
from phew import server, connect_to_wifi

# set up phew! webserver to expose prometheus endpoint:
sensor = dht.DHT22(Pin(22))


# read WIFI configuration from file system
wifiConfigFile = '/.wifi/connections.json'
# Opening JSON file
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    # for future compatibility we get a list of connections, though we only use the first one.
    connections = json.load(f)
print(connect_to_wifi(connections[0]['ssid'], connections[0]['password']))


@server.route("/metrics", methods=["GET"])
def temperature(request):
    sensor.measure()
    response = """# HELP temperature_celsius Room Temperature
# TYPE temperature_celsius gauge
temperature_celsius{{room="pico"}} {temperature}
# HELP humidity_percent Relative Humidity
# TYPE humidity_percent gauge
humidity_percent{{room="pico"}} {humidity}
"""
    return response.format(temperature=str(sensor.temperature()), humidity=str(sensor.humidity()))


@server.catchall()
def catchall(request):
    return "Not found\n", 404


# start server loop
server.run()
