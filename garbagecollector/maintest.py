import cv2
import os

# Directory to save images
output_dir = '/home/adminbox/Env-controll/video'
try:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
except Exception as e:
    print(f"Error: Could not create directory {output_dir}. {e}")
    exit()

# Function to find a working video device
def find_working_device():
    for device_index in range(32):  # Assuming the device indices range from 0 to 31
        cap = cv2.VideoCapture(device_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Video device /dev/video{device_index} is working.")
                cap.release()
                return device_index
            cap.release()
    return -1

# Find the working video device
device_index = find_working_device()
if device_index == -1:
    print("Error: Could not find any working video device.")
    exit()

# Set up the video capture with the found video device
cap = cv2.VideoCapture(device_index)
if not cap.isOpened():
    print(f"Error: Could not open camera at /dev/video{device_index}.")
    exit()

# Capture interval in seconds (e.g., capture every 10 minutes)
interval = 360

try:
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            try:
                # Save the frame as an image
                image_path = os.path.join(output_dir, f'frame_{frame_count:04d}.jpg')
                cv2.imwrite(image_path, frame)
                frame_count += 1
                print(f'Captured {image_path}')
            except Exception as e:
                print(f"Error: Could not save frame to {image_path}. {e}")
        else:
            print("Error: Could not read frame.")

        # Wait for the specified interval
        time.sleep(interval)
except KeyboardInterrupt:
    print("Timelapse capture stopped by user.")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("Camera and all windows released.")
