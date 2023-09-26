import socket
import threading
from queue import Queue
import time
from MAVlinkClass.MAVlink import *


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.counter = 0
        self.command_queue = Queue()
        self.setup_server()

    def setup_server(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen()
        print("Listening for connections...")

    def receive_and_respond_back_to_sever(self):
        client_conn, client_addr = self.conn.accept()
        print("Connected to client:", client_addr)
        while True:
            data = client_conn.recv(8192)
            if not data:
                break
            message, command = data.decode().split("\n")
            self.counter = self.counter + 1
            self.command_queue.put(command)
            print(f"Received: {message}, {self.counter}")
            response = "Hello from server"
            client_conn.sendall(response.encode())
        client_conn.close()
    
    def send_to_drone(self):
        while True:
            command = self.command_queue.get()
            if self.command_queue.empty():
                continue
            print(f"Executing command: {command}")
            time.sleep(1)
            # Perform command execution or call another function here if needed
            # Do some processing or call another function here if needed

    def run(self):
        thread_receive = threading.Thread(
            target=self.receive_and_respond_back_to_sever, daemon=True
        )
        thread_send_to_drone = threading.Thread(target=self.send_to_drone, daemon=True)

        thread_receive.start()
        thread_send_to_drone.start()

        thread_receive.join()
        thread_print.join()



