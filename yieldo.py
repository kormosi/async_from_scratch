import time
import heapq
from collections import deque


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = []
        self.current = None  # Currently executing generator
        self.sequence = 0
        
    async def sleep(self, delay):
        deadline = time.time() + delay
        self.sequence += 1
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None
        await switch()

    def new_task(self, coro):
        self.ready.append(coro)

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, coro = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(coro)
            self.current = self.ready.popleft()
            try:
                self.current.send(None)
                if self.current:
                    print("self.current exists")
                    self.ready.append(self.current)
            except StopIteration:
                pass

class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


async def countdown(n):
    while n > 0:
        print("Down", n)
        await scheduler.sleep(4)
        n -= 1


async def countup(stop):
    x = 0
    while x < stop:
        print("Up", x)
        await scheduler.sleep(1)
        x += 1


scheduler = Scheduler()

scheduler.new_task(countdown(5))
scheduler.new_task(countup(20))
scheduler.run()
