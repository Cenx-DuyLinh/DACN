from DACN.SeverClientClass.Sever4 import *

if __name__ == "__main__":
    HOST_SELF = "127.0.0.1"
    HOST_SEVER = "10.8.0.9"
    SITL = "tcp:127.0.0.1:5762"
    DRONE= "COM10"
    
    PORT = 2000
    server = Server(HOST_SELF, PORT,SITL)
    server.run()