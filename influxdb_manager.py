from datetime import datetime
import time

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

from classes import SensorData
from sensor import generate_sensor_data
from alerts import check_conditions, send_email
from config_manager import read_config



config = read_config("config.json")
influxdb_config = config.get("influxdb", {})
email_config = config.get("email", {})
url = influxdb_config.get("url")
token = influxdb_config.get("token")
org = influxdb_config.get("org")
bucket = influxdb_config.get("bucket")
to_email = email_config.get("to_email")

#init InfluxDBClient
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# write data to InfluxDB
def write_to_influxdb() -> None:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sensor_data: SensorData = generate_sensor_data()
    point = Point("sensor_data").tag("location", "indoor") \
                                 .field("temperature", sensor_data.temperature) \
                                 .field("pressure", sensor_data.pressure) \
                                 .field("humidity", sensor_data.humidity) \
                                 .field("vpd", sensor_data.vpd)

    try:
        write_api.write(bucket=bucket, record=point)
        print(f"Sensor data written to InfluxDB", current_time)
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")
        test_influxdb_connection()
    
    check_conditions(temperature=sensor_data.temperature, humidity=sensor_data.humidity, vpd=sensor_data.vpd, to_email=to_email)




connection_alert_time = 0

def test_influxdb_connection():
    global connection_alert_time

    # Get the current time
    current_time = time.time()

    #30mins passed send next email
    if current_time - connection_alert_time >= 30 * 60:
        config = read_config("config.json")
        email_config = config.get("email", {})
        to_email = email_config.get("to_email")
        subject = "Connection Alert"
        body = f"The connection has been lost"
        send_email(subject, body, to_email)

        # Update the last email time
        connection_alert_time = current_time
