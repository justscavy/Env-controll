import random
from math import exp
from dataclasses import dataclass
import smbus2
import bme280
from enum import Enum, auto

address_box = 0x76
address_room = 0x77
bus = smbus2.SMBus(1)

@dataclass
class SensorData:
    temperature: float
    pressure: float
    humidity: float
    vpd: float

class Location(Enum):
    BOX = auto()
    ROOM = auto()

@dataclass
class Sensor:
    address: int 
    location: Location

    def get_data(self) -> SensorData:
        # Read sensor data
        data = bme280.sample(bus, self.address, calibration_params)
        # Adjust the temperature and humidity (calibrated with govee h5705)
        adjusted_temperature = data.temperature + 0.5  # still 0.6 less than govee
        adjusted_humidity = data.humidity + 4
        
        # Specific adjustment for the room sensor (address 0x77)
        if self.address == address_room:
            adjusted_humidity -= 16  # Apply the adjustment with assignment

            adjusted_temperature += 1.5
        # Ensure humidity stays within the valid range (0-100%)
        if adjusted_humidity > 100:
            adjusted_humidity = 100
        elif adjusted_humidity < 0:
            adjusted_humidity = 0

        # VPD calculation (in kPa)
        saturation_vapor_pressure = 0.611 * exp((17.27 * adjusted_temperature) / (adjusted_temperature + 237.3))
        actual_vapor_pressure = (adjusted_humidity / 100) * saturation_vapor_pressure
        vpd = saturation_vapor_pressure - actual_vapor_pressure

        return SensorData(temperature=adjusted_temperature, pressure=data.pressure, humidity=adjusted_humidity, vpd=vpd)

# Function to load calibration parameters
def load_calibration_params():
    return bme280.load_calibration_params(bus, address_box)  # assuming same calibration for both sensors

# Load calibration parameters
calibration_params = load_calibration_params()

# Initialize sensors
room_sensor = Sensor(address=address_room, location=Location.ROOM)
box_sensor = Sensor(address=address_box, location=Location.BOX)

# Example usage
room_data = room_sensor.get_data()
box_data = box_sensor.get_data()

print(f"Room Sensor Data: {room_data}")
print(f"Box Sensor Data: {box_data}")