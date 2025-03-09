import time

from collections import deque


class Scheduler():
    def __init__(self):
        self.ready = deque()  # Functions ready to execute

    def call_soon(self, func):  # Also could be called `def schedule"
        self.ready.append(func)
        self.sleeping = []

    # My somewhat functioning implementation
    def call_later(self, delay, func):
        deadline = time.time() + delay
        self.sleeping.append((deadline, func))
        self.sleeping.sort()  # Sort by closest deadline

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                # Find the nearest deadline
                deadline, func = self.sleeping.pop(0)
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
