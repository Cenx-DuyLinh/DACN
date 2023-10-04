from picamera import PiCamera
import time
import numpy as np
import cv2

# Create a PiCamera object
camera = PiCamera()
camera.resolution = (640, 480)  # Set resolution as desired
camera.framerate = 5  # Set framerate as desired

# Start the preview
camera.start_preview()

# Allow time for the camera to warm up
time.sleep(2)

frame = np.empty((camera.resolution[1], camera.resolution[0], 3), dtype=np.uint8)
try:
    # Continuously capture video frames
    while True:
        # Capture a frame
        camera.capture(frame, format='rgb')

        # Display the frame using OpenCV
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)  # Delay to show the frame

except KeyboardInterrupt:
    # Close the camera upon keyboard interrupt (Ctrl+C)
    camera.stop_preview()
    camera.close()

# Close the OpenCV window
cv2.destroyAllWindows()