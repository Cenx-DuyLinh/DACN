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

        button_left = self.create_button("Left", 3)
        button_right = self.create_button("Right", 4)
        button_forward = self.create_button("Forward", 7)
        button_backward = self.create_button("Backward", 8)
        button_up = self.create_button("Up", 5)
        button_down = self.create_button("Down", 6)
        button_arm = self.create_button("Arm", 1)
        button_disarm = self.create_button("Disarm", 2)
        button_switch_to_guided = self.create_button("Switch to Guided",9)
        button_take_off = self.create_button("Take Off",10)

        buttons = [button_left, button_right, button_forward, button_backward, 
                   button_up, button_down, button_arm, button_disarm,button_switch_to_guided,button_take_off]
        
        for button in buttons:
            button.pack(side=tk.LEFT)

    def create_button(self, text, command):
        return tk.Button(self.window, text=text,
                         command=lambda: self.command_queue.put(command))

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
        9: SWITCH TO GUIDED
        10: TAKE OFF
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
    HOST = "127.0.0.1"
    # HOST = "10.8.0.62"
    PORT = 2000
    client = Client(HOST, PORT)
    client.run()