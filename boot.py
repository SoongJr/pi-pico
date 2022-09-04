# boot.py -- run on boot-up
import os
import dht
from machine import Pin, ADC
import json
from phew import server, connect_to_wifi, logging


# Pin mappings
led = Pin("LED", Pin.OUT, value=1)


# read WIFI configuration from file system and connect to it
# for future compatibility we get a list of connections, though we only use the first one.
wifiConfigFile = '/.wifi/connections.json'
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    connections = json.load(f)
print(connect_to_wifi(connections[0]['ssid'], connections[0]['password']))


led.off()  # turn off LED to show we're entering main.py
