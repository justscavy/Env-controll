import RPi.GPIO as GPIO
import threading
import schedule
import time as dt
from datetime import datetime, timedelta
from sensor import Sensor, Location, address_box, address_room
import atexit
from shared_state import shared_state
import json
import os

# Initialize GPIOs
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Main Light 230V
GPIO.setup(24, GPIO.OUT)  # Humidifier 230V
GPIO.setup(25, GPIO.OUT)  # Heatmat 230V
GPIO.setup(26, GPIO.OUT)  # waterpump
GPIO.setup(27, GPIO.OUT)  # Extra exhaust fan 12V
GPIO.setup(22, GPIO.OUT)  # Fan on light 12V
GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH) #Dehumidifier 230V channel a outlet
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #water detection sensor
GPIO.setup(20, GPIO.OUT) #water detection sensor

# High since we work with a low trigger SSR
def cleanup_gpio():
    GPIO.output(23, GPIO.HIGH)  # low trigger
    GPIO.output(24, GPIO.HIGH)  # low trigger
    GPIO.output(26, GPIO.HIGH)  # low trigger
    GPIO.output(25, GPIO.HIGH)  # low trigger
    GPIO.output(27, GPIO.LOW)   # high trigger
    GPIO.output(22, GPIO.LOW)   # high trigger
    GPIO.output(17, GPIO.HIGH)  # low trigger
    GPIO.output(20, GPIO.LOW)   # high trigger
    GPIO.output(21, GPIO.HIGH)   # low trigger
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

def fan_on_light_control_loop():
    while True:
        with gpio_lock:
             fan_on_light(True)
             dt.sleep(60)
             fan_on_light(False)
             dt.sleep(60)

    
def humidifier_control(trigger_humidifier):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if trigger_humidifier else GPIO.LOW)
    shared_state.humidifier_state = 0 if trigger_humidifier else 1

def dehumidifier_control(trigger_dehumidifier):
    with gpio_lock:
        GPIO.output(26, GPIO.HIGH if trigger_dehumidifier else GPIO.LOW)
    if trigger_dehumidifier:
        shared_state.dehumidifier_state = 0
    else:
        shared_state.dehumidifier_state = 1

def heatmat_control(trigger_heatmat):
    with gpio_lock:
        GPIO.output(25, GPIO.LOW if trigger_heatmat else GPIO.HIGH)
    shared_state.heatmat_state = 1 if trigger_heatmat else 0

def turn_on_light():
    with gpio_lock:
        GPIO.output(23, GPIO.LOW)
    shared_state.light_state = 1

def turn_off_light():
    with gpio_lock:
        GPIO.output(23, GPIO.HIGH)
    shared_state.light_state = 0

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


def check_water_drain():
    GPIO.output(20, GPIO.HIGH)
    if GPIO.input(21) == GPIO.HIGH:
        shared_state.water_detected_state = 1
        return True
    else:
        shared_state.water_detected_state = 0
        return False

last_watering_file = '/home/adminbox/Env-controll/config/last_watering.json'

if not os.path.exists(last_watering_file):
    with open(last_watering_file, 'w') as file:
        json.dump({'last_watering': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d 20:30:00')}, file)

def get_last_watering():
    try:
        with open(last_watering_file, 'r') as file:
            data = json.load(file)
            return datetime.strptime(data['last_watering'], '%Y-%m-%d %H:%M:%S')
    except (FileNotFoundError, KeyError, ValueError):
        return datetime.now() - timedelta(days=2)

def update_last_watering():
    now = datetime.now()
    fixed_time = '20:30:00'
    watering_datetime = f"{now.strftime('%Y-%m-%d')} {fixed_time}"
    
    with open(last_watering_file, 'w') as file:
        json.dump({'last_watering': watering_datetime}, file)

def run_water_pump(seconds):
    GPIO.output(17, GPIO.LOW)  # Turn pump on
    shared_state.waterpump_state = 1
    dt.sleep(seconds)
    GPIO.output(17, GPIO.HIGH)  # Turn pump off
    shared_state.waterpump_state = 0


def run_watering_cycle():
    now = datetime.now()
    last_watering = get_last_watering()
    
    # Only water if 2 or more days have passed since the last watering
    if (now - last_watering).days >= 2:
        if shared_state.water_detected_state == 0:
            run_water_pump(15)
            dt.sleep(300)
            
            # Check water detection before running the pump again
            if shared_state.water_detected_state == 0:
                run_water_pump(15)
                dt.sleep(300)
            
            # Check water detection before running the pump again
            if shared_state.water_detected_state == 0:
                run_water_pump(15)
                
            update_last_watering()
        else:
            pass


def check_and_wait_for_next_watering():
    last_watering = get_last_watering()
    next_watering_time = last_watering + timedelta(days=2)
    now = datetime.now()

    if now < next_watering_time:
        time_until_watering = (next_watering_time - now).total_seconds()
        dt.sleep(time_until_watering)

    run_watering_cycle()

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
    #fan_on_light_on = False

    last_humidifier_on_time = datetime.now() - timedelta(minutes=3)
    
    while True:
        water_present = check_water_drain()
        if water_present:
            fan_exhaust2_control(True) 
        else:
            fan_exhaust2_control(False) 

            
        now = datetime.now()
        current_minute = now.minute
        is_even_minute = current_minute % 2 == 0
        box_data = box_sensor.get_data()
        box_vpd = box_data.vpd
        with gpio_lock:
            light_state = shared_state.light_state

        if light_state == 1:
        # Calculate the time difference since the last humidifier activation
            time_since_last_on = now - last_humidifier_on_time

            if time_since_last_on >= timedelta(minutes=2):
                # Turn on the humidifier
                humidifier_control(False)
                humidifier_on = False
                last_humidifier_on_time = now  # Update the last on time

                # Keep the humidifier on for 15 seconds
                dt.sleep(40)

                # Turn off the humidifier
                humidifier_control(True)
                humidifier_on = True
            '''
            if box_vpd > shared_state.max_vpd and humidifier_on: #turn humidifier off
                if debounce_check(lambda: box_sensor.get_data().vpd > shared_state.max_vpd):
                    humidifier_control(False) #should be False
                    humidifier_on = False    #should be False
            elif box_vpd < shared_state.min_vpd and not humidifier_on: #turn humidifier on
                humidifier_control(True)
                humidifier_on = True
'''
    
            if box_vpd > shared_state.max_vpd: #turn dehumidifier on
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < shared_state.min_vpd: #turn dehumidifier off
                dehumidifier_control(False)
                dehumidifier_on = False
                
        else:
            if is_even_minute:
                humidifier_control(True)  # Turn on the humidifier during even minutes
                humidifier_on = True
            else:
                humidifier_control(False)  # Turn off the humidifier during odd minutes
                humidifier_on = False
          
            '''
            if box_vpd > shared_state.max_vpd and humidifier_on:
                if debounce_check(lambda: box_sensor.get_data().vpd > shared_state.max_vpd):
                    humidifier_control(True) #should be False, True for now 
                    humidifier_on = True #should be False
            elif box_vpd < shared_state.min_vpd and not humidifier_on:
                humidifier_control(True)
                humidifier_on = True
'''
            if box_vpd > shared_state.max_vpd:
                dehumidifier_control(True)
                dehumidifier_on = True
            elif box_vpd < shared_state.min_vpd:
                dehumidifier_control(False)
                dehumidifier_on = False

        dt.sleep(1)

