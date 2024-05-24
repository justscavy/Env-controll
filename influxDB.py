import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from alerts import check_conditions, test_influxdb_connection
from sensor import generate_sensor_data
from influxdb_manager import read_config
from classes import SensorData
from datetime import datetime




config = read_config("config.json")

#InfluxDB auth connection
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



if __name__ == "__main__":
    
    while True:
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        write_to_influxdb()
        time.sleep(1)  # Generate data every 1 second
        
        
