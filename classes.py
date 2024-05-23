from dataclasses import dataclass



@dataclass
class SensorData:
    temperature: float
    pressure: float
    humidity: float
    vpd: float