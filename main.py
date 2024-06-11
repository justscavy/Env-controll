import time
import threading
from controller import condition_control, light_control
from influxdb_manager import write_to_influxdb
#import sys
#sys.path.append('/home/adminbox/Env-controll/video')
#from video.timelapse_capture import timelapse\


if __name__ == "__main__":
    light_thread = threading.Thread(target=light_control)
    light_thread.start()

    condition_thread = threading.Thread(target=condition_control)
    condition_thread.start()
   # timelapse()
    while True:
        write_to_influxdb()
        time.sleep(1)
