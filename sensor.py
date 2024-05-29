import random
from math import exp
from dataclasses import dataclass
import smbus2
import bme280

# Define the I2C address and bus
address = 0x76
bus = smbus2.SMBus(1)

@dataclass
class SensorData:
    temperature: float
    pressure: float
    humidity: float
    vpd: float

# Function to load calibration parameters
def load_calibration_params():
    return bme280.load_calibration_params(bus, address)

# Function to read sensor data
def generate_sensor_data():
    # Load calibration parameters
    calibration_params = load_calibration_params()
    
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    
    # Extract temperature, pressure, and humidity
    temperature = data.temperature
    pressure = data.pressure
    humidity = data.humidity
    
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * temperature) / (temperature + 237.3))
    actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    
    # Return sensor data
    return SensorData(temperature=temperature, pressure=pressure, humidity=humidity, vpd=vpd)
