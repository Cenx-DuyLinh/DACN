from SeverClientClass.Client2 import *

if __name__ == "__main__":
    HOST_SELF = "127.0.0.1"
    HOST_CLIENT = "10.8.0.9"
    PORT = 2000
    PORT_CAM = 2001
    client = Client(HOST_CLIENT, PORT,PORT_CAM)
    client.run()