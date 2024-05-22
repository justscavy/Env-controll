import random
import json
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from math import exp
from alerts_copy import check_conditions

#read json file
def read_config(file_path):
    with open(file_path) as f:
        return json.load(f)

config = read_config("config.json")
influxdb_config = config.get("influxdb", {})
email_config = config.get("email", {})

#influx auth connection
url = influxdb_config.get("url")
token = influxdb_config.get("token")
org = influxdb_config.get("org")
bucket = influxdb_config.get("bucket")

#email receiver
to_email = email_config.get("to_email")

#init influxclient
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

#init timestamp
out_of_range_start_time = None

# Simulate sensor data
def generate_sensor_data() -> tuple:
    temperature = random.uniform(0.0, 40.0)
    pressure = random.uniform(100.0, 1000.0)
    humidity = random.uniform(0.0, 20.0)
    # Calculate saturation vapor pressure (in kPa)
    saturation_vapor_pressure = 0.611 * exp((17.27 * temperature) / (temperature + 237.3))
    actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    return temperature, pressure, humidity, vpd

#write data to influx
def write_to_influxdb() -> None:
    temperature, pressure, humidity, vpd = generate_sensor_data()
    point = Point("sensor_data").tag("location", "indoor") \
                                 .field("temperature", temperature) \
                                 .field("pressure", pressure) \
                                 .field("humidity", humidity) \
                                 .field("vpd", vpd)

    write_api.write(bucket=bucket, record=point)

    check_conditions(temperature=temperature, humidity=humidity, vpd=vpd, to_email=to_email)

if __name__ == "__main__":
    while True:
        write_to_influxdb()
        print("Sensor data written to InfluxDB")
        time.sleep(1)  # Generate data every 1 second
