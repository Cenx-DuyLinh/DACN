from CopterAAVC.Class.MAVlink import MyMAVlink,ProgressStatus

import tkinter as tk
def RUN():

    copter = MyMAVlink("tcp:127.0.0.1:5762",57600,0)
    window = tk.Tk()
    button = tk.Button(window,text="send",width=15,height=3,command=lambda:copter.send_ned_pos_and_get_ack([10,0,0]))
    button2 = tk.Button(window,text="takeoff",width=15,height=3,command=lambda:copter.take_off(10))
    button.pack()
    button2.pack()
    window.mainloop()
if __name__ == "__main__":
    RUN()