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
# GPIO 25 - Dehumidifier

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Light outlet1 230V
GPIO.setup(24, GPIO.OUT)  # Humidifier
GPIO.setup(25, GPIO.OUT)  # Dehumidifier

gpio_lock = threading.Lock()

def cleanup_gpio():
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    GPIO.output(25, GPIO.LOW)
    GPIO.cleanup()

# turn of relais on exit
atexit.register(cleanup_gpio)


def humidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on else GPIO.LOW)
    if turn_on:
        print("Humidifier is on.")
    else:
        print("Humidifier is off.")

def turn_on_light():
    with gpio_lock:
        GPIO.output(23, GPIO.HIGH)
    shared_state.light_state = 1
    print(f"Light turned on at {datetime.now()} with state {shared_state.light_state}")

def turn_off_light():
    with gpio_lock:
        GPIO.output(23, GPIO.LOW)
    shared_state.light_state = 0
    print(f"Light turned off at {datetime.now()} with state {shared_state.light_state}")


def light_control():
    # Get the current time
    now = datetime.now().time()

    turn_on_time = datetime.strptime("20:00:00", "%H:%M:%S").time()
    turn_off_time = datetime.strptime("14:00:00", "%H:%M:%S").time()

    # Determine the initial state of the light based on the current time
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()

    schedule.every().day.at("20:00:00").do(turn_on_light)
    schedule.every().day.at("14:00:00").do(turn_off_light)

    while True:
        schedule.run_pending()
        dt.sleep(1)
        


#avoid devices turning on/off 
def debounce_check(condition_func, duration=30, check_interval=1):
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < duration:
        if not condition_func():
            return False
        dt.sleep(check_interval)
    return True

def condition_control():
    humidifier_on = False

    while True:
        sensor_data = generate_sensor_data(shared_state.light_state)
        humidity = sensor_data.humidity

        if humidity < 70 and not humidifier_on:
            if debounce_check(lambda: generate_sensor_data(shared_state.light_state).humidity < 65):
                print("Turning on humidifier...")
                threading.Thread(target=humidifier_control, args=(True,)).start()
                humidifier_on = True
        elif humidity >= 75 and humidifier_on:
            if debounce_check(lambda: generate_sensor_data(shared_state.light_state).humidity >= 80):
                print("Turning off humidifier...")
                threading.Thread(target=humidifier_control, args=(False,)).start()
                humidifier_on = False

        dt.sleep(1)