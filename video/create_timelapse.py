import imageio
import os

# Directory containing captured images
image_dir = '/media/adminbox/ESD-USB1/timelapse'
# Path to save the timelapse video
output_video = '/media/adminbox/ESD-USB1/timelapse_video.mp4'

# Get the list of image files
images = sorted([img for img in os.listdir(image_dir) if img.endswith('.jpg')])

# Create the video writer
with imageio.get_writer(output_video, fps=30) as writer:
    for image_file in images:
        image_path = os.path.join(image_dir, image_file)
        image = imageio.imread(image_path)
        writer.append_data(image)
        print(f'Added {image_path} to video')

print(f'Timelapse video saved to {output_video}')


