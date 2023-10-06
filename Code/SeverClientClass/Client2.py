import socket
import tkinter as tk
import threading
import time
import logging
from queue import Queue


class Client:
    def __init__(self, host, port):
        logging.basicConfig(level=logging.DEBUG, filename="Log/ClientLog", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
        date = time.localtime()
        logging.info(f"--------------------------[New Run File]--[{date.tm_mday}/{date.tm_mon}/{date.tm_year}]--[{date.tm_hour}:{date.tm_min}]-----------------------------")
        self.host = host
        self.port = port
        self.command_queue = Queue()
        self.setup_ui()
        self.connect_to_sever()

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
        button_switch_to_auto = self.create_button("Switch to Auto",11)
        button_take_off = self.create_button("Take Off",10)
        button_stop = self.create_button("Stop",12)

        buttons = [button_left, button_right, button_forward, button_backward, 
                   button_up, button_down,button_stop, button_arm, button_disarm,button_switch_to_guided,button_switch_to_auto,button_take_off]
        
        for button in buttons:
            button.pack(side=tk.LEFT)

    def create_button(self, text, command):
        return tk.Button(self.window, text=text,width=15,height=3,
                         command=lambda: self.command_queue.put(command))
    def print_and_write_log(self,data):
            print(data)
            logging.info(data)
    def connect_to_sever(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
        self.print_and_write_log("Connected")

    def send_message(self):
        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get()
                message = f"Command from client\n{command}"
                self.conn.sendall(message.encode())

                time_send = time.perf_counter_ns()
                # print("Sent:", message)

                response = self.conn.recv(100)
                time_recv = time.perf_counter_ns()

                delay = ((time_recv - time_send) / 2) / 1e9
                message = response.decode()
                self.print_and_write_log(f"Received: {message}\nDelay: {delay}s\n--------------------------------")

    def start_sending_thread(self):
        thread_send_message = threading.Thread(target=self.send_message, daemon=True)
        thread_send_message.start()

    def run(self):
        self.start_sending_thread()
        self.window.mainloop()


