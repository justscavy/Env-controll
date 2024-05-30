import random
from sensor import SensorData
from math import exp
from dataclasses import dataclass
import smbus2
import bme280

# Define the I2C address and bus
address = 0x76
bus = smbus2.SMBus(1)

# Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

@dataclass
class SensorData:
    temperature: float
    pressure: float
    humidity: float
    vpd: float

def read_sensor_data():
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    # Extract temperature, pressure, and humidity
    
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * data.temperature) / (data.temperature + 237.3))
    actual_vapor_pressure = (data.humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    

    return SensorData(temperature=data.temperature, pressure=data.pressure, humidity=data.humidity, vpd=vpd)

# Main function to read and print sensor data
if __name__ == "__main__":
    sensor_data = read_sensor_data()
