import heapq
import time

from collections import deque


class Scheduler():
    def __init__(self):
        self.ready = deque()  # Functions ready to execute

    def call_soon(self, func):  # Also could be called `def schedule"
        self.ready.append(func)
        self.sleeping = []
        # A tie-braking mechanism to resolve cases where two co-routines would get
        # scheduled with the same deadline (we would get a TypeError, because we cannot
        # compare two functions).
        self.sequence = 0

    # My somewhat functioning implementation
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


def countdown(n):
    if n > 0:
        print("Down", n)
        scheduler.call_later(4, lambda: countdown(n - 1))


def countup(stop, n=0):
    if n < stop:
        print("Up", n)
        scheduler.call_later(1, lambda: countup(stop, n + 1))


scheduler.call_soon(lambda: countdown(5))
scheduler.call_soon(lambda: countup(7))
scheduler.run()
