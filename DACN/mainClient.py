from SeverClientClass.Client import *

if __name__ == "__main__":
    HOST = "127.0.0.1"
    # HOST = "10.8.0.13"
    PORT = 2000
    client = Client(HOST, PORT)
    client.run()