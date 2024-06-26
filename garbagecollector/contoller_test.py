# controller.py
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

gpio_lock = threading.Lock()

def cleanup_gpio():
    GPIO.output(23, GPIO.LOW)
    GPIO.output(24, GPIO.LOW)
    GPIO.output(17, GPIO.LOW)
    GPIO.cleanup()

# Turn off relays on exit
atexit.register(cleanup_gpio)

def humidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(24, GPIO.HIGH if turn_on else GPIO.LOW)
    if turn_on:
        shared_state.humidifier_state = 1
        print(f"Humidifier is on. {shared_state.humidifier_state}")
    else:
        shared_state.humidifier_state = 0
        print(f"Humidifier is off. {shared_state.humidifier_state}")

def humidifier_on_for_duration():
    threading.Thread(target=humidifier_control, args=(True,)).start()
    dt.sleep(5)
    threading.Thread(target=humidifier_control, args=(False,)).start()

def dehumidifier_control(turn_on):
    with gpio_lock:
        GPIO.output(17, GPIO.HIGH if turn_on else GPIO.LOW)
    if turn_on:
        print("Dehumidifier is on.")
    else:
        print("Dehumidifier is off.")

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

    #check lightstate in case program starts in between times
    if now < turn_on_time and now > turn_off_time:
        turn_off_light()
    else:
        turn_on_light()
    schedule.every().day.at("20:00:00").do(turn_on_light)
    schedule.every().day.at("14:00:00").do(turn_off_light)
    while True:
        schedule.run_pending()
        dt.sleep(1)


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
        sensor_data = generate_sensor_data()
        humidity = sensor_data.humidity
        temperature = sensor_data.temperature
        # Control humidifier(fan bot of tent)
        if humidity < 72 and not humidifier_on:
            if debounce_check(lambda: generate_sensor_data().humidity < 72):
                print("Turning on humidifier for 5 seconds")
                threading.Thread(target=humidifier_control, args=(True,)).start()
                humidifier_on = True
                print("Turning off humidifier")
        elif humidity >= 80 and humidifier_on:
            print("Turning off humidifier")
            threading.Thread(target=humidifier_control, args=(False,)).start()
            humidifier_on = False

        # Control dehumidifier(fan on bottom of tent)
        if (humidity > 82 or temperature > 24) and not dehumidifier_on:
            if debounce_check(lambda: generate_sensor_data().humidity > 82 or generate_sensor_data().temperature > 24):
                print("Turning on dehumidifier(fan)")
                threading.Thread(target=dehumidifier_control, args=(True,)).start()
                dehumidifier_on = True
        elif (humidity <= 75 or temperature < 23.5) and dehumidifier_on:
            print("Turning off dehumidifier(fan)")
            threading.Thread(target=dehumidifier_control, args=(False,)).start()
            dehumidifier_on = False

        dt.sleep(1)
