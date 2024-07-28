from notification_manager import found_sensors
import time as dt
import threading

# Start the sensor scanning in a separate thread
sensor_thread = threading.Thread(target=found_sensors)
sensor_thread.daemon = True
sensor_thread.start()
# Keep the main thread alive
try:
    while True:
        dt.sleep(1)  # Adjust sleep as needed to keep the main thread running
except KeyboardInterrupt:
    print("Program interrupted by user")