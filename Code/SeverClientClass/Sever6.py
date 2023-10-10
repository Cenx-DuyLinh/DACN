import socket
import threading
from queue import Queue
import time
import logging
from CopterAAVC.Class.MAVlink import MyMAVlink,ProgressStatus
import os
import io 
import struct
import picamera
class SplitFrames(object):
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

class Server:
    def __init__(self, host, port,port_cam,connection_object):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_log_file = current_dir + "\Log\SeverLog"
        logging.basicConfig(level=logging.DEBUG, filename=current_log_file, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
        date = time.localtime()
        logging.info(f"--------------------------[New Run File]--[{date.tm_mday}/{date.tm_mon}/{date.tm_year}]--[{date.tm_hour}:{date.tm_min}]-----------------------------")
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
    def print_and_write_log(self,data):
        print(data)
        logging.info(data)
    def setup_server(self):
        self.conn_server_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_pi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.conn_server_client.bind((self.host, self.port))
        self.conn_pi.bind((self.host, self.port_cam))

        self.conn_server_client.listen()
        self.conn_pi.listen()

        self.print_and_write_log("Listening for connections on server and camera...")
    def cam_pi(self):
        connection = self.conn_pi.accept()[0].makefile('wb')
        self.cam_pi_connected =True
        print("camPIconnect to client")
        try:
            output = SplitFrames(connection)
            with picamera.PiCamera(resolution='VGA', framerate=30) as camera:
                time.sleep(2)  # Give the camera time to initialize
                camera.start_recording(output, format='mjpeg')
                camera.wait_recording(6400)
                camera.stop_recording()
                # Write the terminating 0-length to the connection to let the
                # client know we're done
                connection.write(struct.pack('<L', 0))
        except KeyboardInterrupt:
            connection.close()
            self.conn_pi.close()
            print('Sent %d images' % output.count)
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
                    self.print_and_write_log("Drone connected\n")
            else:
                self.print_and_write_log("Failed to connect to the drone\n")

        except ConnectionRefusedError:
            self.print_and_write_log("Unable to establish a connection to the drone. Make sure it's running and accessible.\n")
    def receive_command_from_client(self):
        while True:
            self.client_conn, client_addr = self.conn_server_client.accept()
            self.client_connected = True
            self.print_and_write_log(f"Connected to client: {client_addr}")

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
                        self.print_and_write_log(f"Received: {message}, {command}")
                        response = "Command received"
                        self.client_conn.sendall(response.encode())

                else:
                    self.print_and_write_log("Drone connection failed, aborting client communication")
            except ConnectionResetError:
                self.print_and_write_log("Client connection reset by peer")
            finally:
                self.client_conn.close()
                self.client_connected = False
                self.print_and_write_log("Client disconnected, returning to listen for connections...")   
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
                    self.print_and_write_log(f"Command {command} got timeout \n--------------------------------")
                else :
                    self.print_and_write_log(f"The delay of command {command} to drone: {delay}s\n--------------------------------")
        if data == 2:
            start_time = time.perf_counter_ns()
            data,confirm = self.drone.get_ned_ack()
            if confirm:
                delay = (time.perf_counter_ns() - start_time)/2/1e9
                self.print_and_write_log(f"Status: {data} \nThe delay of command {command} to drone: {delay}\n--------------------------------")
            else :
                self.print_and_write_log(f"Command {command} got timeout \n--------------------------------")

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
            self.print_and_write_log(f"Executing command: {command}")
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
        thread_cam_pi.start()
        print("campi thread and recieve thread start")
        while not self.client_connected or not self.drone_connected or not self.cam_pi_connected:
        # while not self.client_connected or not self.drone_connected:
            print("sleeping")
            time.sleep(0.1)

        thread_send_to_drone.start()
        print("thread send drone start")

        thread_receive.join()
        thread_send_to_drone.join()
        thread_cam_pi.join()



