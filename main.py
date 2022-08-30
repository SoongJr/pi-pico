import utime
from machine import Pin
import st7789

LCD = st7789.LCD_1inch3()
LCD.fill(LCD.green)
LCD.show()


# show readiness by blinking LED
led = Pin('LED')
led.off()
for n in range(0, 6):
    led.value(not led.value())
    utime.sleep_ms(500)
led.off()
