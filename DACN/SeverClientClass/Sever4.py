import socket
import threading
from queue import Queue
import time
from CopterAAVC.Class.MAVlink import MyMAVlink,ProgressStatus


class Server:
    def __init__(self, host, port,connection_object):
        self.drone_connection_string = connection_object
        self.host = host
        self.port = port
        self.drone_queue = Queue
        self.drone_baudrate = 921600
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
        try:
            self.drone = MyMAVlink(
                connection_string=self.drone_connection_string,
                baudrate=self.drone_baudrate,
                queue=self.drone_queue
            )

            if self.drone.connection_status == ProgressStatus.OK:
                    self.drone_connected = True
                    print("Drone connected\n")
            else:
                print("Failed to connect to the drone\n")

        except ConnectionRefusedError:
            print("Unable to establish a connection to the drone. Make sure it's running and accessible.\n")

    def receive_and_respond_back_to_client(self):
        while True:
            self.client_conn, client_addr = self.conn.accept()
            self.client_connected = True
            print("Connected to client:", client_addr)

            drone_connection_thread = threading.Thread(target=self.connect_to_drone)
            drone_connection_thread.start()

            try:
                drone_connection_thread.join(5)  # Wait for 5 seconds for the thread to complete
                if self.drone_connected:
                    while True:
                        data = self.client_conn.recv(100)
                        if not data:
                            break

                        message, command = data.decode().split("\n")
                        self.command_queue.put(command)
                        print(f"Received: {message}, {command}")
                        response = "Command received"
                        self.client_conn.sendall(response.encode())

                else:
                    print("Drone connection failed, aborting client communication")
            except ConnectionResetError:
                print("Client connection reset by peer")
            finally:
                self.client_conn.close()
                self.client_connected = False
                print("Client disconnected, returning to listen for connections...")
    
    def send_to_drone(self):
        """
        Args: 
        1: ARM
        2: DISARM
        3: LEFT
        4: RIGHT
        5: UP
        6: DOWN
        7: FORWARD
        8: BACKWARD
        9: SWITCH TO GUIDED
        10: TAKE OFF
        """
        while True:
            command = self.command_queue.get()
            print(f"Executing command: {command}")
            self.distant_to_move = 10 
            if command == "1":
                self.drone.arm_disarm(1)
                start_time = time.perf_counter_ns()
                data = self.drone.command_acknowledge()
                
                if data:
                    delay = (time.perf_counter_ns() - start_time)/2/1e9
                    print(f"The delay of command {command} to drone: {delay}")
            elif command == "2":
                self.drone.arm_disarm(0)
                start_time = time.perf_counter_ns()
                data = self.drone.command_acknowledge()
                
                if data:
                    delay = (time.perf_counter_ns() - start_time)/2/1e9
                    print(f"The delay of command {command} to drone: {delay}")
            elif command == "3":
                self.drone.set_frame_position([0, -self.distant_to_move, 0])
            elif command == "4":
                self.drone.set_frame_position([0,self.distant_to_move,0])
            elif command == "5":
                self.drone.set_frame_position([0,0,-self.distant_to_move])
            elif command == "6":
                self.drone.set_frame_position([0,0,self.distant_to_move])
            elif command == "7":
                self.drone.set_frame_position([self.distant_to_move,0,0])
            elif command == "8":
                self.drone.set_frame_position([-self.distant_to_move,0,0])
            elif command == "9":
                self.drone.set_mode(4)
                start_time = time.perf_counter_ns()
                data = self.drone.command_acknowledge()
                
                if data:
                    delay = (time.perf_counter_ns() - start_time)/2/1e9
                    print(f"The delay of command {command} to drone: {delay}")
            elif command == "10":
                self.drone.take_off(10)
                start_time = time.perf_counter_ns()
                data = self.drone.command_acknowledge()
                
                if data:
                    delay = (time.perf_counter_ns() - start_time)/2/1e9
                    print(f"The delay of command {command} to drone: {delay}")
        
            time.sleep(0.01)
            # Perform command execution or call another function here if needed
            # Do some processing or call another function here if needed
    def command_acknowledge(self):
        pass
    def run(self):
        thread_receive = threading.Thread(
            target=self.receive_and_respond_back_to_client, daemon=True
        )
        thread_send_to_drone = threading.Thread(target=self.send_to_drone, daemon=True)
        thread_command_acknowledge = threading.Thread(target=self.command_acknowledge, daemon=True)

        thread_receive.start()
        while not self.client_connected or not self.drone_connected:
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

