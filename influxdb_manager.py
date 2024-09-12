# influxdb_manager.py
from datetime import datetime
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from sensor import Sensor, Location, address_box, address_room
from config_manager import ConfigManager
from notification_manager import check_conditions, send_email
from shared_state import shared_state
from wage import wage, initialize_hx711

# Init auth config
config_manager = ConfigManager("config/config.json")

# Init InfluxDBClient
client = InfluxDBClient(url=config_manager.influxdb_config.url, 
                        token=config_manager.influxdb_config.token, 
                        org=config_manager.influxdb_config.org)
write_api = client.write_api(write_options=SYNCHRONOUS)

connection_lost_time = None
connection_alert_time = 0

room_sensor = Sensor(address=address_room, location=Location.ROOM)
box_sensor = Sensor(address=address_box, location=Location.BOX)

# Initialize the HX711
hx = initialize_hx711()

def write_to_influxdb() -> None:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Fetch data from sensors
        room_sensor_data = room_sensor.get_data()                                     

    except Exception as e:
        print(f"Failed to get data from room sensor: {e}")
        room_sensor_data = None

    try:
        box_sensor_data = box_sensor.get_data()
    except Exception as e:
        print(f"Failed to get data from box sensor: {e}")
        box_sensor_data = None

    # Fetch weight data
    try:
        val_A, val_B = wage(hx)
    except Exception as e:
        print(f"Failed to get data from HX711: {e}")
        val_A, val_B = None, None

    if room_sensor_data:
        room_point = Point("sensor_data").tag("location", "outside") \
                                          .field("temperature", room_sensor_data.temperature) \
                                          .field("pressure", room_sensor_data.pressure) \
                                          .field("humidity", room_sensor_data.humidity) \
                                          .field("vpd", room_sensor_data.vpd)
    else:
        room_point = None

    if box_sensor_data:
        box_point = Point("sensor_data").tag("location", "growbox") \
                                        .field("temperature", box_sensor_data.temperature) \
                                        .field("pressure", box_sensor_data.pressure) \
                                        .field("humidity", box_sensor_data.humidity) \
                                        .field("vpd", box_sensor_data.vpd)
    else:
        box_point = None

    state_point = Point("state_data").tag("location", "indoor") \
                                     .field("light_state", shared_state.light_state) \
                                     .field("humidifier_state", shared_state.humidifier_state) \
                                     .field("dehumidifier_state", shared_state.dehumidifier_state) \
                                     .field("heatmat_state", shared_state.heatmat_state) \
                                     .field("water_drain_state", shared_state.water_detected_state) \
                                     .field("waterpump_state", shared_state.waterpump_state) 


    if val_A is not None and val_B is not None:
        wage_point = Point("wage_data").tag("location", "wage") \
                                       .field("Wage1", val_A) \
                                       .field("Wage2", val_B)
    else:
        wage_point = None

    points = [point for point in [room_point, box_point, state_point, wage_point] if point is not None]

    try:
        write_api.write(bucket=config_manager.influxdb_config.bucket, record=points)
        shared_state.last_successful_write = time.time()  # Update the last successful write time
    except Exception as e:
        print(f"Failed to write data to InfluxDB: {e}")
        handle_connection_loss()

    # Check conditions and send notifications if needed
    if box_sensor_data:
        check_conditions(temperature=box_sensor_data.temperature, 
                         humidity=box_sensor_data.humidity, 
                         vpd=box_sensor_data.vpd, 
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
