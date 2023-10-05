import io
import socket
import struct
import threading
from PIL import ImageTk, Image
import tkinter as tk

# Create a Tkinter window
window = tk.Tk()

# Create a Tkinter label widget
label = tk.Label(window)
label.pack()

# Create a variable to keep track of the image being displayed
current_image = None

# Function to continuously update the image in the Tkinter window
def update_image():
    global current_image

    server_socket = socket.socket()
    server_socket.bind(('10.8.0.13', 8000))
    server_socket.listen(0)
    print("Listening on")

# Accept a single connection and make a file-like object out of it
    connection = server_socket.accept()[0].makefile('rb')

    try:
        while True:
            # Read the length of the image as a 32-bit unsigned int. If the length is zero, quit the loop
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break

            # Construct a stream to hold the image data and read the image data from the connection
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))

            # Rewind the stream, open it as an image with PIL and do some processing on it
            image_stream.seek(0)
            image = Image.open(image_stream).convert('RGB')
            print('Image is %dx%d' % image.size)
            image.verify()
            print('Image is verified')

            # Create a Tkinter image object
            image_tk = ImageTk.PhotoImage(image)

            # Update the image on the label widget
            label.configure(image=image_tk)
            label.image = image_tk

            # Set the current image to the newly displayed image
            current_image = image_tk

            # Display the image in the Tkinter window
            window.update()

    finally:
        connection.close()

# Start a new thread for image streaming
thread = threading.Thread(target=update_image)
thread.start()

# Start Tkinter event loop
window.mainloop()