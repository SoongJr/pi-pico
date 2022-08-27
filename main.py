from machine import Pin
import sys
import json
import time
from phew import server, connect_to_wifi
import dht

# read WIFI configuration from file system
wifiConfigFile = '/.wifi/connections.json'
# Opening JSON file
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    # for future compatibility we get a list of connections, though we only use the first one.
    connections = json.load(f)
connect_to_wifi(connections[0]['ssid'], connections[0]['password'])

# main loop:
led = Pin("LED", Pin.OUT)
sensor = dht.DHT22(Pin(22))
led.off()
while True:
    led.value((led.value()+1) % 2)
    time.sleep(2)
    # take temp and humidity measurement
    sensor.measure()
    print("T: {}, H: {}".format(sensor.temperature(), sensor.humidity()))
