import time
import heapq
from collections import deque


class Result:
    def __init__(self, value=None, exception=None):
        self.value = value
        self.exception = exception

    def result(self):
        if self.exception:
            raise self.exception
        else:
            return self.value


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


class QueueClosed(Exception):
    pass


class AsyncQueue:
    def __init__(self):
        self.items = deque()
        self.waiting = deque()  # All getters waiting for data
        self._closed = False  # Can queue be used?

    def close(self):
        self._closed = True
        if self.waiting and not self.items:
            for func in self.waiting:
                scheduler.call_soon(func)

    def put(self, item):
        if self._closed:
            raise QueueClosed()
        self.items.append(item)
        if self.waiting:
            func = self.waiting.popleft()
            scheduler.call_soon(func)

    def get(self, callback):
        # Wait until an item is available, then return it
        if self.items:
            callback(Result(value=self.items.popleft()))  # Good result
        else:
            if self._closed:
                callback(Result(exception=QueueClosed()))  # Bad result
            self.waiting.append(lambda: self.get(callback))


scheduler = Scheduler()


def producer(q, count):
    def _run(n):
        if n < count:
            print("Producing", n)
            q.put(n)
            scheduler.call_later(1, lambda: _run(n + 1))
        else:
            print("Producer done")
            q.close()

    _run(0)


def consumer(q):
    def _consume(result):
        try:
            item = result.result()
            print("Consuming", item)
            scheduler.call_soon(lambda: consumer(q))
        except QueueClosed:
            print("Consumer done")

    q.get(callback=_consume)


q = AsyncQueue()
scheduler.call_soon(lambda: producer(q, 3))
scheduler.call_soon(lambda: consumer(q))
scheduler.run()
