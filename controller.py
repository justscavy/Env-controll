import RPi.GPIO as GPIO
import threading
import schedule
import time as dt
from datetime import datetime
from sensor import generate_sensor_data
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
GPIO.setup(23, GPIO.OUT)  # Light outlet1 230V (in test phase since we only interupt phase (searching for 2pol interupter))
GPIO.setup(24, GPIO.OUT)  # Humidifier
GPIO.setup(25, GPIO.OUT)  # TODO: Heatmat for now (should get heat from lamp) (probably wrong flag set from humidifier)
GPIO.setup(17, GPIO.OUT)  # Dehumidifier Not used right now
GPIO.setup(27, GPIO.OUT)  # TODO: track state
GPIO.setup(22, GPIO.OUT)  # TODO: track state


gpio_lock = threading.Lock()

#High since we work with an low trigger ssr
def cleanup_gpio():
    GPIO.output(23, GPIO.HIGH) #low trigger
    GPIO.output(24, GPIO.HIGH) #low trigger
    GPIO.output(17, GPIO.HIGH) #low trigger
    GPIO.output(25, GPIO.HIGH) #low trigger
    GPIO.output(27, GPIO.LOW)  #high trigger
    GPIO.output(22, GPIO.LOW) #high trigger
    GPIO.cleanup()

# Turn off relays on exit
atexit.register(cleanup_gpio)

def fan_exhaust2_control(turn_on_fanexhaust2):
    GPIO.output(27, GPIO.HIGH if turn_on_fanexhaust2 else GPIO.LOW)
    #if turn_on_fanexhaust2:
    #    shared_state.fanexhaust2_state = 0
    #else:
    #    shared_state.fanexhaust2_state = 1

def fan_on_light(turn_on_fan_on_light):
    GPIO.output(22, GPIO.HIGH if turn_on_fan_on_light else GPIO.LOW)

def humidifier_control(turn_on_humidifier):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on_humidifier else GPIO.LOW)
    if turn_on_humidifier:
        shared_state.humidifier_state = 0
        print(f"Humidifier is on. {shared_state.humidifier_state}")
    else:
        shared_state.humidifier_state = 1
        print(f"Humidifier is off. {shared_state.humidifier_state}")


def heatmat_control(turn_on_heatmat):
    with gpio_lock:
        GPIO.output(25, GPIO.LOW if turn_on_heatmat else GPIO.HIGH)
    if turn_on_heatmat:
        shared_state.heatmat_state = 1
        print(f"Heatmat is on. {shared_state.heatmat_state}")
    else:
        shared_state.heatmat_state = 0
        print(f"Heatmat is off. {shared_state.heatmat_state}")


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

    #check lightstate in case program starts in between times
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()
    schedule.every().day.at("21:00:00").do(turn_on_light)
    schedule.every().day.at("09:00:00").do(turn_off_light)
    while True:
        schedule.run_pending()
        dt.sleep(1)
'''
def light_control_flower():
    now = datetime.now().time()
    turn_on_time = datetime.strptime("21:00:00", "%H:%M:%S").time()
    turn_off_time = datetime.strptime("09:00:00", "%H:%M:%S").time()

    #check lightstate in case program starts in between times
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()
    schedule.every().day.at("21:00:00").do(turn_on_light)
    schedule.every().day.at("09:00:00").do(turn_off_light)
    while True:
        schedule.run_pending()
        dt.sleep(1)
'''

def debounce_check(condition_func, duration=5, check_interval=1):
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < duration:
        if not condition_func():
            return False
        dt.sleep(check_interval)
    return True

#control for seedling - early veg
"""
def condition_control():
    humidifier_on = False
    heatmat_on = False
    fan_exhaust2_on = False
    fan_on_light_on = False

    while True:
        sensor_data = generate_sensor_data()
        vpd = sensor_data.vpd
        temperature = sensor_data.temperature
        with gpio_lock:
            light_state = shared_state.light_state
        # we gotta set flags to opposite since we use low trigger SSRs now

        # LIGHT STATE ON
        if light_state == 1:
            if vpd > 0.85 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 0.90):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                    
            elif vpd < 0.75 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            #if vpd < 0.70:
            #    fan_exhaust2_on = True #fan on
            #    fan_exhaust2_control(True)
#
            #elif vpd > 0.80:
            #    fan_exhaust2_on = False  
            #    fan_exhaust2_control(False)
                    
            if temperature > 24:
                if debounce_check(lambda: generate_sensor_data().temperature > 24):
                    fan_on_light(True)
                    fan_on_light_on = True
                    print("Turning on heatmat")
                    heatmat_control(False) #TODO:
                    heatmat_on = False
            elif temperature < 22:
                if debounce_check(lambda: generate_sensor_data().temperature < 22):
                    fan_on_light(False)
                    fan_on_light_on = False
                    print("Turning off heatmat")
                    heatmat_control(True)
                    heatmat_on = True

        # LIGHT STATE OFF
        else:
            if vpd > 0.85 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 0.85):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                
            elif vpd < 0.75 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            if vpd < 0.70:
                fan_exhaust2_on = True #fan on
                fan_exhaust2_control(True)

            elif vpd > 0.80:
                fan_exhaust2_on = False  
                fan_exhaust2_control(False)
            #if temperature > 24:
            #    if debounce_check(lambda: generate_sensor_data().temperature > 24):
            #        print("Turning on heatmat")
            #        heatmat_control(False) #TODO:
            #        heatmat_on = False
            #elif temperature < 22:
            #    if debounce_check(lambda: generate_sensor_data().temperature < 22):
            #        print("Turning off heatmat")
            #        heatmat_control(True)
            #        heatmat_on = True
        dt.sleep(1)
        """

