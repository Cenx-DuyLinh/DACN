import socket
import tkinter as tk
import threading
import time
from queue import Queue

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.command_queue = Queue()
        self.setup_ui()
        self.connect()

    def setup_ui(self):
        self.window = tk.Tk()
        self.window.title("Client")

        button_left = tk.Button(self.window, text="Left", command= lambda:self.command_queue.put(3))
        button_right = tk.Button(self.window, text="Right", command= lambda:self.command_queue.put(4))
        button_forward = tk.Button(self.window, text="Forward", command= lambda:self.command_queue.put(7))
        button_backward = tk.Button(self.window, text="Backward", command= lambda:self.command_queue.put(8))
        button_up = tk.Button(self.window, text="Up", command= lambda:self.command_queue.put(5))
        button_down = tk.Button(self.window, text="Down", command= lambda:self.command_queue.put(6))
        button_arm = tk.Button(self.window, text="Arm", command= lambda:self.command_queue.put(1))
        button_disarm = tk.Button(self.window, text="Disarm",command=lambda:self.command_queue.put(2))

        button_left.pack(side=tk.LEFT)
        button_right.pack(side=tk.LEFT)
        button_forward.pack(side=tk.LEFT)
        button_backward.pack(side=tk.LEFT)
        button_up.pack(side=tk.LEFT)
        button_down.pack(side=tk.LEFT)
        button_arm.pack(side=tk.LEFT)
        button_disarm.pack(side=tk.LEFT)

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
        print("Connected")

    def send_message(self):
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
        """
        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                message = f"Command from client\n{command}"
                self.conn.sendall(message.encode())
                time_send = time.perf_counter_ns()
                print("Sent:", message)
                response = self.conn.recv(100)
                time_recv = time.perf_counter_ns()
                delay = ((time_recv - time_send) / 2) / 1e9
                message = response.decode()
                print(f"Received: {message}, Delay: {delay} s")

    def start_sending_thread(self):
        thread_send_message = threading.Thread(target=self.send_message, daemon=True)
        thread_send_message.start()

    def run(self):
        self.start_sending_thread()
        self.window.mainloop()


if __name__ == "__main__":
    # HOST = "127.0.0.1"
    HOST = "10.8.0.62"
    PORT = 2000
    client = Client(HOST, PORT)
    client.run()


