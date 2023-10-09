import io
import socket
import struct
from PIL import Image

# Create a socket to connect to the server
client_socket = socket.socket()
client_socket.connect(('10.8.0.9', 8000))
connection = client_socket.makefile('rb')

try:
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break

        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))

        # Rewind the stream, open it as an image with PIL and do some processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        # Process the image as needed (e.g., show, save, etc)
        image.show()
finally:
    connection.close()
    client_socket.close()