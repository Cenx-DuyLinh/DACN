import io
import picamera
import socket

# Create a socket object
server_socket = socket.socket()
server_socket.bind(('10.8.0.13', 8000))
server_socket.listen(0)

# Accept a single client connection
client_socket, address = server_socket.accept()

# Create a bytes-like object as a stream for the PiCamera
stream = io.BytesIO()

# Create a PiCamera object
camera = picamera.PiCamera()

# Set camera resolution (optional)
camera.resolution = (640, 480)

# Start the video capture
camera.start_recording(stream, format='h264')

try:
    while True:
        # Capture video frames continuously
        camera.wait_recording(0)

        # Send the current frame to the client
        client_socket.sendall(stream.getvalue())

        # Reset the stream for the next frame
        stream.seek(0)
        stream.truncate()

finally:
    # Clean up resources
    camera.stop_recording()
    client_socket.close()
    server_socket.close()