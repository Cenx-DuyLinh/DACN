from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 30
camera.start_preview()
# Camera warm-up time
sleep(5)
while True:
    camera.capture('foo.jpg')
    sleep(0.1)