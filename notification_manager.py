from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config_manager import ConfigManager
import smbus2
import bme280
import math
import time as dt


config_manager = ConfigManager("config/config.json")
to_email = config_manager.email_config.to_email

def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = config_manager.email_config.from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config_manager.email_config.from_email, config_manager.email_config.email_password)
            server.send_message(msg)
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Track out-of-range time and last email sent time
out_of_range_start_time_temp = None
out_of_range_start_time_humidity = None
out_of_range_start_time_vpd = None
last_email_sent_time = None
email_cooldown = timedelta(minutes=5)  # Set time between sending alerts

# The idea is to first let the program try to handle the environment before taking actions.
# After <5mins> give out notifications
def check_conditions(temperature, humidity, vpd, to_email):
    global out_of_range_start_time_temp, out_of_range_start_time_humidity, out_of_range_start_time_vpd, last_email_sent_time
    current_time = datetime.now()
    # Check temperature
    if temperature < 18 or temperature > 30:
        if out_of_range_start_time_temp is None:
            # Start the timer when temperature goes out of range
            out_of_range_start_time_temp = current_time
        elif current_time - out_of_range_start_time_temp > timedelta(minutes=1):  # Set to 5
            # Check if enough time has passed since the last email
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                # Temp has been out of range for more than 1 minute
                subject = "Temperature Alert"
                body = f"The current temperature is {temperature:.2f} °C.\nThe current humidity is {humidity:.2f} %.\nThe current VPD is {vpd:.2f} kPa."
                send_email(subject, body, to_email)
                # Reset the timer after sending the email and set the last email sent time
                out_of_range_start_time_temp = None
                last_email_sent_time = current_time
    else:
        # Reset timer if temperature goes back in range
        out_of_range_start_time_temp = None

    if humidity < 60 or humidity > 90:
        if out_of_range_start_time_humidity is None:
            # Start the timer when humidity goes out of range
            out_of_range_start_time_humidity = current_time
        elif current_time - out_of_range_start_time_humidity > timedelta(minutes=1):  # Set to 5
            # Check if enough time has passed since the last email
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                # Humidity has been out of range for more than 1 minute
                subject = "Humidity Alert"
                body = f"The current humidity is {humidity:.2f} %.\nThe current temperature is {temperature:.2f} °C.\nThe current VPD is {vpd:.2f} kPa."
                send_email(subject, body, to_email)
                # Reset the timer after sending the email and set the last email sent time
                out_of_range_start_time_humidity = None
                last_email_sent_time = current_time
    else:
        # Reset the timer if humidity goes back in range
        out_of_range_start_time_humidity = None
    
    if vpd < 0.40 or vpd > 0.95:
        if out_of_range_start_time_vpd is None:
            # Start the timer when humidity goes out of range
            out_of_range_start_time_vpd = current_time
        elif current_time - out_of_range_start_time_vpd > timedelta(minutes=1):  # Set to 5
            # Check if enough time has passed since the last email
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                # Humidity has been out of range for more than 1 minute
                subject = "Vpd Alert"
                body = f"The current vpd is {vpd:.2f} kPa.\nThe current temperature is {temperature:.2f} °C.\nThe current humidity is {humidity:.2f} %."
                send_email(subject, body, to_email)
                # Reset the timer after sending the email and set the last email sent time
                out_of_range_start_time_vpd = None
                last_email_sent_time = current_time
    else:
        # Reset the timer if humidity goes back in range
        out_of_range_start_time_vpd = None

def restart_notification():
    subject = "Raspberry Restart"
    body = "Log entry todo"
    send_email(subject, body, to_email)


def scan_i2c_bus(bus):
    print("Scanning I2C bus...")
    devices = []
    for address in range(128):
        try:
            bus.read_byte(address)
            devices.append(hex(address))
        except OSError:
            pass
    return devices

# Initialize I2C bus
i2c_bus = smbus2.SMBus(1)

def found_sensors():
    global last_email_sent_time
    while True:
        devices = scan_i2c_bus(i2c_bus)
        print("Found I2C devices with addresses:", devices)
        
        if len(devices) < 2:
            current_time = datetime.now()
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                subject = "Sensor disconnected"
                body = "Sensor lost connection. Found sensors: " + ", ".join(devices)
                send_email(subject, body, to_email)
                last_email_sent_time = current_time
        else:
            # Loop through sensors to see if they work
            for device in devices:
                if device in ['0x76', '0x77']:
                    print(f"Initializing BME280 sensor at address {device}")
                    address = int(device, 16)
                    try:
                        # Load calibration params and read data
                        bme280.load_calibration_params(i2c_bus, address)
                        data = bme280.sample(i2c_bus, address)
                        print(f"Sensor data: {data}")
                    except Exception as e:
                        print(f"Failed to initialize or read from sensor at address {device}: {e}")
        # Sleep for a few seconds before the next scan
        dt.sleep(5)

