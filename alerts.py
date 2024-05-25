from datetime import datetime, timedelta

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config_manager import read_config



config = read_config("config.json")
influxdb_config = config.get("influxdb", {})
email_config = config.get("email", {})
to_email = email_config.get("to_email")
from_email = email_config.get("from_email")
email_password = email_config.get("email_password")


def send_email(subject, body, to_email) -> None:
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, email_password)  #replace with your Gmail address AND app password (not ur gmail acc password)
            server.send_message(msg)
            print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Variables to track out-of-range time and last email sent time
out_of_range_start_time_temp = None
out_of_range_start_time_humidity = None
last_email_sent_time = None
email_cooldown = timedelta(minutes=5) #set time between sending alerts 


def check_conditions(temperature, humidity, vpd, to_email):
    global out_of_range_start_time_temp, out_of_range_start_time_humidity, last_email_sent_time
    current_time = datetime.now()
    #Check temperature
    if temperature < 20 or temperature > 28:
        if out_of_range_start_time_temp is None:
            #Start the timer when temperature goes out of range
            out_of_range_start_time_temp = current_time
        elif current_time - out_of_range_start_time_temp > timedelta(minutes=1):
            #Check if enough time has passed since the last email
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                #Temp has been out of range for more than 1 minute
                subject = "Temperature Alert"
                body = f"The current temperature is {temperature:.2f} °C.\nThe current humidity is {humidity:.2f} %.\nThe current VPD is {vpd:.2f} kPa."
                to_email = to_email
                send_email(subject, body, to_email)
                # Reset the timer after sending the email and set the last email sent time
                out_of_range_start_time_temp = None
                last_email_sent_time = current_time
    else:
        #reset the timer if temperature goes back in range
        out_of_range_start_time_temp = None

    #Check humidity
    if humidity < 30 or humidity > 90:
        if out_of_range_start_time_humidity is None:
            #Start the timer when humidity goes out of range
            out_of_range_start_time_humidity = current_time
        elif current_time - out_of_range_start_time_humidity > timedelta(minutes=1):
            #Check if enough time has passed since the last email
            if last_email_sent_time is None or current_time - last_email_sent_time > email_cooldown:
                # Humidity has been out of range for more than 1 minute
                subject = "Humidity Alert"
                body = f"The current humidity is {humidity:.2f} %.\nThe current temperature is {temperature:.2f} C°.\nThe current VPD is {vpd:.2f} kPa."
                to_email = to_email
                send_email(subject, body, to_email)
                #reset the timer after sending the email and set the last email sent time
                out_of_range_start_time_humidity = None
                last_email_sent_time = current_time
    else:
        #reset the timer if humidity goes back in range
        out_of_range_start_time_humidity = None


