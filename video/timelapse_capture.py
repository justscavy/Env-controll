import cv2
import time
import os

# Directory to save images
output_dir = '/media/adminbox/ESD-USB1'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Set up the video capture with the USB camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Capture interval in seconds (e.g., capture every 10 minutes)
interval = 360

try:
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if ret:
            # Save the frame as an image
            image_path = os.path.join(output_dir, f'frame_{frame_count:04d}.jpg')
            cv2.imwrite(image_path, frame)
            frame_count += 1
            print(f'Captured {image_path}')
        else:
            print("Error: Could not read frame.")

        # Wait for the specified interval
        time.sleep(interval)
except KeyboardInterrupt:
    print("Timelapse capture stopped.")
finally:
    cap.release()
