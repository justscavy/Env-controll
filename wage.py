from hx711 import HX711
import RPi.GPIO as GPIO
import time
import sys

def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

hx = HX711(5, 6)

hx.set_reference_unit(1)  # Use set_reference_unit
hx.reset()
hx.tare()

while True:
    try:
        val = hx.get_weight(5)
        print(val)
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
