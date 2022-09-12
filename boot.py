# boot.py -- run on boot-up
from machine import Pin
import json
from phew import connect_to_wifi


# Pin mappings
ledYel = Pin(1, Pin.OUT, value=1)
ledRed = Pin(22, Pin.OUT, value=0)


# read WIFI configuration from file system and connect to it
# for future compatibility we get a list of connections, though we only use the first one.
wifiConfigFile = '/.wifi/connections.json'
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    connections = json.load(f)
print(connect_to_wifi(connections[0]['ssid'], connections[0]['password']))


ledYel.off()  # turn off LED to show we're entering main.py
