import io
import socket
import struct
from PIL import Image
import matplotlib.pyplot as imshow
import numpy as np
import cv2
import time

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 8888))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
count =0
try:
    st_time = time.time()
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        start = time.time()
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        rec_time=time.time()
        if not image_len:
            print('0')
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        wrt_time=time.time()
        # image = Image.open(image_stream)
        # print('Image is %dx%d' % image.size)
        # image.verify()
        #plt.imshow(image)
        #image.show()
        #imshow(np.asarray(image))
        
        #print('Image is verified')
        print(count)
        count +=1
        array = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        cv2.imshow('Image', image)
        cvt_time=time.time()
        #cv2.imwrite("Image%d.jpeg"% count, image)
        #print(array)
        if cv2.waitKey(1) == ord('q'):
            break
        print("package :", count, rec_time - start, wrt_time - rec_time, cvt_time -wrt_time)
finally:
    connection.close()
    server_socket.close()