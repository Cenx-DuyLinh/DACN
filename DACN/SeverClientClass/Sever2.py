import socket
import threading
from queue import Queue
import time
from CopterAAVC.Class.MAVlink import MyMAVlink,ProgressStatus


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.drone_queue = Queue
        self.drone_connection_string = "tcp:127.0.0.1:5762"
        # self.drone_connection_string = "COM10"
        self.drone_baudrate = 9600
        self.client_connected = False
        self.drone_connected = False
        self.command_queue = Queue()
        self.setup_server()

    def setup_server(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((self.host, self.port))
        self.conn.listen()
        print("Listening for connections...")

    def receive_and_respond_back_to_sever(self):
        client_conn, client_addr = self.conn.accept()
        self.client_connected = True
        print("Connected to client:", client_addr)
        self.drone = MyMAVlink(connection_string= self.drone_connection_string, baudrate= self.drone_baudrate, queue= self.drone_queue)
        while True:
            if self.drone.connection_status == ProgressStatus.OK:
                self.drone_connected = True
                print("Drone connected")
                break
            print("Connecting to drone\n")
            time.sleep(0.2)
        while True:
            data = client_conn.recv(8192)
            if not data:
                break
            message, command = data.decode().split("\n")
            print(type(command))
            self.command_queue.put(command)
            print(f"Received: {message}, {command}")
            response = "Command recieved"
            client_conn.sendall(response.encode())
        client_conn.close()
    
    def send_to_drone(self):
        """
        Args: 
        1: ARM
        2: DISARM
        """
        while True:
            command = self.command_queue.get()
            if self.command_queue.empty():
                continue
            print(f"Executing command: {command}")
            if command == "1":
                self.drone.arm_disarm(1)
            elif command == "2":
                self.drone.arm_disarm(0)
            # Perform command execution or call another function here if needed
            # Do some processing or call another function here if needed
    def command_acknowledge(self):
        pass
    def run(self):
        thread_receive = threading.Thread(
            target=self.receive_and_respond_back_to_sever, daemon=True
        )
        thread_send_to_drone = threading.Thread(target=self.send_to_drone, daemon=True)
        thread_command_acknowledge = threading.Thread(target=self.command_acknowledge, daemon=True)

        thread_receive.start()
        while not self.client_connected and not self.drone_connected:
            time.sleep(0.1)
        thread_command_acknowledge.start()
        thread_send_to_drone.start()

        thread_receive.join()
        thread_send_to_drone.join()
        thread_command_acknowledge.join()

if __name__ == "__main__":
    HOST = "127.0.0.1"
    # HOST = "10.8.0.13"
    PORT = 2000
    server = Server(HOST, PORT)
    server.run()

