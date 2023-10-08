import cv2
import socket
import pickle
import struct
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue

# Server configuration
HOST = 'localhost'
PORT = 9999

class StreamClient:
    def __init__(self, host, port):
        self.queue = queue.Queue()
        self.host = host
        self.port = port

        # Create a Tkinter window
        self.root = tk.Tk()
        self.root.title("Webcam Stream")
        self.canvas = tk.Canvas(self.root, width=640, height=480)
        self.canvas.pack()

    def start(self):
        # Start video streaming thread
        video_thread = threading.Thread(target=self.receive_video)
        video_thread.start()
        show_video_thread = threading.Thread(target=self.show_video)
        show_video_thread.start()
        
        # Start Tkinter main loop
        self.root.mainloop()

    def show_video(self):
        while True:
            frame = self.queue.get()
            if frame is None:
                continue
            else:
                # Convert the frame to PIL Image format
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

                # Resize the image to fit the canvas
                image = image.resize((640, 480), Image.LANCZOS)

                # Update the Tkinter window with the current frame
                tk_image = ImageTk.PhotoImage(image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
                self.root.update()

    def receive_video(self):
        # Initialize client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.host, self.port))

        try:
            while True:
                # Receive the packed frame size and data
                data = b""
                while len(data) < struct.calcsize("Q"):
                    packet = client_socket.recv(4 * 1024)
                    print("package recieve from sever")
                    if not packet:
                        break
                    data += packet

                # Extract the frame size and data
                message_size = struct.unpack("Q", data[:8])[0]
                data = data[8:]
                while len(data) < message_size:
                    data += client_socket.recv(4 * 1024)

                # Extract the frame from the received data
                frame = pickle.loads(data)
                self.queue.put(frame)

        except KeyboardInterrupt:
            pass

        # Close gracefully
        client_socket.close()

# Create the StreamClient instance and start the streaming
client = StreamClient(HOST, PORT)
client.start()