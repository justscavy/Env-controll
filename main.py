import time
import threading
from controller import condition_control, light_control
from influxdb_manager import write_to_influxdb
from notification_manager import restart_notification
from wage import wage, initialize_hx711
#import sys
#sys.path.append('/home/adminbox/Env-controll/video')
#from video.timelapse_capture import timelapse\



if __name__ == "__main__":
    hx = initialize_hx711()
    
    restart_notification()
    light_thread = threading.Thread(target=light_control)
    light_thread.start()

    condition_thread = threading.Thread(target=condition_control)
    condition_thread.start()
   # timelapse()
    while True:
        val_A, val_B = wage(hx)
        #print("A: %s  B: %s" % (val_A, val_B))
        write_to_influxdb()
        time.sleep(1)
