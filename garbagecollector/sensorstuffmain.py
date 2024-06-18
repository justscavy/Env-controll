import smbus2
import bme280
import math

def scan_i2c_bus(bus):
    print("Scanning I2C bus...")
    devices = []
    for address in range(128):
        try:
            bus.read_byte(address)
            devices.append(hex(address))
        except OSError:
            pass  # No device at this address
    return devices

# Initialize I2C bus
i2c_bus = smbus2.SMBus(1)  # Ensure you are using SMBus from smbus2

# Scan the I2C bus
devices = scan_i2c_bus(i2c_bus)

if devices:
    print("Found I2C devices at addresses:", devices)
else:
    print("No I2C devices found")

# You can add code here to initialize the BME280 sensors using the detected addresses
for device in devices:
    if device in ['0x76', '0x77']:
        print(f"Initializing BME280 sensor at address {device}")
        address = int(device, 16)
        # Load calibration parameters
        bme280.load_calibration_params(i2c_bus, address)
        # Example readout (assuming a readout function exists in your implementation)
        data = bme280.sample(i2c_bus, address)
        print(f"Temperature: {data.temperature:.2f} °C, Pressure: {data.pressure:.2f} hPa, Humidity: {data.humidity:.2f} %")



"""
#Define the I2C address and bus
address = 0x77
bus = smbus2.SMBus(1)

#Load calibration parameters
calibration_params = bme280.load_calibration_params(bus, address)

# Initialize timestamp for temperature out of range
out_of_range_start_time = None




def read_sensor_data():
    
    # Read sensor data
    data = bme280.sample(bus, address, calibration_params)
    # Extract temperature, pressure, and humidity
    temperature_celsius = data.temperature
    pressure = data.pressure
    humidity = data.humidity
    print(temperature_celsius, pressure, humidity)
    """
