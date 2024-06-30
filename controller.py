import RPi.GPIO as GPIO
import threading
import schedule
import time as dt
from datetime import datetime
from sensor import Sensor, Location, address_box, address_room
import atexit
from shared_state import shared_state

# GPIO 23 - Main Light 230V
# GPIO 24 - Humidifier
# GPIO 17 - Dehumidifier
# GPIO 25 - Heatmat
# GPIO 27 - Extra exhaustfan2 5v inline to exhaustfan1
# GPIO 22 - Fan on light

# Initialize GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Light outlet1 230V
GPIO.setup(24, GPIO.OUT)  # Humidifier
GPIO.setup(25, GPIO.OUT)  # Heatmat
GPIO.setup(17, GPIO.OUT)  # Dehumidifier (Not used right now)
GPIO.setup(27, GPIO.OUT)  # Extra exhaust fan
GPIO.setup(22, GPIO.OUT)  # Fan on light

gpio_lock = threading.Lock()

# High since we work with a low trigger SSR
def cleanup_gpio():
    GPIO.output(23, GPIO.HIGH)  # low trigger
    GPIO.output(24, GPIO.HIGH)  # low trigger
    GPIO.output(17, GPIO.HIGH)  # low trigger
    GPIO.output(25, GPIO.HIGH)  # low trigger
    GPIO.output(27, GPIO.LOW)   # high trigger
    GPIO.output(22, GPIO.LOW)   # high trigger
    GPIO.cleanup()

# Turn off relays on exit
atexit.register(cleanup_gpio)

room_sensor = Sensor(address=address_room, location=Location.ROOM)
box_sensor = Sensor(address=address_box, location=Location.BOX)

def fan_exhaust2_control(turn_on_fanexhaust2):
    GPIO.output(27, GPIO.HIGH if turn_on_fanexhaust2 else GPIO.LOW)

def fan_on_light(turn_on_fan_on_light):
    GPIO.output(22, GPIO.HIGH if turn_on_fan_on_light else GPIO.LOW)

def humidifier_control(turn_on_humidifier):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on_humidifier else GPIO.LOW)
    shared_state.humidifier_state = 0 if turn_on_humidifier else 1
    print(f"Humidifier {'on' if turn_on_humidifier else 'off'}. State: {shared_state.humidifier_state}")


def dehumidifier_control(turn_on_dehumidifier):
    with gpio_lock:
        GPIO.output(17, GPIO.HIGH if turn_on_dehumidifier else GPIO.LOW)
    if turn_on_dehumidifier:
        shared_state.dehumidifier_state = 0
        print(f"dehumidifier is on. {shared_state.dehumidifier_state}")
    else:
        shared_state.dehumidifier_state = 1
        print(f"dehumidifier is off. {shared_state.dehumidifier_state}")


def heatmat_control(turn_on_heatmat):
    with gpio_lock:
        GPIO.output(25, GPIO.LOW if turn_on_heatmat else GPIO.HIGH)
    shared_state.heatmat_state = 1 if turn_on_heatmat else 0
    print(f"Heatmat {'on' if turn_on_heatmat else 'off'}. State: {shared_state.heatmat_state}")

def turn_on_light():
    with gpio_lock:
        GPIO.output(23, GPIO.LOW)
    shared_state.light_state = 1
    print(f"Light turned on at {datetime.now()} with state {shared_state.light_state}")

def turn_off_light():
    with gpio_lock:
        GPIO.output(23, GPIO.HIGH)
    shared_state.light_state = 0
    print(f"Light turned off at {datetime.now()} with state {shared_state.light_state}")

def light_control():
    now = datetime.now().time()
    turn_on_time = datetime.strptime("21:00:00", "%H:%M:%S").time()
    turn_off_time = datetime.strptime("09:00:00", "%H:%M:%S").time()

    # Check light state in case program starts in between times
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()

    schedule.every().day.at("21:00:00").do(turn_on_light)
    schedule.every().day.at("09:00:00").do(turn_off_light)
    while True:
        schedule.run_pending()
        dt.sleep(1)

def debounce_check(condition_func, duration=5, check_interval=1):
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < duration:
        if not condition_func():
            return False
        dt.sleep(check_interval)
    return True

def condition_control():
    humidifier_on = False
    heatmat_on = False
    dehumidifier_on = False
    fan_exhaust2_on = False
    fan_on_light_on = False

    while True:
        room_data = room_sensor.get_data()
        box_data = box_sensor.get_data()
        room_vpd = room_data.vpd
        box_vpd = box_data.vpd
        room_temp = room_data.temperature
        box_temp = box_data.temperature

        with gpio_lock:
            light_state = shared_state.light_state

        if light_state == 1:
            if box_vpd > 1.3 and humidifier_on:
                if debounce_check(lambda: box_sensor.get_data().vpd > 1.3):
                    print("Turning off humidifier")
                    humidifier_control(False)
                    humidifier_on = False
            elif box_vpd < 1.0 and not humidifier_on:
                print("Turning on humidifier")
                humidifier_control(True)
                humidifier_on = True
            if box_temp > 24:
                if debounce_check(lambda: box_sensor.get_data().temperature > 24):
                    fan_on_light(True)
                    fan_on_light_on = True
                    print("Turning off heatmat")
                    heatmat_control(False)
                    heatmat_on = False
            elif box_temp < 22:
                if debounce_check(lambda: box_sensor.get_data().temperature < 22):
                    fan_on_light(False)
                    fan_on_light_on = False
                    print("Turning on heatmat")
                    heatmat_control(True)
                    heatmat_on = True
            if box_vpd > 1.25:
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < 1.15:
                dehumidifier_control(False)
                dehumidifier_on = False
                
        else:
            if box_vpd > 1.25 and humidifier_on:
                if debounce_check(lambda: box_sensor.get_data().vpd > 1.25):
                    print("Turning off humidifier")
                    humidifier_control(False)
                    humidifier_on = False
            elif box_vpd < 1.15 and not humidifier_on:
                print("Turning on humidifier")
                humidifier_control(True)
                humidifier_on = True
            if box_vpd > 1.25:
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < 1.15:
                dehumidifier_control(False)
                dehumidifier_on = False
            #if room_vpd < 0.90:
            #    fan_exhaust2_on = True
            #    fan_exhaust2_control(True)
            #elif room_vpd > 1.6:
            #    fan_exhaust2_on = False
            #    fan_exhaust2_control(False)

        dt.sleep(1)
