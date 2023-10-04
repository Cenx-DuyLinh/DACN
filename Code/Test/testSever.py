# import io
# import socket
# import struct
# from PIL import Image

# # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# # all interfaces)
# server_socket = socket.socket()
# server_socket.bind(('10.8.0.13', 8000))
# server_socket.listen(0)
# print("listening on")

# # Accept a single connection and make a file-like object out of it
# connection = server_socket.accept()[0].makefile('rb')
# try:
#     while True:
#         # Read the length of the image as a 32-bit unsigned int. If the
#         # length is zero, quit the loop
#         image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
#         if not image_len:
#             break
#         # Construct a stream to hold the image data and read the image
#         # data from the connection
#         image_stream = io.BytesIO()
#         image_stream.write(connection.read(image_len))
#         # Rewind the stream, open it as an image with PIL and do some
#         # processing on it
#         image_stream.seek(0)
#         image = Image.open(image_stream)
#         print('Image is %dx%d' % image.size)
#         image.verify()
#         print('Image is verified')
# finally:
#     connection.close()
#     server_socket.close()
import io
import socket
import struct
from PIL import Image
import tkinter as tk
from PIL import ImageTk

# Create a Tkinter window
window = tk.Tk()

# Create a Canvas widget to display the image
canvas = tk.Canvas(window, width=640, height=480)
canvas.pack()

# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means all interfaces)
server_socket = socket.socket()
server_socket.bind(('10.8.0.13', 8000))
server_socket.listen(0)
print("Listening on")

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')

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

        # Rewind the stream, open it as an image with PIL, and convert to PhotoImage
        image_stream.seek(0)
        image = Image.open(image_stream)
        photo = ImageTk.PhotoImage(image)

        # Update the image on the Canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        window.update_idletasks()  # Update the Tkinter window

finally:
    connection.close()
    server_socket.close()

# Start the Tkinter main loop
window.mainloop()