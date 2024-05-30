import RPi.GPIO as GPIO
import threading
import schedule
import time as dt
from datetime import datetime, timedelta
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

# Cleanup GPIO on program exit
atexit.register(cleanup_gpio)

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

    # Define the scheduled times
    turn_on_time = datetime.strptime("20:00:00", "%H:%M:%S").time()
    turn_off_time = datetime.strptime("14:00:00", "%H:%M:%S").time()

    # Determine the initial state of the light based on the current time
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()

    # Schedule the tasks to turn the light on and off
    schedule.every().day.at("20:00:00").do(turn_on_light)
    schedule.every().day.at("14:00:00").do(turn_off_light)

    while True:
        schedule.run_pending()
        dt.sleep(1)



def condition_control():
    humidifier_on = False

    while True:
        sensor_data = generate_sensor_data(shared_state.light_state)
        humidity = sensor_data.humidity

        if humidity < 65 and not humidifier_on:
            print("Turning on humidifier...")
            threading.Thread(target=humidifier_control, args=(True,)).start()
            humidifier_on = True
        elif humidity >= 80 and humidifier_on:
            print("Turning off humidifier...")
            threading.Thread(target=humidifier_control, args=(False,)).start()
            humidifier_on = False

        dt.sleep(1)

def humidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on else GPIO.LOW)
    if turn_on:
        print("Humidifier is on.")
    else:
        print("Humidifier is off.")

