import RPi.GPIO as GPIO
import time
import threading
from sensor import SensorData

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # Humidifier 5V
GPIO.setup(18, GPIO.OUT)  # Dehumidifier 230V
GPIO.setup(15, GPIO.OUT)  # Input fan 12V

# Initialize sensor data
sensor_data = SensorData(temperature=SensorData.temperature, humidity=SensorData.humidity, vpd=SensorData.vpd)

# Device control functions
def control_device(pin, duration=0):
    GPIO.output(pin, GPIO.HIGH)
    if duration > 0:
        time.sleep(duration)
        GPIO.output(pin, GPIO.LOW)

def humidifier_control():
    control_device(17)

def dehumidifier_control():
    control_device(18)

def input_fan_control():
    control_device(15)

# Function to check conditions and control environment mazbe get from check conditions TODO
def condition_control():
    while True:
        temperature = sensor_data.temperature
        humidity = sensor_data.humidity
        vpd = sensor_data.vpd

        if temperature >= 26:
            threading.Thread(target=humidifier_control).start()
            threading.Thread(target=input_fan_control).start()
            time.sleep(180)  # Run for 3 more minutes

        elif humidity >= 55:

            threading.Thread(target=dehumidifier_control).start()

        time.sleep(5)  #check conditions every 5 seconds

'''
if __name__ == "__main__":
    try:
        condition_control()
    except KeyboardInterrupt:
        GPIO.cleanup()
        '''
