import cv2
import time
import os
import re


def timelapse():
    output_dir = '/home/adminbox/Env-controll/video'
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    except Exception as e:
        print(f"Error: Could not create directory {output_dir}. {e}")
        exit()

    #find last highest picture number
    def find_highest_frame_number(directory):
        frame_pattern = re.compile(r'frame_(\d{4}).jpg')
        max_frame = -1
        for filename in os.listdir(directory):
            match = frame_pattern.match(filename)
            if match:
                frame_num = int(match.group(1))
                max_frame = max(max_frame, frame_num)
        return max_frame
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()


    interval = 360
    frame_count = find_highest_frame_number(output_dir) + 1

    try:
        while True:
            ret, frame = cap.read()
            if ret:
                try:
          
                    image_path = os.path.join(output_dir, f'frame_{frame_count:04d}.jpg')
                    cv2.imwrite(image_path, frame)
                    frame_count += 1
                    print(f'Captured {image_path}')
                except Exception as e:
                    print(f"Error: Could not save frame to {image_path}. {e}")
            else:
                print("Error: Could not read frame.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Timelapse capture stopped by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera and all windows released.")


timelapse()



