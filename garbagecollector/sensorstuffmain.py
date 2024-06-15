import time
import smbus2
import bme280
import math
from datetime import datetime, timedelta
from sensor import SensorData  # Import the SensorData dataclass
from notification_manager import send_email  # Import the send_email function

'''
I2C communication is not enabled by default. You need to enable it manually.
Open a terminal window on your Raspberry Pi and type the following command:

sudo raspi-config
Interface Options Configure connections to peripherals      select
I2C Enable/disable automatic loading of I2  kernel module   enable
sudo reboot
'''

'''
With the sensor connected to the Raspberry Pi, lets check if the sensor is connected properly by searching for its I2C address.
Open a Terminal window on your Raspberry Pi and run the following command:

sudo i2cdetect -y 1
sudo pip install --upgrade pip
sudo pip install RPI.BME280
'''



#Define the I2C address and bus
address = 0x76
bus = smbus2.SMBus(1)

#Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

# Initialize timestamp for temperature out of range
out_of_range_start_time = None


def vpd_converter(temperature_celsius, humidity):
    e_s = 0.6108 * math.exp((17.27 * temperature_celsius) / (temperature_celsius + 237.3))
    e_a = e_s * (humidity / 100.0)
    vpd = e_s - e_a
    return vpd

def read_sensor_data():
    
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    # Extract temperature, pressure, and humidity
    temperature_celsius = data.temperature
    pressure = data.pressure
    humidity = data.humidity
    # Estimate leaf temperature (4-6°C cooler than room temperature)
    leaf_temperature_celsius = temperature_celsius - 5  # Adjust as needed
    # Calculate VPD using leaf temperature
    vpd = vpd_converter(leaf_temperature_celsius, humidity)
    return SensorData(
        pressure=pressure,
        temperature_celsius=temperature_celsius,
        humidity=humidity,
        vpd=vpd
    )