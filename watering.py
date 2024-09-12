'''
import RPi.GPIO as GPIO
import time
import json
import os
from datetime import datetime, timedelta
from shared_state import shared_state


GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT, initial=GPIO.HIGH)
GPIO.output(26, GPIO.HIGH)  


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
    GPIO.output(26, GPIO.LOW)  # Turn pump on
    shared_state.waterpump_state = 1
    time.sleep(seconds)
    GPIO.output(26, GPIO.HIGH)  # Turn pump off
    shared_state.waterpump_state = 0


def run_watering_cycle():
    now = datetime.now()
    last_watering = get_last_watering()
    
    # Only water if 2 or more days have passed since the last watering
    if (now - last_watering).days >= 2:
        if shared_state.water_detected_state == 0:
            run_water_pump(10)
            time.sleep(5)
            
            # Check water detection before running the pump again
            if shared_state.water_detected_state == 0:
                run_water_pump(10)
                time.sleep(5)
            
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
        time.sleep(time_until_watering)

    run_watering_cycle()
    '''