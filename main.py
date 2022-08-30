from machine import Pin
import utime

# show readiness by blinking LED
led = Pin('LED')
led.off()
for n in range(0, 6):
    led.value(not led.value())
    utime.sleep_ms(500)
led.off()
