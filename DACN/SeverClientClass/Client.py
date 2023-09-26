import socket
import tkinter as tk
import threading
import time


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.setup_ui()
        self.connect()

    def setup_ui(self):
        self.window = tk.Tk()
        self.window.title("Client")
        self.button = tk.Button(self.window, text="SEND", command=self.send_message)
        self.button.pack()

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))
        print("Connected")

    def send_message(self):
        message = "Hello from client\n 1"
        self.conn.sendall(message.encode())
        time_send = time.perf_counter_ns()
        print("Sent:", message)
        response = self.conn.recv(8192)
        time_recv = time.perf_counter_ns()
        delay = ((time_recv - time_send) / 2) / 10**9
        message = response.decode()
        print(f"Received: {message}, Delay: {delay} s")

    def run(self):
        self.window.mainloop()



