import random
from math import exp

from classes import SensorData


#simulate sensor data
def generate_sensor_data() -> tuple:
    temperature = random.uniform(0.0, 40.0)
    pressure = random.uniform(100.0, 1000.0)
    humidity = random.uniform(0.0, 20.0)
    
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * temperature) / (temperature + 237.3))
    actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    return SensorData(temperature=temperature, pressure=pressure, humidity=humidity, vpd=vpd)