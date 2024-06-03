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

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)  # Light outlet1 230V
GPIO.setup(24, GPIO.OUT)  # Humidifier
GPIO.setup(17, GPIO.OUT)  # Dehumidifier
#GPIO.setup(18, GPIO.OUT)

gpio_lock = threading.Lock()

def cleanup_gpio():
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    GPIO.output(17, GPIO.LOW)
    #GPIO.output(18, GPIO.LOW)
    GPIO.cleanup()

# Turn off relays on exit
atexit.register(cleanup_gpio)

def humidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on else GPIO.LOW)
   

def humidifier_on_for_duration():
    threading.Thread(target=humidifier_control, args=(True,)).start()
    dt.sleep(5)
    threading.Thread(target=humidifier_control, args=(False,)).start()

def dehumidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(17, GPIO.HIGH if turn_on else GPIO.LOW)


def turn_on_light():
    with gpio_lock:
        GPIO.output(23, GPIO.HIGH)
    shared_state.light_state, shared_state.humidifier_state = 1
    print(f"Light turned on at {datetime.now()} with state {shared_state.light_state, shared_state.humidifier_state}")

def turn_off_light():
    with gpio_lock:
        GPIO.output(23, GPIO.LOW)
    shared_state.light_state, shared_state.humidifier_state = 0
    print(f"Light turned off at {datetime.now()} with state {shared_state.light_state, shared_state.humidifier_state}")

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

# Avoid devices turning on/off frequently
def debounce_check(condition_func, duration=30, check_interval=1):
    start_time = datetime.now()
    while (datetime.now() - start_time).total_seconds() < duration:
        if not condition_func():
            return False
        dt.sleep(check_interval)
    return True

def condition_control():
    humidifier_on = False
    dehumidifier_on = False

    while True:
        sensor_data = generate_sensor_data(shared_state.light_state, shared_state.humidifier_state)
        humidity = sensor_data.humidity
        temperature = sensor_data.temperature

        # Control humidifier(fan bot of tent)
        if humidity < 70 and not humidifier_on:
            if debounce_check(lambda: generate_sensor_data(shared_state.light_state, shared_state.humidifier_state).humidity < 70):
                print("Turning on humidifier for 5 seconds")
                humidifier_on_for_duration()
                humidifier_on = True
                print("Turning off humidifier")
                dt.sleep(5)  # Sleep for 5 seconds to match the humidifier on duration
                humidifier_on = False
        elif humidity >= 75 and humidifier_on:
            print("Turning off humidifier")
            threading.Thread(target=humidifier_control, args=(False,)).start()
            humidifier_on = False

        # Control dehumidifier(fan on bottom of tent)
        if humidity > 80 or temperature > 24 and not dehumidifier_on:
            if debounce_check(lambda: generate_sensor_data(shared_state.light_state, shared_state.humidifier_state).humidity > 80 or generate_sensor_data(shared_state.light_state, shared_state.humidifier_state).temperature > 24):
                print("Turning on dehumidifier...")
                threading.Thread(target=dehumidifier_control, args=(True,)).start()
                dehumidifier_on = True
        elif humidity <= 65 or temperature < 23.5 and dehumidifier_on:
                print("Turning off dehumidifier...")
                threading.Thread(target=dehumidifier_control, args=(False,)).start()
                dehumidifier_on = False

        dt.sleep(1)


