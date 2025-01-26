TODO: rewrite deployment instructions for pymakr (some stuff moved to boot.py)
create terminal for your device in pymakr_project view
right-click configure-wifi.py, pymakr->run on device
enter credentials in terminal

Remote temperature and humidity sensor using a raspberry pi pico W and one or more DHT22 (AKA AM2302) sensors.  
Data is exposed as prometheus metrics so [my grafana setup](https://github.com/SoongJr/internet-pi) can capture and display it.  

This uses micropython with the builtin dht module and the formadible [phew!](https://pypi.org/project/micropython-phew/) module.

To set up the pi pico, proceed as follows (it's assumed you have your IDE set up, e.g. VS Code with workspace recommendations):
1. wire your pi pico, e.g. using a bread board:
   1. connect the DHT sensor(s) to GPIOs with a 10k resistor, following the [wiring guide](https://learn.adafruit.com/dht/connecting-to-a-dhtxx-sensor) (I'm using GP16 and GP17 because they are close on the board to where I want my sensors to connect, but you are free to choose).  
   2. pull one of your ADCs to VSYS with a 47k resistor if you want to have VSYS monitoring  
   3. also consider attaching an LED (mine is using a 100 Ohm resistor), which will light up during boot and turn off when the pico done and should be reachable.  
   For reference, do take a look at the attached [schematics](images/pico-temp-schematic.png) and [PCB layout](images/pico-temp-pcb.png) for my own board.
2. flash micropython onto your pico (you can get [nightly builds](https://micropython.org/download/rp2-pico-w/))
3. transfer and run configure-wifi.py on the pico, e.g. with  
   `rshell 'cp configure-wifi.py /pyboard; repl ~ exec(open("/configure-wifi.py").read())'` (after which you have to hit Ctrl+X to get out of REPL)  
   This will prompt for credentials and write them into a file on the pico, so there is no chance you'll accidentally upload them to github.
4. run install-dependencies.py on the pico, this uses your wifi to install the phew! module:  
   `rshell 'cp install-dependencies.py /pyboard; repl ~ exec(open("/install-dependencies.py").read())'`
5. open main.py in your IDE. Set values for the `dht_sensors` and `led` variables to use the Pins you chose and give a meaningful value to variable `pico_name`
6. run main.py on the pico:  
   `rshell 'cp main.py /pyboard; repl ~ exec(open("/main.py").read())'` (stop it with Ctrl+C, then exit REPL with Ctrl+X)  
7. test your setup with `curl http://<ip-address>:80/metrics`, you should get metrics for temperature_celsius and humidity_percent in prometheus syntax
8. consider setting your router to give the new device a proper hostname (I have to reboot my router for the change to take effect...)

As this process downloads the main.py directly to the pico, it will run main.py every time it gets power, even when not connected to your PC.  
