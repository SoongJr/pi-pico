from phew import server, connect_to_wifi
import phew
import upip
import os
import json
import time
import network

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
    print('connected to wifi ' + connections[0]['ssid'])
print()


def list_members(classname):
    print(str(classname) + ' contains: ' +
          ', '.join(i for i in dir(classname) if not i.startswith('_')))


f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
print("free size before install: {}kB".format((f_bfree * f_frsize) / 1024))
print()

# (re)install phew
upip.install("micropython-phew")
# verify it can be imported and list exposed classes
list_members(phew)
list_members(phew.server)
print('phew.server contains: ' +
      ', '.join(i for i in dir(phew.server) if not i.startswith('_')))


print()
f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
print("free size after install: {}kB".format((f_bfree * f_frsize) / 1024))

print()
print('Please note that you also have to upload the content of micropython-nano-gui repo before you can run main.py')
