from SeverClientClass.Client2 import *

if __name__ == "__main__":
    HOST_SELF = "127.0.0.1"
    HOST_CLIENT = "10.8.0.9"
    PORT = 2000
    client = Client(HOST_SELF, PORT)
    client.run()