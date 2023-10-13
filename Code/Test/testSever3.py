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
class LimitedQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)
        self.maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        if self.full():
            self.get()  # Remove the oldest item when the queue is full
        super().put(item, block, timeout)
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
my_queue = LimitedQueue(maxsize=10)
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
    img = my_queue.get()
    if img is None: 
        pass
    else: 
        start = time.time()
        imgtk = ImageTk.PhotoImage(image=img)
        end = time.time()
        # Clear the existing image from the Canvas
        canvas.delete("all")
        
        # Create a new image item on the Canvas
        canvas.image = imgtk
        canvas.create_image(0, 0, anchor=tk.NW, image=canvas.image)
        print(f"tk time {end - start}")
        canvas.after(1,update_to_canvas)

def run_threads():
    # Start the thread to receive frames from the server
    receive_thread = threading.Thread(target=get_frame_from_sever)
    receive_thread.start()
    # Start the Tkinter event loop
    update_to_canvas()
    window.mainloop()

run_threads()