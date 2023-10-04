import cv2
import tkinter as tk
from PIL import Image, ImageTk
import socket

# Create a socket object and connect to the server
client_socket = socket.socket()
client_socket.connect(('10.8.0.13', 8000))

# Create a Tkinter window
window = tk.Tk()

# Create a Canvas widget to display the video feed
canvas = tk.Canvas(window, width=640, height=480)
canvas.pack()

# Display the video frames on the Tkinter window
def update_video():
    # Receive the video frame from the server
    frame = client_socket.recv(1024)

    # Check if the frame is empty
    if len(frame) == 0:
        return

    # Convert the received frame into an image
    image = Image.frombytes('RGB', (640, 480), frame)

    # Create a PhotoImage object to display the image on the Canvas widget
    photo = ImageTk.PhotoImage(image)

    # Update the image on the Canvas
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)

    # Repeat the update process after a delay (e.g., 30ms for 30fps)
    window.after(30, update_video)

# Start updating the video display
update_video()

# Start the Tkinter main loop
window.mainloop()