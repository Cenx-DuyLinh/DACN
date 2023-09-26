from Class.UI import DroneControlApp
from Class.AIDataSocket import Server
import multiprocessing

def ControlApp(queue):
    connection_string = "tcp:127.0.0.1:5762"
    #connection_string = "COM10"
    MyCopter = DroneControlApp(string= connection_string, baud= 9600, queue=queue)

# ControlApp(1)

def AIReceiver(queue):
    server = Server(host= "0.0.0.0", port=8080) #port AI = 8080
    while True:
        AI_Data = server.read()
        if AI_Data != None:
            queue.put(AI_Data)
        
if __name__ == "__main__":
    queue = multiprocessing.Queue()
    p1 = multiprocessing.Process(target= ControlApp, args=(queue,))
    p2 = multiprocessing.Process(target= AIReceiver, args=(queue,))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()