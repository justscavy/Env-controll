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
    light_state: int

# Function to load calibration parameters
def load_calibration_params():
    return bme280.load_calibration_params(bus, address)

# Load calibration parameters
calibration_params = load_calibration_params()

def generate_sensor_data(light_state):
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    
    # Adjust the temperature and humidity
    adjusted_temperature = data.temperature + 0.5
    adjusted_humidity = data.humidity + 6
    
    # Ensure humidity stays within the valid range (0-100%)
    if adjusted_humidity > 100:
        adjusted_humidity = 100

    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * adjusted_temperature) / (adjusted_temperature + 237.3))
    actual_vapor_pressure = (adjusted_humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    
    return SensorData(temperature=adjusted_temperature, pressure=data.pressure, humidity=adjusted_humidity, vpd=vpd, light_state=light_state)
