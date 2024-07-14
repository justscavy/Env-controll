import time
import json
import RPi.GPIO as GPIO
from hx711_classes import HX711


def initialize_hx711():
    hx = HX711(5, 6)
    
    # Check if set_reading_format method exists and call it if it does
    if hasattr(hx, 'set_reading_format'):
        hx.set_reading_format("MSB", "MSB")
    
    referenceUnit = 96.354222222
    hx.set_reference_unit(referenceUnit)
    hx.reset()

    tare_file = "tare_values.json"
    try:
        with open(tare_file, "r") as f:
            tare_values = json.load(f)
            hx.set_offset_A(tare_values["offset_A"])
            hx.set_offset_B(tare_values["offset_B"])
            print("Tare values loaded from file")
    except FileNotFoundError:
        print("Tare file not found, performing tare...")
        hx.tare_A()
        hx.tare_B()
        tare_values = {
            "offset_A": hx.get_offset_A(),
            "offset_B": hx.get_offset_B()
        }
        with open(tare_file, "w") as f:
            json.dump(tare_values, f)
        print("Tare done and values saved to file")

    print("Tare done! Add weight now...")
    return hx

def wage(hx):
    val_A = hx.get_weight_A(5) // 1
    val_B = hx.get_weight_B(5) // 24.6
    hx.power_down()
    hx.power_up()
    time.sleep(0.1)
    return val_A, val_B


"""
GPIO.setmode(GPIO.BCM)
    hx = initialize_hx711()

    try:
        while True:
            val_A, val_B = wage(hx)
            print("A: %s  B: %s" % (val_A, val_B))
            time.sleep(1)  # Adjust the sleep time as needed for your measurements
    except KeyboardInterrupt:
        print("Measurement loop terminated.")
    finally:
        GPIO.cleanup()
"""