import time
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()

hx = HX711(dout_pin=5, pd_sck_pin=6)

# Reset the hx711
hx.reset()

# Calculate the reference unit based on your specific setup
reference_unit = 97.054222222
hx.set_reference_unit(reference_unit)

hx.tare()
print("Tare done! Add weight now...")

while True:
    try:
        # Read weight
        val = hx.get_weight(5)
        print(val)

        # Power down and up between readings
        hx.power_down()
        hx.power_up()
        time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
