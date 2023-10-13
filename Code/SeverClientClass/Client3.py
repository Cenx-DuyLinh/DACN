import socket, threading, time, logging, os, io,struct
import tkinter as tk
import queue
from PIL import Image, ImageTk
class LimitedQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)
        self.maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        if self.full():
            self.get()  # Remove the oldest item when the queue is full
        super().put(item, block, timeout)
class Client:
    def __init__(self, host, port,port_pi):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_log_file = current_dir + "\Log\ClientLog"
        logging.basicConfig(level=logging.DEBUG, filename=current_log_file, filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
        date = time.localtime()
        logging.info(f"--------------------------[New Run File]--[{date.tm_mday}/{date.tm_mon}/{date.tm_year}]--[{date.tm_hour}:{date.tm_min}]-----------------------------")
        self.host = host
        self.port = port
        self.port_pi = port_pi
        self.queue_command = queue.Queue()
        self.queue_camera = LimitedQueue(maxsize=5)
        self.connected_to_sever = False
        self.conn_pi_obj = None
        self.setup_ui()
        self.connect_to_sever()
        self.count = 0
        self.image_counter = 0

    def setup_ui(self):
        self.window = tk.Tk()
        self.window.title("Client")

        self.frame_button = tk.Frame(master=self.window)
        self.frame_button.pack()
        self.frame_cam = tk.Frame(master=self.window,width=640,height=480)
        self.frame_cam.pack(side="bottom")

        self.canvas = tk.Canvas(master=self.frame_cam,width=640,height=480)
        self.canvas.pack()

        button_left = self.create_button("Left", 3)
        button_right = self.create_button("Right", 4)
        button_forward = self.create_button("Forward", 7)
        button_backward = self.create_button("Backward", 8)
        button_up = self.create_button("Up", 5)
        button_down = self.create_button("Down", 6)
        button_arm = self.create_button("Arm", 1)
        button_disarm = self.create_button("Disarm", 2)
        button_switch_to_guided = self.create_button("Switch to Guided",9)
        button_switch_to_auto = self.create_button("Switch to Auto",11)
        button_take_off = self.create_button("Take Off",10)
        button_stop = self.create_button("Stop",12)

        buttons = [button_left, button_right, button_forward, button_backward, 
                   button_up, button_down,button_stop, button_arm, button_disarm,button_switch_to_guided,button_switch_to_auto,button_take_off]
        
        for button in buttons:
            button.pack(side=tk.LEFT)

    def create_button(self, text, command):
        return tk.Button(self.frame_button, text=text,width=15,height=3,
                         command=lambda: self.queue_command.put(command))
    def print_and_write_log(self,data):
            print(data)
            logging.info(data)
    def connect_to_sever(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
        self.print_and_write_log("Connected to Sever")

        self.conn_pi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn_pi.connect((self.host, self.port_pi))
        self.conn_pi_obj = self.conn_pi.makefile('rb')
        self.print_and_write_log("Connected to Camera")
        
        self.connected_to_sever = True
    def get_image_from_sever(self):
        # print("thread get is running")
        while True:
            image_len = struct.unpack('<L', self.conn_pi_obj.read(struct.calcsize('<L')))[0]
            self.image_counter += 1
            # print(f"recieve image number {self.image_counter}, delay: {end - start}")
            if not image_len:
                break
            # Construct a stream to hold the image data and read the image
            # data from the connection
            image_stream = io.BytesIO()
            image_stream.write(self.conn_pi_obj.read(image_len))
            # Rewind the stream, open it as an image with PIL and do some
            # processing on it
            image_stream.seek(0)
            image = Image.open(image_stream)
            
            self.queue_camera.put(image)
            time.sleep(0.01)
    def update_camera(self):
        img = self.queue_camera.get()
        if img is None:
            return
        else:
            start = time.time()
            imgtk = ImageTk.PhotoImage(image=img)
            end = time.time()
            # Clear the existing image from the Canvas
            self.canvas.delete("all")
            
            # Create a new image item on the Canvas
            self.canvas.image = imgtk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)
            # print(f"tk time {end - start}")
            self.count += 1
            print(f'cam updated {self.count}')
            self.canvas.after(100,self.update_camera)
        

    def send_message(self):
        while True:
            if not self.queue_command.empty():
                command = self.queue_command.get()
                message = f"Command from client\n{command}"
                self.conn.sendall(message.encode())

                time_send = time.perf_counter_ns()
                # print("Sent:", message)

                response = self.conn.recv(100)
                time_recv = time.perf_counter_ns()

                delay = ((time_recv - time_send) / 2) / 1e9
                message = response.decode()
                self.print_and_write_log(f"Received: {message}")
                self.print_and_write_log(f"Delay: {delay}s\n--------------------------------")

    def start_thread(self):
        thread_send_message = threading.Thread(target=self.send_message, daemon=True)
        thread_get_image = threading.Thread(target=self.get_image_from_sever, daemon=True)
        
        thread_send_message.start()
        thread_get_image.start()

    def run(self):
        self.start_thread()
        self.update_camera()
        self.window.mainloop()