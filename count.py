import time

from collections import deque


class Scheduler():
    def __init__(self):
        self.ready = deque()  # Functions ready to execute

    def call_soon(self, func):  # Also could be called `def schedule"
        self.ready.append(func)

    def call_later(self, delay, func):
        if delay > 0:
            time.sleep(1)
            self.ready.append(lambda: self.call_later(delay - 1, func))
        else:
            self.ready.append(func)

    def run(self):
        while self.ready:
            func = self.ready.popleft()
            func()


scheduler = Scheduler()


def countdown(n):
    if n > 0:
        print("Down", n)
        # time.sleep(4)  # Blocking call
        # scheduler.call_soon(lambda: countdown(n - 1))
        scheduler.call_later(4, lambda: countdown(n - 1))


def countup(stop, n=0):
    if n < stop:
        print("Up", n)
        # time.sleep(1)
        # scheduler.call_soon(lambda: countup(stop, n + 1))
        scheduler.call_later(1, lambda: countup(stop, n + 1))


scheduler.call_soon(lambda: countdown(5))
scheduler.call_soon(lambda: countup(5))
scheduler.run()
