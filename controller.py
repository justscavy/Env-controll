import RPi.GPIO as GPIO
import threading
import time as dt
from datetime import datetime, timedelta
from sensor import SensorData
'''
# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # Humidifier 5V
GPIO.setup(18, GPIO.OUT)  # Dehumidifier outlet2 230V
GPIO.setup(15, GPIO.OUT)  # Fan Fresh air 12V
GPIO.setup(13, GPIO.OUT)  # Light outlet1 230V
GPIO.setup(16, GPIO.OUT)  # Main Fan outlet3 230V



sensor_data = SensorData(temperature=SensorData.temperature, humidity=SensorData.humidity, vpd=SensorData.vpd)

#Device control functions
def control_device(pin, duration=0):
    GPIO.output(pin, GPIO.HIGH)
    if duration > 0:
        dt.sleep(duration)
        GPIO.output(pin, GPIO.LOW)

def humidifier_control():
    control_device(17)

def dehumidifier_control():
    control_device(18)

def input_fan_control():
    control_device(15)

def light_controll():
    control_device(13)

def main_fan():
    control_device (16)



def condition_control():
    exceed_time_low = None
    exceed_time_high = None 

    while True:
        sensor_data = generate_sensor_data()  # Assume this function gets the latest sensor data
        temperature = sensor_data.temperature
        humidity = sensor_data.humidity
        vpd = sensor_data.vpd

        if humidity <= 70:
            if exceed_time_low is None:
                exceed_time_low = datetime.now()
            elif datetime.now() - exceed_time_low >= timedelta(minutes=1): #after condition is 1min true start  
                threading.Thread(target=humidifier_control).start()
                exceed_time_low = None  # Reset the timer after starting the humidifier
        else:
            exceed_time_low = None  # Reset the timer if humidity is not < 70%

        if humidity > 90:
            if exceed_time_high is None:
                exceed_time_high = datetime.now()
            elif datetime.now() - exceed_time_high >= timedelta(minutes=1): #after condition is 1min true start  
                threading.Thread(target=main_fan_control).start()
                exceed_time_high = None  # Reset the timer after starting the main_fan
        else:
            exceed_time_high = None  # Reset the timer if humidity is not > 90%

        dt.sleep(5)  # Check conditions every 5 seconds




#light_state=0
def light_control():
    #global light_state #track light state for influxdb
    #start/end time for light
    on_hour, on_minute = 6, 0  # 6:00 AM
    off_hour, off_minute = 0, 0  # 12:00 AM (midnight)
    on_time = dt(on_hour, on_minute)
    off_time = dt(off_hour, off_minute)
    
    while True:
        now = datetime.now().time()

        if on_time <= now < off_time:
            GPIO.output(13, GPIO.HIGH)  # Turn on the light
            light_state = 1
        else:
            GPIO.output(13, GPIO.LOW)   # Turn off the light
            light_state = 0

        dt.sleep(60)  # Check every minute
        '''
    


