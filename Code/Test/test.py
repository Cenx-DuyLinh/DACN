import cv2
import socket
import struct
import pickle
import time

# Server configuration
HOST = 'localhost'
PORT = 9999

# Initialize server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Accept a client connection
client_socket, addr = server_socket.accept()
print("Client connected:", addr)

# Open webcam
capture = cv2.VideoCapture(0)

# Set video properties
capture.set(3, 640)  # Width
capture.set(4, 480)  # Height

while True:
    try:
        # Read frame from webcam
        ret, frame = capture.read()
        frame = cv2.flip(frame, 1)  # Flip frame horizontally for mirror effect

        # Serialize the frame
        data = pickle.dumps(frame)

        # Pack the frame size and data
        message = struct.pack("Q", len(data)) + data

        # Send the frame to the client
        client_socket.sendall(message)
        time.sleep(0.33)
    except KeyboardInterrupt:
        break

# Release resources
client_socket.close()
server_socket.close()
capture.release()
cv2.destroyAllWindows()