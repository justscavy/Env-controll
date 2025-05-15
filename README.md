HVAC Controller

Developed a fully automated HVAC controller that monitors and regulates light, temperature, humidity, vpd, watering system, air circulation / airflow, heating rod and weight of plants to optimize plant growth. This embedded system integrates sensors and actuators controlled via an raspberrypi microcontroller, demonstrating expertise in IoT and automation.


## Features

- Real time Data visualisation per influxdata
  Temperature / Humidity folr different Zones
  Weight of each Plant
  
  Status from all devices:
    Humidifier
    Dehumidifier
    Light
    3 x Fans
    heating element
    waterpump
  
- notifications for thresholds and Warnings on your smartphone
  
- Modular and exstensible design for future sensors / actuators via plug&play

## Hardware requirements

RaspberryPI 2GB RAM min.
MicroSD 32GB
USB-C Kabel + Winkeladapter
Main Exhaust fan
environment-fan x2
Waterpump
Main light
5V 1chan relais
BME280 Sensor x2
Breadboard
Jumper cables
12V 4chan SSR Low Level Trigger relais
15V Power supply
12V Power supply
Load Cell Weight Sensor
HX711 Dual Channel
12V Waterpump

distribution
Sicherung/RCD 10A pref.
Kleinverteiler
Ap Steckdose 3Fach (contacts must be seperated.)


## Installation

1. Clone this repository

2. download the latest flux client at https://www.influxdata.com/downloads/
2.2 create account at http://localhost:8086/

3. create an gmail account, 2FA must be enabled!!
3.2 create an app at https://myaccount.google.com/u/5/apppasswords?rapt=AEjHL4OHSMiTk2LrPZ4ej33cm1stjrzY34jaaodaYg8Sr2ia2EBoCiM09yZK16fJ8VdjgbdhOnnv_iQdflYRD88bjXZeRhcHmD7IGE_JFe5InJ_FpOLiq1g save password for json file.

4.1 install the requirements.txt

5. Modify ur thresholds in the controller.py file
5.1 tare ur wage adjusting tare_values.json file
5.2 configure the config_copy.json file with your credentials and rename it to config.json

6. adjust and setup sensors and other hardware

   
