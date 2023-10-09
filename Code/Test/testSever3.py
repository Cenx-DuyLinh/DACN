import io
import socket
import struct
import PIL
from PIL import Image,ImageTk
import tkinter as tk
import queue
import threading
import time
#!-------[THIS CODE RUN ON UR PC]----------------------------------------------------------------
# Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
# all interfaces)
server_socket = socket.socket()
server_socket.bind(('10.8.0.13', 8000))
server_socket.listen(0)
print("Listening")
#----------------------------------------------------------------
window = tk.Tk()
canvas = tk.Canvas(window, width=640, height=480)
canvas.pack()
#----------------------------------------------------------------
# Accept a single connection and make a file-like object out of it
my_queue = queue.Queue()
connection = server_socket.accept()[0].makefile('rb')
def get_frame_from_sever():
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
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        my_queue.put(image)
    
def update_to_canvas():
    while True:
        if not my_queue.empty():
            image = my_queue.get()
            # Resize the image to fit the canvas
            # resized_image = image.resize((640, 480))
            # Convert the image to Tkinter-compatible format
            tk_image = ImageTk.PhotoImage(image)
            # Update the canvas with the new image
            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            # Keep a reference to the image to prevent it from being garbage collected
            canvas.image = tk_image
            window.update()
            print("Image updated")
            time.sleep(0.001)

def run_threads():
    # Start the thread to receive frames from the server
    receive_thread = threading.Thread(target=get_frame_from_sever)
    update_thread = threading.Thread(target=update_to_canvas)
    receive_thread.start()
    update_thread.start()
    # Start the Tkinter event loop
    window.mainloop()

run_threads()