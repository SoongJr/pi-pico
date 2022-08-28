Remote temperature and humidity sensor using a raspberry pi pico W and a DHT22 sensor (AKA AM2302).  
Data is exposed as prometheus metrics so [my grafana setup](https://github.com/SoongJr/internet-pi) can capture and display it.  

This uses micropython with the builtin dht module and the formadible [phew!](https://pypi.org/project/micropython-phew/) module.

To set up the pi pico, proceed as follows (it's assumed you have your IDE set up):
1. connect the sensor to your pico following the [wiring guide](https://learn.adafruit.com/dht/connecting-to-a-dhtxx-sensor) (I'm using Pin 22 because it's the only one that has no double use, but you are free to choose)
2. flash micropython onto your pico (you can get [nightly builds](https://micropython.org/download/rp2-pico-w/))
3. open configure-wifi.py and enter your WIFI's credentials
4. run configure-wifi.py on the pico, this writes your credentials into a file on the pico. You can remove them from configure-wifi.py now
5. run install-dependencies.py on the pico, this uses your wifi to install the phew! module
6. open main.py and set the `sensor` variable to use the Pin you chose to connect the DHT to
7. run main.py on the pico
8. test your setup with `curl http://<ip-address>:80/metrics`, you should get metrics for temperature_celsius and humidity_percent in prometheus syntax
7. Once everything works as you wish, upload main.py to the pico. This will cause it to run main.py every time it starts up, without the need of connecting an IDE, but prevents you from being able to use your IDE.  
   If you need to modify the program later, try following this [guide on renaming main.py](https://forums.raspberrypi.com/viewtopic.php?f=146&t=305432). There's also the nuke option, which deletes all files as well, meaning you'd have to configure wifi and install dependencies again as well.
