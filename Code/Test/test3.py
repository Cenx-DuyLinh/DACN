import tkinter as tk
import queue

class App:
    def __init__(self, queue):
        self.counter = 0
        self.window = tk.Tk()
        self.label = tk.Label(text=self.counter)
        self.button = tk.Button()
        self.button.pack()
        self.label.pack()
        self.queue = queue

    def update1(self):
        if self.queue.empty():
            pass
        else: 
            counter = self.queue.get() 
            self.label.configure(text=counter)
            print(f"got counter: {counter}")
            print('hi')
            self.label.after(100, self.update1)

    def update2(self):
        if self.queue.empty():
            pass
        else: 
            counter = self.queue.get()
            self.label.configure(text=counter)
            print(f"got counter: {counter}")
            print(self.queue.qsize())
            self.label.after(100, self.update2)

q = queue.Queue()   
for i in range(0, 100):
    q.put(i)

obj = App(q)
obj.update1()
obj.update2()
obj.window.mainloop()