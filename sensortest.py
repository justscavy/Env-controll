import smbus2
import bme280
import math
import time as dt


def scan_i2c_bus(bus):
    print("Scanning I2C bus...")
    devices = []
    for address in range(128):
        try:
            bus.read_byte(address)
            devices.append(hex(address))
        except OSError:
            pass
    return devices

# Initialize I2C bus
i2c_bus = smbus2.SMBus(1)

#start scan
devices = scan_i2c_bus(i2c_bus)


def found_sensors():

    if devices:
        print("Found I2C devices with addresses:", devices)

    elif devices <2:
        send_email(subject, body, to_email)


    #loop through sensor to see if thez work
    for device in devices:
        if device in ['0x76', '0x77']:
            print(f"Initializing BME280 sensor at address {device}")
            address = int(device, 16)
            #load param.
            bme280.load_calibration_params(i2c_bus, address)
            data = bme280.sample(i2c_bus, address)
            print(f"Temperature: {data.temperature:.2f} °C, Pressure: {data.pressure:.2f} hPa, Humidity: {data.humidity:.2f} %")

while True:

    found_sensors()
    dt.sleep(2)
