import time
import heapq
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()  # Functions ready to execute
        self.sleeping = []
        # A tie-braking mechanism to resolve cases where two co-routines would get
        # scheduled with the same deadline (we would get a TypeError, because we cannot
        # compare two functions).
        self.sequence = 0

    def call_soon(self, func):  # Also could be called `def schedule"
        self.ready.append(func)

    def call_later(self, delay, func):
        self.sequence += 1
        deadline = time.time() + delay
        heapq.heappush(self.sleeping, (deadline, self.sequence, func))

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # Find the nearest deadline
                deadline, _, func = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(func)
            while self.ready:
                func = self.ready.popleft()
                func()


scheduler = Scheduler()


class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # All getters waiting for data

    def put(self, item):
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            scheduler.call_soon(func)

    def get(self, callback):
        # Wait until an item is available, then return it
        if self.items:
            callback(self.items.popleft())
        else:
            self.waiting.append(lambda: self.get(callback))


def producer(q, count):
    def _run(n):
        if n < count:
            print("Producing", n)
            q.put(n)
            scheduler.call_later(1, lambda: _run(n + 1))
        else:
            print("Producer done")
            q.put(None)  # "Sentinel" to shut down

    _run(0)


def consumer(q):
    def _consume(item):
        if item is None:
            print("Consumer done")
        else:
            print("Consuming", item)
            scheduler.call_soon(lambda: consumer(q))

    q.get(callback=_consume)


q = AsyncQueue()
scheduler.call_soon(lambda: producer(q, 10))
scheduler.call_soon(lambda: consumer(q))
scheduler.run()
