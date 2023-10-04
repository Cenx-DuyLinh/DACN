import socket

#Vu 10.8.0.62
#Thien 10.8.0.13
class Client():
    def __init__(self, host, port):
        """_The sender_
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        
    def send(self, data):
        try:
            self.socket.send(data.encode())
            print("Send data: ", data)
        except:
            raise ConnectionRefusedError()
    
class Server():
    def __init__(self, host, port):
        """_The receiver_
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.wait()
        
    def wait(self):
        print("Waiting for client")
        self.connection, self.address = self.socket.accept()
        print(f"Connected with client at {self.address}")
    
    def read(self):
        try:
            data = self.connection.recv(64).decode()
            if not data:
                print("No data")
            else:
                try:
                    x_relative_distance, y_relative_distance = data.split()
                    #print(f"Received Data: x_relative = {x_relative_distance}, y_relative = {y_relative_distance}")
                    return [float(x_relative_distance), float(y_relative_distance)]
                except Exception as e:
                    print(e)
                    print("Data received error!")
            
        except Exception as e:
            print(e)
            self.connection.close()
            self.wait()