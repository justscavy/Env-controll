import time

from influxdb_manager import write_to_influxdb



if __name__ == "__main__":
    while True:
        write_to_influxdb()
        time.sleep(1)  # Generate data every 1 second
