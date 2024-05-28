import time
import threading
#from controller import condition_control, light_control
from influxdb_manager import write_to_influxdb



if __name__ == "__main__":
    #light_control()
    #condition_control()
    while True:
        write_to_influxdb()
        time.sleep(1)  # Generate data every 1 second
