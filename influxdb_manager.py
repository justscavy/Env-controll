from datetime import datetime
import time

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from classes import SensorData
from sensor import generate_sensor_data
from alerts import send_email, check_conditions
from config_manager import ConfigManager



config_manager = ConfigManager("config/config.json")

#init InfluxDBClient
client = InfluxDBClient(url=config_manager.influxdb_url, token=config_manager.influxdb_token, org=config_manager.influxdb_org)
write_api = client.write_api(write_options=SYNCHRONOUS)


def write_to_influxdb() -> None:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_data: SensorData = generate_sensor_data()
    point = Point("sensor_data").tag("location", "indoor") \
                                 .field("temperature", sensor_data.temperature) \
                                 .field("pressure", sensor_data.pressure) \
                                 .field("humidity", sensor_data.humidity) \
                                 .field("vpd", sensor_data.vpd)

    try:
        write_api.write(bucket=config_manager.influxdb_bucket, record=point)  # Corrected line
        print(f"Sensor data written to InfluxDB", current_time)
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")
        test_influxdb_connection()

    check_conditions(temperature=sensor_data.temperature, humidity=sensor_data.humidity, vpd=sensor_data.vpd, to_email=config_manager.email_to)



connection_alert_time = 0

def test_influxdb_connection():
    global connection_alert_time
    current_time = time.time()

    #30mins passed send next email
    if current_time - connection_alert_time >= 30 * 60:
        email_config = config_manager.email_config
        to_email = email_config.get("to_email")
        subject = "Connection Alert"
        body = f"The connection has been lost"
        send_email(subject, body, to_email)

        #Update the last email time
        connection_alert_time = current_time

