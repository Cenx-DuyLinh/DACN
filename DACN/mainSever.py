from SeverClientClass.Sever2 import *

if __name__ == "__main__":
    HOST = "127.0.0.1"
    SITL = "tcp:127.0.0.1:5762"
    DRONE= "COM10"
    # HOST = "10.8.0.13"
    PORT = 2000
    server = Server(HOST, PORT,SITL)
    server.run()