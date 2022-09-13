# boot.py -- run on boot-up
import os
from machine import Pin
import json
from phew import connect_to_wifi
from machine import SPI
import sdcard


# Pin mappings
# LEDs
ledYel = Pin(1, Pin.OUT, value=1)
ledRed = Pin(22, Pin.OUT, value=1)
# SPI SD card interface
sd = sdcard.SDCard(SPI(1, baudrate=40000000,
                   sck=Pin(10), mosi=Pin(11), miso=Pin(12)), cs=Pin(13))


ledRed.toggle()  # toggle yellow LED to signal next stage of bootup sequence
# mount sd card so it can be used
# vfs = os.VfsFat(sd)
try:
    os.umount("/sd")
except:
    pass
os.mount(sd, "/sd")


ledRed.toggle()  # toggle yellow LED to signal next stage of bootup sequence
# read WIFI configuration from file system and connect to it
# for future compatibility we get a list of connections, though we only use the first one.
wifiConfigFile = '/.wifi/connections.json'
with open(wifiConfigFile, 'r', encoding='utf-8') as f:
    connections = json.load(f)
print(connect_to_wifi(connections[0]['ssid'], connections[0]['password']))


ledYel.off()  # turn off both LEDs to show we're entering main.py
ledRed.off()
