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
          ', '.join(i for i in sorted(dir(classname)) if not i.startswith('_')))


f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
print("free size before install: {}kB".format((f_bfree * f_frsize) / 1024))
print()


def verify_phew():
    # verify it can be imported and list exposed classes
    import phew
    from phew import server, connect_to_wifi
    list_members(phew)
    list_members(phew.server)


# (re)install phew, then verify it can be loaded
upip.install("micropython-phew")
verify_phew()


print()
f_frsize, f_bfree = (os.statvfs('/')[1], os.statvfs('/')[3])
print("free size after install: {}kB".format((f_bfree * f_frsize) / 1024))
