import upip
import os
import json
import time
import network

f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
print("free size before install: {}kB".format((f_bfree * f_frsize) / 1024))

# read WIFI configuration from file system
with open('/.wifi/connections.json', 'r', encoding='utf-8') as f:
    connections = json.load(f)
# connect
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(connections[0]['ssid'], connections[0]['password'])
# Wait for connect or fail
while True:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    print('waiting for connection...')
    time.sleep(1)
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')


try:
    upip.install("micropython-phew")
finally:
    f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
    print("free size after install: {}kB".format((f_bfree * f_frsize) / 1024))