'''
#control for early veg - mid veg
def condition_control():
    humidifier_on = False
    heatmat_on = False
    fan_exhaust2_on = False
    fan_on_light_on = False

    while True:
        sensor_data = generate_sensor_data()
        vpd = sensor_data.vpd
        temperature = sensor_data.temperature
        with gpio_lock:
            light_state = shared_state.light_state
        # we gotta set flags to opposite since we use low trigger SSRs now

        # LIGHT STATE ON
        if light_state == 1:
            if vpd > 0.90 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 0.90):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                    
            elif vpd < 0.85 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            #if vpd < 0.80:
            #    fan_exhaust2_on = True #fan on
            #    fan_exhaust2_control(True)
#
            #elif vpd > 0.85:
            #    fan_exhaust2_on = False  
            #    fan_exhaust2_control(False)
                    
            if temperature > 24:
                if debounce_check(lambda: generate_sensor_data().temperature > 24):
                    fan_on_light(True)
                    fan_on_light_on = True
                    print("Turning on heatmat")
                    heatmat_control(False) #TODO:
                    heatmat_on = False
            elif temperature < 22:
                if debounce_check(lambda: generate_sensor_data().temperature < 22):
                    fan_on_light(False)
                    fan_on_light_on = False
                    print("Turning off heatmat")
                    heatmat_control(True)
                    heatmat_on = True

        # LIGHT STATE OFF
        else:
            if vpd > 0.90 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 0.90):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                
            elif vpd < 0.85 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            if vpd < 0.80:
                fan_exhaust2_on = True #fan on
                fan_exhaust2_control(True)

            elif vpd > 0.85:
                fan_exhaust2_on = False  
                fan_exhaust2_control(False)
            #if temperature > 24:
            #    if debounce_check(lambda: generate_sensor_data().temperature > 24):
            #        print("Turning on heatmat")
            #        heatmat_control(False) #TODO:
            #        heatmat_on = False
            #elif temperature < 22:
            #    if debounce_check(lambda: generate_sensor_data().temperature < 22):
            #        print("Turning off heatmat")
            #        heatmat_control(True)
            #        heatmat_on = True
        dt.sleep(1)
'''

#early flower 0.8-1.2
def condition_control():
    humidifier_on = False
    heatmat_on = False
    fan_exhaust2_on = False
    fan_on_light_on = False

    while True:
        sensor_data = generate_sensor_data()
        vpd = sensor_data.vpd
        temperature = sensor_data.temperature
        with gpio_lock:
            light_state = shared_state.light_state
        # we gotta set flags to opposite since we use low trigger SSRs now

        # LIGHT STATE ON
        if light_state == 1:
            if vpd > 1.3 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 1.3):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                    
            elif vpd < 1.0 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            #if vpd < 0.90:
            #    fan_exhaust2_on = True #fan on
            #    fan_exhaust2_control(True)
#
            #elif vpd > 1.6:
            #    fan_exhaust2_on = False  
            #    fan_exhaust2_control(False)
                    
            if temperature > 24:
                if debounce_check(lambda: generate_sensor_data().temperature > 24):
                    fan_on_light(True)
                    fan_on_light_on = True
                    print("Turning on heatmat")
                    heatmat_control(False) #TODO:
                    heatmat_on = False
            elif temperature < 22:
                if debounce_check(lambda: generate_sensor_data().temperature < 22):
                    fan_on_light(False)
                    fan_on_light_on = False
                    print("Turning off heatmat")
                    heatmat_control(True)
                    heatmat_on = True

        # LIGHT STATE OFF
        else:
            if vpd > 1.3 and humidifier_on:
                if debounce_check(lambda: generate_sensor_data().vpd > 1.3):
                    print("Turning on humidifier")
                    humidifier_control(False)
                    humidifier_on = False
                
            elif vpd < 1.0 and not humidifier_on:
                print("Turning off humidifier")
                humidifier_control(True) #humid off
                humidifier_on = True
                #if debounce_check(lambda: generate_sensor_data().vpd < 0.75):
            if vpd < 0.90:
                fan_exhaust2_on = True #fan on
                fan_exhaust2_control(True)

            elif vpd > 1.6:
                fan_exhaust2_on = False  
                fan_exhaust2_control(False)
            #if temperature > 24:
            #    if debounce_check(lambda: generate_sensor_data().temperature > 24):
            #        print("Turning on heatmat")
            #        heatmat_control(False) #TODO:
            #        heatmat_on = False
            #elif temperature < 22:
            #    if debounce_check(lambda: generate_sensor_data().temperature < 22):
            #        print("Turning off heatmat")
            #        heatmat_control(True)
            #        heatmat_on = True
        dt.sleep(1)