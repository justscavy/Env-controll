from datetime import datetime
import time

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from sensor import SensorData
from config_manager import ConfigManager
from sensor import generate_sensor_data
from alerts import check_conditions, send_email



#init auth config
config_manager = ConfigManager("config/config.json")

# Init InfluxDBClient
client = InfluxDBClient(url=config_manager.influxdb_config.url, 
                        token=config_manager.influxdb_config.token, 
                        org=config_manager.influxdb_config.org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# write from sensor -> influxDB
def write_to_influxdb() -> None:
    #just to see if programm still inserting data in console
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_data: SensorData = generate_sensor_data()
    point = Point("sensor_data").tag("location", "indoor") \
                                 .field("temperature", sensor_data.temperature) \
                                 .field("pressure", sensor_data.pressure) \
                                 .field("humidity", sensor_data.humidity) \
                                 .field("vpd", sensor_data.vpd)

    try:
        write_api.write(bucket=config_manager.influxdb_config.bucket, record=point)
        print(f"Sensor data written to InfluxDB", current_time)
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")
        test_influxdb_connection()
    #condition be set in alerts
    check_conditions(temperature=sensor_data.temperature, 
                     humidity=sensor_data.humidity, 
                     vpd=sensor_data.vpd, 
                     to_email=config_manager.email_config.to_email)

connection_alert_time = 0

def test_influxdb_connection():
    global connection_alert_time
    current_time = time.time()

    # 30 mins passe send another email
    if current_time - connection_alert_time >= 30 * 60:
        to_email = config_manager.email_config.to_email
        subject = "Connection Alert"
        body = f"The connection has been lost"
        send_email(subject, body, to_email)

        # Update the last email time
        connection_alert_time = current_time
