import socket
import threading
from queue import Queue
import time
from CopterAAVC.Class.MAVlink import MyMAVlink, ProgressStatus


class Server:
    def __init__(self, host, port, connection_object):
        self.drone_connection_string = connection_object
        self.host = host
        self.port = port
        self.drone_queue = Queue()
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

    def connect_to_drone(self):
        while not self.drone_connected:
            if self.drone.connection_status == ProgressStatus.OK:
                self.drone_connected = True
                print("Drone connected")
            else:
                print("Connecting to drone...")
                time.sleep(0.2) 

    def receive_and_respond(self):
        self.client_conn, client_addr = self.conn.accept()
        self.client_connected = True
        print("Connected to client:", client_addr)
        self.drone = MyMAVlink(connection_string=self.drone_connection_string, baudrate=self.drone_baudrate, queue=self.drone_queue)
        self.connect_to_drone()

        while True:
            data = self.client_conn.recv(100)
            if not data:
                break

            message, command = data.decode().split("\n")
            self.command_queue.put(command)
            print(f"Received: {message}, {command}")
            response = "Command received"
            self.client_conn.sendall(response.encode())

        self.client_conn.close()

    def execute_command(self, command, pos):
        start_time = time.perf_counter_ns()
        data = None
        if command == "1":
            self.drone.arm_disarm(1)
            data = self.drone.command_acknowledge()
        elif command == "2":
            self.drone.arm_disarm(2)
            data = self.drone.command_acknowledge()
        elif pos is not None:
            self.drone.set_frame_position(pos)
            data = self.drone.command_acknowledge()

        if data:
            delay = (time.perf_counter_ns() - start_time) / 2 / 1e9
            print(f"The delay of command {command} to drone: {delay}")
    def send_commands_to_drone(self):
        while True:
            command = self.command_queue.get()
            print(f"Executing command: {command}")
            self.distant_to_move = 2

            if command == "1":
                self.drone.arm_disarm(1)
                self.execute_command(command, None)
            elif command == "2":
                self.drone.arm_disarm(2)
                self.execute_command(command, None)
            elif command in ["3", "4", "5", "6", "7", "8"]:
                pos = self.get_position_to_move(command)
                self.execute_command(command, pos)
            elif command == "9":
                self.drone.set_mode(4)
                self.execute_command(command, None)
            elif command == "10":
                self.drone.take_off(10)
                self.execute_command(command, None)

    def get_position_to_move(self, command):
        pos_dict = {
            "3": [0, -self.distant_to_move, 0],
            "4": [0, self.distant_to_move, 0],
            "5": [0, 0, self.distant_to_move],
            "6": [0, 0, -self.distant_to_move],
            "7": [self.distant_to_move, 0, 0],
            "8": [-self.distant_to_move, 0, 0]
        }
        return pos_dict.get(command)

    def run(self):
        thread_receive = threading.Thread(
            target=self.receive_and_respond, daemon=True
        )
        thread_send_to_drone = threading.Thread(target=self.send_commands_to_drone, daemon=True)

        thread_receive.start()
        while not (self.client_connected and self.drone_connected):
            time.sleep(0.1)
        thread_send_to_drone.start()

        thread_receive.join()
        thread_send_to_drone.join()


if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 2000
    drone_connection_string = "your_connection_string"
    server = Server(HOST, PORT, drone_connection_string)
    server.run()