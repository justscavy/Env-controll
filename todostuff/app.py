from flask import Flask, jsonify, render_template
import random
from classes import SensorData
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from math import exp
import json


'''for later webapp use maybe'''

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

app = Flask(__name__)


client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)


#Simulated data function with random values
def mock_bme280_sample():
    class MockData:
        def __init__(self, temperature, pressure, humidity):
            self.temperature = temperature
            self.pressure = pressure
            self.humidity = humidity

    temperature = random.uniform(5.0, 40.0)
    pressure = random.uniform(900.0, 1100.0)
    humidity = random.uniform(40.0, 60.0)

    return MockData(temperature=temperature, pressure=pressure, humidity=humidity)


@app.route('/')
def index():
    data = mock_bme280_sample()
    sensor_data = SensorData(
        temperature_celsius=data.temperature,
        pressure=data.pressure,
        humidity=data.humidity,
    )

    return render_template('index.html', sensor_data=sensor_data)



@app.route('/api/data')
def get_sensor_data():
    #simulate sensor
    temperature = random.uniform(5.0, 40.0)
    pressure = random.uniform(900.0, 1100.0)
    humidity = random.uniform(40.0, 60.0)
    saturation_vapor_pressure = 0.611 * exp((17.27 * temperature) / (temperature + 237.3))
    actual_vapor_pressure = (humidity / 100) * saturation_vapor_pressure
    vpd = saturation_vapor_pressure - actual_vapor_pressure
    point = Point("sensor_data").tag("location", "indoor").field("temperature", temperature).field("pressure", pressure).field("humidity", humidity).field("vpd", vpd)
    write_api.write(bucket=bucket, record=point)

    return jsonify(
        temperature=f"{temperature:.2f} °C",
        pressure=f"{pressure:.2f} hPa",
        humidity=f"{humidity:.2f} %",
        vpd=f"{vpd:.2f} kPa",
    )

if __name__ == '__main__':
    app.run(host='192.168.2.118', port=5000, debug=True)  #host=ur local network



