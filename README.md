Remote temperature and humidity sensor using a raspberry pi pico W and a DHT22 sensor (AKA AM2302).  
Data is exposed as prometheus metrics so [my grafana setup](https://github.com/SoongJr/internet-pi) can capture and display it.  

This uses micropython with the builtin dht module and the formadible [phew!](https://pypi.org/project/micropython-phew/) module.

To set up the pi pico, proceed as follows (it's assumed you have your IDE set up):
1. connect the sensor to your pico following the [wiring guide](https://learn.adafruit.com/dht/connecting-to-a-dhtxx-sensor) (I'm using Pin 22 because it's the only one that has no double use, but you are free to choose)
2. flash micropython onto your pico (you can get [nightly builds](https://micropython.org/download/rp2-pico-w/))
3. connect your IDE and run configure-wifi.py on the pico, it will prompt for credentialsand write them into a file on the pico, so there is no chance you'll accidentally upload them ti github.
4. run install-dependencies.py on the pico, this uses your wifi to install the phew! module
5. open main.py and set the `sensor` variable to use the Pin you chose to connect the DHT to
6. run main.py on the pico
7. test your setup with `curl http://<ip-address>:80/metrics`, you should get metrics for temperature_celsius and humidity_percent in prometheus syntax
8. consider setting your router to give the new device a proper hostname (I have to reboot my router for the change to take effect...)
8. Once everything works as you wish, upload main.py to the pico. This will cause it to run main.py every time it starts up, without the need of connecting an IDE.  
   If you need to modify the program later, you can exit out of REPL with Ctrl+D, see also this [guide on renaming main.py](https://forums.raspberrypi.com/viewtopic.php?f=146&t=305432). There's also the nuke option, which deletes all files as well, meaning you'd have to configure wifi and install dependencies again from scratch.
