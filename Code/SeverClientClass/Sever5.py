import socket
import threading
from queue import Queue
import time
from CopterAAVC.Class.MAVlink import MyMAVlink,ProgressStatus


class Server:
    def __init__(self, host, port,port_cam,connection_object):
        self.drone_connection_string = connection_object
        self.host = host
        self.port = port
        self.port_cam = port_cam
        self.drone_queue = Queue
        self.drone_baudrate = 921600
        self.client_connected = False
        self.drone_connected = False
        self.cam_pi_connected = False
        self.command_queue = Queue()
        self.setup_server()

    def setup_server(self):
        self.conn_server_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_pi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn_server_client.bind((self.host, self.port))
        self.conn_pi.bind((self.host, self.port_cam))

        self.conn_server_client.listen()
        self.conn_pi.listen()

        print("Listening for connections on server and camera...")
    def cam_pi(self):
        pass  
    def stream_to_client(self,frame):
        pass
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
    def receive_command_from_client(self):
        while True:
            self.client_conn, client_addr = self.conn_server_client.accept()
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
    def calculate_delay(self,command,data):
        """Data Args:
        01: CMD_ACK
        02: NED_ACK
        """
        if data == 1:
            start_time = time.perf_counter_ns()
            confirm = self.drone.command_acknowledge()
            if confirm:
                delay = (time.perf_counter_ns() - start_time)/2/1e9
                if delay > 1: 
                    print (f"Command {command} got timeout \n--------------------------------")
                else :
                    print(f"The delay of command {command} to drone: {delay}\n--------------------------------")
        if data == 2:
            start_time = time.perf_counter_ns()
            data,confirm = self.drone.get_ned_ack()
            if confirm:
                delay = (time.perf_counter_ns() - start_time)/2/1e9
                print (f"Status: {data} \nThe delay of command {command} to drone: {delay}\n--------------------------------")
            else :
                print(f"Command {command} got timeout \n--------------------------------")

        pass
    def send_to_drone(self):
        """
        Args: 
        01: ARM        11: AUTO 
        02: DISARM     12: STOP
        03: LEFT
        04: RIGHT
        05: UP
        06: DOWN
        07: FORWARD
        08: BACKWARD
        09: GUIDED
        10: TAKE OFF
        
        """
        while True:
            command = self.command_queue.get()
            print(f"Executing command: {command}")
            self.distant_to_move = 3
            if command == "1":
                self.drone.arm_disarm(1)
                self.calculate_delay("1",1)
            elif command == "2":
                self.drone.arm_disarm(0)
                self.calculate_delay("2",1)
            elif command == "3":
                self.drone.set_frame_position([0, -self.distant_to_move, 0])
                self.calculate_delay("3",2)
            elif command == "4":
                self.drone.set_frame_position([0,self.distant_to_move,0])
                self.calculate_delay("4",2)
            elif command == "5":
                self.drone.set_frame_position([0,0,-self.distant_to_move])
                self.calculate_delay("5",2)
            elif command == "6":
                self.drone.set_frame_position([0,0,self.distant_to_move])
                self.calculate_delay("6",2)
            elif command == "7":
                self.drone.set_frame_position([self.distant_to_move,0,0])
                self.calculate_delay("7",2)
            elif command == "8":
                self.drone.set_frame_position([-self.distant_to_move,0,0])
                self.calculate_delay("8",2)
            elif command == "12":
                self.drone.set_frame_position([0,0,0])
                self.calculate_delay("12",2)
            elif command == "9":
                self.drone.set_mode(4)
                self.calculate_delay("9",1)
            elif command == "10":
                self.drone.take_off(self.distant_to_move)
                self.calculate_delay("10",1)
    
            
    def run(self):
        thread_receive = threading.Thread(target=self.receive_command_from_client, daemon=True)
        thread_send_to_drone = threading.Thread(target=self.send_to_drone, daemon=True)
        thread_cam_pi = threading.Thread(target=self.cam_pi, daemon=True)

        thread_receive.start()

        # while not self.client_connected or not self.drone_connected or not self.cam_pi_connected:
        while not self.client_connected or not self.drone_connected:
            time.sleep(0.1)

        thread_send_to_drone.start()

        thread_receive.join()
        thread_send_to_drone.join()
        thread_cam_pi.join()



