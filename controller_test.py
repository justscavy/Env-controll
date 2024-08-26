import RPi.GPIO as GPIO
import threading
import schedule
import time as dt
from datetime import datetime, timedelta
from sensor import Sensor, Location, address_box, address_room
import atexit
from shared_state import shared_state
import json

# Initialize GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Main Light 230V
GPIO.setup(24, GPIO.OUT)  # Humidifier 230V
GPIO.setup(25, GPIO.OUT)  # Heatmat 230V
GPIO.setup(17, GPIO.OUT)  # Dehumidifier 230V channel a outlet
GPIO.setup(27, GPIO.OUT)  # Extra exhaust fan 12V
GPIO.setup(22, GPIO.OUT)  # Fan on light 12V
GPIO.setup(26, GPIO.OUT)  # anzucht channel b outlet

# High since we work with a low trigger SSR
def cleanup_gpio():
    GPIO.output(23, GPIO.HIGH)  # low trigger
    GPIO.output(24, GPIO.HIGH)  # low trigger
    GPIO.output(17, GPIO.HIGH)  # low trigger
    GPIO.output(25, GPIO.HIGH)  # low trigger
    GPIO.output(27, GPIO.LOW)   # high trigger
    GPIO.output(22, GPIO.LOW)   # high trigger
    GPIO.output(26, GPIO.HIGH)
    GPIO.cleanup()

# Turn off relays on exit
atexit.register(cleanup_gpio)

gpio_lock = threading.Lock()
room_sensor = Sensor(address=address_room, location=Location.ROOM)
box_sensor = Sensor(address=address_box, location=Location.BOX)

def fan_exhaust2_control(trigger_fanexhaust2):
    GPIO.output(27, GPIO.HIGH if trigger_fanexhaust2 else GPIO.LOW)

def fan_on_light(trigger_fan_on_light):
    GPIO.output(22, GPIO.HIGH if trigger_fan_on_light else GPIO.LOW)

def humidifier_control(trigger_humidifier):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if trigger_humidifier else GPIO.LOW)
    shared_state.humidifier_state = 0 if trigger_humidifier else 1
    print(f"Humidifier {'off' if trigger_humidifier else 'on'}. State: {shared_state.humidifier_state}")

def dehumidifier_control(trigger_dehumidifier):
    with gpio_lock:
        GPIO.output(17, GPIO.HIGH if trigger_dehumidifier else GPIO.LOW)
    if trigger_dehumidifier:
        shared_state.dehumidifier_state = 0
        print(f"dehumidifier is off. {shared_state.dehumidifier_state}")
    else:
        shared_state.dehumidifier_state = 1
        print(f"dehumidifier is on. {shared_state.dehumidifier_state}")

def heatmat_control(trigger_heatmat):
    with gpio_lock:
        GPIO.output(25, GPIO.LOW if trigger_heatmat else GPIO.HIGH)
    shared_state.heatmat_state = 1 if trigger_heatmat else 0
    print(f"Heatmat {'on' if trigger_heatmat else 'off'}. State: {shared_state.heatmat_state}")

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
    turn_on_time = datetime.strptime("20:00:00", "%H:%M:%S").time()
    turn_off_time = datetime.strptime("08:00:00", "%H:%M:%S").time()

    if turn_off_time < now < turn_on_time:
        turn_off_light()
    else:
        turn_on_light()
    schedule.every().day.at("20:00:00").do(turn_on_light)
    schedule.every().day.at("08:00:00").do(turn_off_light)
    while True:
        schedule.run_pending()
        dt.sleep(1)
'''
last_watering_file = 'last_watering.json'

def get_last_watering():
    try:
        with open(last_watering_file, 'r') as file:
            data = json.load(file)
            return datetime.strptime(data['last_watering'], '%Y-%m-%d %H:%M:%S')
    except (FileNotFoundError, KeyError):
        return datetime.now() - timedelta(days=2)

def update_last_watering():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(last_watering_file, 'w') as file:
        json.dump({'last_watering': now}, file)

def run_water_pump(seconds):
    GPIO.output(26, GPIO.HIGH)
    dt.sleep(seconds)
    GPIO.output(26, GPIO.LOW)

def run_watering_cycle():
    now = datetime.now()
    last_watering = get_last_watering()

    if (now - last_watering).days >= 2:
        run_water_pump(10)
        dt.sleep(300)  # Pause for 5 minutes
        run_water_pump(10)
        dt.sleep(300)  # Pause for 5 minutes
        run_water_pump(30)
        update_last_watering()

def watering_schedule():
    schedule.every().day.at("20:15").do(run_watering_cycle)
    while True:
        schedule.run_pending()
        dt.sleep(1)
'''

def debounce_check(condition_func, duration=10, check_interval=1):
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
            if box_vpd > 1.20 and humidifier_on:
                if debounce_check(lambda: box_sensor.get_data().vpd > 1.2): #turn humidifier off
                    print("Turning off humidifier")
                    humidifier_control(False)
                    humidifier_on = False 
            elif box_vpd < 1.10 and not humidifier_on: #turn humidifier on
                print("Turning on humidifier")
                humidifier_control(True)
                humidifier_on = True
           # if box_temp > 24:
           #     if debounce_check(lambda: box_sensor.get_data().temperature > 24):
           #         fan_on_light(True)
           #         fan_on_light_on = True
           #         print("Turning off heatmat")
           #         heatmat_control(False)
           #         heatmat_on = False
           # elif box_temp < 22:
           #     if debounce_check(lambda: box_sensor.get_data().temperature < 22):
           #         fan_on_light(False)
           #         fan_on_light_on = False
           #         print("Turning on heatmat")
           #         heatmat_control(True)
           #         heatmat_on = True
            if box_vpd > 1.20: #turn dehumidifier off
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < 1.10: # turn dehumidifier on
                dehumidifier_control(False)
                dehumidifier_on = False
                
        else:
            if box_vpd < 1.2 and humidifier_on:
                if debounce_check(lambda: box_sensor.get_data().vpd > 1.2):
                    print("Turning off humidifier")
                    humidifier_control(False)
                    humidifier_on = False
            elif box_vpd > 1.1 and not humidifier_on:
                print("Turning on humidifier")
                humidifier_control(True)
                humidifier_on = True
            if box_vpd > 1.20:
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < 1.10:
                dehumidifier_control(False)
                dehumidifier_on = False
            #if room_vpd < 0.90:
            #    fan_exhaust2_on = True
            #    fan_exhaust2_control(True)
            #elif room_vpd > 1.6:
            #    fan_exhaust2_on = False
            #    fan_exhaust2_control(False)

        dt.sleep(1)


