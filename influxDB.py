import random
import json
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from math import exp
from alerts import check_conditions
from sensor import generate_sensor_data

#read json file
def read_config(file_path):
    with open(file_path) as f:
        return json.load(f)

#influx auth connection
config = read_config("config.json")
influxdb_config = config.get("influxdb", {})
email_config = config.get("email", {})
url = influxdb_config.get("url")
token = influxdb_config.get("token")
org = influxdb_config.get("org")
bucket = influxdb_config.get("bucket")
to_email = email_config.get("to_email")

#init influxclient
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


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
