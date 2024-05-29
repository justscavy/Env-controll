import RPi.GPIO as GPIO
import threading
import time as dt
from datetime import datetime, timedelta
from sensor import generate_sensor_data
import atexit

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)  # Humidifier 5V
GPIO.setup(25, GPIO.OUT)  # Dehumidifier outlet2 230V
GPIO.setup(15, GPIO.OUT)  # Fan Fresh air 12V
GPIO.setup(23, GPIO.OUT)  # Light outlet1 230V
GPIO.setup(16, GPIO.OUT)  # Main Fan outlet3 230V

# Create lock for GPIO operations
gpio_lock = threading.Lock()

# Define GPIO cleanup function
def cleanup_gpio():
    GPIO.output(23, GPIO.LOW)
    GPIO.cleanup()

# Register GPIO cleanup function to be called on program exit
atexit.register(cleanup_gpio)

# Device control functions
def control_device(pin, duration=0):
    with gpio_lock:
        GPIO.output(pin, GPIO.HIGH)
    if duration > 0:
        dt.sleep(duration)
        with gpio_lock:
            GPIO.output(pin, GPIO.LOW)

# Control functions
def humidifier_control():
    control_device(24)

def dehumidifier_control():  # Corrected function name
    control_device(25)  # Corrected pin number

# Main control function
def condition_control():
    exceed_time_low = None
    exceed_time_high = None 

    while True:
        sensor_data = generate_sensor_data()  # Get latest sensor data
        
        humidity = sensor_data.humidity

        if humidity <= 70:
            if exceed_time_low is None:
                exceed_time_low = datetime.now()
            elif datetime.now() - exceed_time_low >= timedelta(seconds=10):
                threading.Thread(target=humidifier_control).start()
                exceed_time_low = None

        else:
            exceed_time_low = None

        if humidity > 90:
            if exceed_time_high is None:
                exceed_time_high = datetime.now() + timedelta(seconds=10)  # Corrected syntax
                threading.Thread(target=dehumidifier_control).start()  # Corrected function name
                exceed_time_high = None

        else:
            exceed_time_high = None

        dt.sleep(5)  # Check conditions every 5 seconds


def light_control():
    on_time = datetime.strptime('09:00:00', '%H:%M:%S').time()
    off_time = datetime.strptime('03:00:00', '%H:%M:%S').time()
    light_state = False

    while True:
        now = datetime.now().time()

        if on_time <= now < off_time:
            if not light_state:
                print("Turning on the light...")
                with gpio_lock:
                    GPIO.output(23, GPIO.HIGH)
                    light_state = True
        else:
            if light_state:
                print("Turning off the light...")
                with gpio_lock:
                    GPIO.output(23, GPIO.LOW)
                    light_state = False

        dt.sleep(10)  # Check every 10 seconds








