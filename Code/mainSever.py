from SeverClientClass.Sever5copy2 import *

if __name__ == "__main__":
    HOST_SELF = "127.0.0.1"
    HOST_SEVER = "10.8.0.9"

    DRONE_SITL = "tcp:127.0.0.1:5762"
    DRONE_TELE= "COM10"
    DRONE_PIX = "/dev/serial0"
    
    PORT = 2000
    PORT_CAM = 5000
    server = Server(HOST_SEVER, PORT,PORT_CAM,DRONE_PIX)
    server.run()