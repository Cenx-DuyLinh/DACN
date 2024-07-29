# Tóm tắt

---

Sơ đồ set up dành cho Sever và Client:
![](https://i.imgur.com/9NOvmXP.png)

- **Sever:** raspberry pi ở trên drone
- **Client:** một máy tính bên ngoài kết nối vô sever
- **IP của Sever:** 10.8.0.9 (IP này là của OpenVPN)

Client sẽ kết nối vô Sever thông qua hai port 2000 và 5000 (2 port này hiện chỉ đang lấy ngẫu nhiên 2 số)

- **Port 2000:** gửi điều khiển cho drone
- **Port 5000:** gửi hình ảnh từ drone về ground control station

# Quá trình chạy file

---

![](https://i.imgur.com/DViZrAv.png)

- Client: chạy file **mainClient.py** (Class của file này là từ file SeverClientClass/Client3.py)
- Sever: chạy file **mainSever.py** (Class của file này là từ file SeverClientClass/Sever6.py)

# Class Client

---

Trên class client sẽ có 3 thread chính chạy song song, ba thread này được khởi tạo ở trong self.run() và self.start_thread()

```python
def start_thread(self):
        thread_send_message = threading.Thread(target=self.send_message, daemon=True)
        thread_get_image= threading.Thread(target=self.get_image_from_sever,daemon=True)

        thread_send_message.start()
        thread_get_image.start()

    def run(self):
        self.start_thread()
        self.update_camera()
        self.window.mainloop()
```

### 1. Thread send_message()

```python
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
            time.sleep(0.1)
```

Khi một nút được nhấn ở trên app tkinter, một số từ 1 đến 12 sẽ được cho vào self.queue_command:

```python
def create_button(self, text, command):
        return tk.Button(self.frame_button, text=text,width=15,height=3,command=lambda: self.queue_command.put(command))
```

Thread send_message này sẽ liên tục đợi số đó từ self.queue_command để lấy ra và gửi qua cho sever. Sau khi gửi lệnh, thread này sẽ đợi response từ Sever để có thể tính độ trễ từ Client sang Sever

Độ trễ được tính bằng phương pháp round-trip time (RTT)
![](https://i.imgur.com/vNQfUHG.png)

### 2. Thread get_img_from_sever()

```python
def get_image_from_sever(self):
        # print("thread get is running")
        while True:
            image_len = struct.unpack('<L',self.conn_pi_obj.read(struct.calcsize('<L')))[0]
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
```

Thread này sẽ nhận dữ liệu ảnh từ Sever gửi qua, unpact nó và bỏ dữ liệu ảnh vào trong queue, về chi tiết hơn có thể đọc tại link này: https://picamera.readthedocs.io/en/latest/recipes2.html#rapid-capture-and-streaming

> **Lưu ý:** Ở link trên họ đảo ngược vị trí của Sever và Client. Sever là máy tính ở GCS và Client sẽ là
> raspberry pi

Queue này là queue được giới hạn lại max size để tránh trường hợp ảnh trên app không update kịp theo tốc độ ảnh bỏ vào trong queue
![](https://i.imgur.com/MTuqW2T.png)

### 3. Thead update_camera()

Đây là thread sẽ update ảnh gửi về từ sever lên trên app

Thread này không chạy bằng Threading nhưng mà chạy bằng chức năng .after() của tkinter với các args là after(time in ms, function to run)

```python
def update_camera(self):
        img = self.queue_camera.get()
        if img is None:
            return
        else:
            start = time.time()
            imgtk = ImageTk.PhotoImage(image=img)
            # Clear the existing image from the Canvas
            self.canvas.delete("all")

            # Create a new image item on the Canvas
            self.canvas.image = imgtk
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.canvas.image)
            # print(f"tk time {end - start}")
            self.count += 1
            end = time.time()
            print(f'cam updated {self.count}    time:{end - start}')
            self.canvas.after(10,self.update_camera)
```

Thread này chỉ cần gọi một lần trước khi chạy window.mainloop()

# Class Sever

---

Trên class client sẽ có 3 thread chính chạy song song, ba thread này được khởi tạo ở trong self.run()

```python
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
```

Đầu tiên 2 thread thread_recieve và thread_cam_pi sẽ chạy trước để kết nối với drone và camera, sau khi thỏa 3 điều kiện là:

- Đã kết nối với sever
- Đã kết nối với camera
- Đã kết nối với drone
  Thì sẽ bắt đầu thread cuối là thead_send_to_drone để có thể gửi MAVLink qua cho drone

### 1. Thread recieve_command_from_client()

Công dụng của thread này đó là:

- Kết nối với client
- Kết nối với drone
- Nhận tin nhắn từ client, decode và bỏ thông tin đó vào trong self.command_queue
- Gửi tin nhắn confirm lại cho client

```python
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
```

Thread này đồng thời cũng chạy một thread nhỏ là self.connect_to_drone() để kết nối với drone.

```python
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
```

### 2. Thread cam_pi()

Công dụng của thread này:

- Kết nối với client
- Gửi hình ảnh qua port 5000 của client

```python
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
```

> Note: Do trong giai đoạn thử nghiệm nên phần camera.wait_recording chỉ dừng lại ở 6400 giây, có thể để số lớn hơn cho thời gian quay lâu hơn

### 3. Thread send_to_drone()

Công dụng của thread này:

- Lấy command từ trong self.command_queue() và tùy thuộc theo số để gửi lệnh MAVLink cho drone
  > Các số này hoàn toàn có thể customize tùy theo ý mình, các số cho sẵn trước ở đây chỉ là để có một sự thống nhất trong việc encode và decode từ client sang sever.

```python
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
```
