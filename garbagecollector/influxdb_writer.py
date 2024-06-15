import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sensor import generate_sensor_data
from classes import SensorData
from notification_manager import check_conditions

class InfluxDBWriter:
    def __init__(self, config_path: str):
        self.config = self.read_config(config_path)
        self.influxdb_config = self.config.get("influxdb", {})
        self.email_config = self.config.get("email", {})
        self.url = self.influxdb_config.get("url")
        self.token = self.influxdb_config.get("token")
        self.org = self.influxdb_config.get("org")
        self.bucket = self.influxdb_config.get("bucket")
        self.to_email = self.email_config.get("to_email")

        # Init InfluxDBClient
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    @classmethod
    def read_config(file_path):
        with open(file_path) as f:
            return json.load(f)

    def write_to_influxdb(self) -> None:
        sensor_data: SensorData = generate_sensor_data()
        point = Point("sensor_data").tag("location", "indoor") \
                                     .field("temperature", sensor_data.temperature) \
                                     .field("pressure", sensor_data.pressure) \
                                     .field("humidity", sensor_data.humidity) \
                                     .field("vpd", sensor_data.vpd)

        self.write_api.write(bucket=self.bucket, record=point)
        check_conditions(temperature=sensor_data.temperature, humidity=sensor_data.humidity, vpd=sensor_data.vpd, to_email=self.to_email)
