from time import sleep
from picamera import PiCamera
import cv2
import numpy as np

def get_dominant_color(frame):
    avg_color = np.mean(frame, axis=(0, 1))

    if avg_color[2] > avg_color[1] and avg_color[2] > avg_color[0]:
        return "Red"
    elif avg_color[1] > avg_color[2] and avg_color[1] > avg_color[0]:
        return "Green"
    else:
        return "Blue"

camera = PiCamera()
camera.resolution = (1920, 1080)
camera.start_preview()

try:
    while True:
        # Capture an image into a flat numpy array
        image = np.empty((1920 * 1088 * 3,), dtype=np.uint8)
        camera.capture(image, 'bgr', use_video_port=True)
        image = image.reshape((1088, 1920, 3))

        # Get the dominant color
        dominant_color = get_dominant_color(image)

        # Display the result in the console
        print(f"Couleur dominante : {dominant_color}")

finally:
    camera.stop_preview()
