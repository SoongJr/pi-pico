from machine import Pin
import utime
import sys
import json
import time
import network
import urequests as requests
import dht

# read WIFI configuration from file system
wifiConfigFile = '/.wifi/connections.json'
# Opening JSON file
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    # for future compatibility we get a list of connections, though we only use the first one.
    connections = json.load(f)
# print(json.dumps(connections))
# for key, value in connections[0].items():
#     print (key, value)
# for conn in connections:
#     print(json.dumps(conn))
#     for key, value in conn.items():
#         print("{} : {}".format(key, value))
# sys.exit()
ssid = connections[0]['ssid']
password = connections[0]['password']

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])

led = Pin("LED", Pin.OUT)
sensor = dht.DHT22(Pin(22))
led.off()
while True:
    led.value((led.value()+1) % 2)
    utime.sleep(2)
    # take temp and humidity measurement
    sensor.measure()
    print("T: {}, H: {}".format(sensor.temperature(), sensor.humidity()))
