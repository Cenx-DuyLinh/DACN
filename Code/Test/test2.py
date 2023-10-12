import queue

class LimitedQueue(queue.Queue):
    def __init__(self, maxsize):
        super().__init__(maxsize)
        self.maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        if self.full():
            self.get()  # Remove the oldest item when the queue is full
        super().put(item, block, timeout)

# Create a LimitedQueue with a maximum size of 5
q = LimitedQueue(maxsize=5)

# Add items to the queue
q.put(1)
q.put(2)
q.put(3)
q.put(4)
q.put(5)

print(f"Queue size: {q.qsize()}")  # Output: 5

# Add a new item (6) to the queue, oldest item (1) is automatically removed
for i in range(6,10):
    q.put(i)

# Retrieve and display the current queue items
    queue_items = list(q.queue)
    print(f"Updated queue: {queue_items}")  # Output: [2, 3, 4, 5, 6]