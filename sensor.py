import random
from math import exp
from dataclasses import dataclass
#import smbus2
#import bme280

@dataclass
class SensorData:
    temperature: float
    pressure: float
    humidity: float
    vpd: float


#simulate sensor data
def generate_sensor_data() -> tuple:
    #random test values
    temperature = random.uniform(0.0, 40.0)
    pressure = random.uniform(100.0, 1000.0)
    humidity = random.uniform(0.0, 20.0)
    
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * temperature) / (temperature + 237.3))
    actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    return SensorData(temperature=temperature, pressure=pressure, humidity=humidity, vpd=vpd)





"""
I2C communication is not enabled by default. You need to enable it manually.
Open a terminal window on your Raspberry Pi and type the following command:

sudo raspi-config
Interface Options Configure connections to peripherals      select
I2C Enable/disable automatic loading of I2  kernel module   enable
sudo reboot



With the sensor connected to the Raspberry Pi, lets check if the sensor is connected properly by searching for its I2C address.
Open a Terminal window on your Raspberry Pi and run the following command:

sudo i2cdetect -y 1
sudo pip install --upgrade pip
sudo pip install RPI.BME280


#Define the I2C address and bus
address = 0x76
bus = smbus2.SMBus(1)

#Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)


def read_sensor_data():
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    # Extract temperature, pressure, and humidity
    
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * data.temperature) / (data.temperature + 237.3))
    actual_vapor_pressure = (data.humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    return SensorData(temperature=data.temperature, pressure=data.pressure, humidity=data.humidity, vpd=vpd)
"""