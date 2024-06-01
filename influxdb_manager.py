from datetime import datetime
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sensor import SensorData
from config_manager import ConfigManager
from sensor import generate_sensor_data
from email_notification import check_conditions, send_email
from shared_state import shared_state

# Init auth config
config_manager = ConfigManager("config/config.json")

# Init InfluxDBClient
client = InfluxDBClient(url=config_manager.influxdb_config.url, 
                        token=config_manager.influxdb_config.token, 
                        org=config_manager.influxdb_config.org)
write_api = client.write_api(write_options=SYNCHRONOUS)





connection_lost_time = None
connection_alert_time = 0

def write_to_influxdb() -> None:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_data = generate_sensor_data(shared_state.light_state)
    point = Point("sensor_data").tag("location", "indoor") \
                                 .field("temperature", sensor_data.temperature) \
                                 .field("pressure", sensor_data.pressure) \
                                 .field("humidity", sensor_data.humidity) \
                                 .field("vpd", sensor_data.vpd) \
                                 .field("light_state", shared_state.light_state)

    try:
        write_api.write(bucket=config_manager.influxdb_config.bucket, record=point)
        print(f"Sensor data written to InfluxDB at {current_time} with light state {shared_state.light_state}")
        shared_state.last_successful_write = time.time()  # Update the last successful write time
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")
        handle_connection_loss()

    check_conditions(temperature=sensor_data.temperature, 
                     humidity=sensor_data.humidity, 
                     vpd=sensor_data.vpd, 
                     to_email=config_manager.email_config.to_email)

def handle_connection_loss():
    global connection_lost_time
    connection_lost_time = time.time()

def test_influxdb_connection():
    global connection_alert_time
    current_time = time.time()

    if connection_lost_time is not None and current_time - connection_lost_time >= 60:
        if current_time - connection_alert_time >= 60:
            to_email = config_manager.email_config.to_email
            subject = "Connection Alert"
            body = "The connection has been lost for more than 1 minute"
            send_email(subject, body, to_email)
            connection_alert_time = current_time