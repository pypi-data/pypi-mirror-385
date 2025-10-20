import time
# from datetime import timedelta
from collections import deque

class Limit:
    def __init__(self, seconds: float, limit: int):
        '''
        Represents a single rate limit constraint.

        :param seconds: Time window duration in seconds
        :param limit: Maximum number of allowed actions within the given time window

        Example:
            Limit(60, 100)  # 100 requests per minute
        '''

        self.seconds = seconds
        self.limit = limit
        self.calls: deque[float] = deque()

    def __repr__(self) -> str:
        return f'Limit({self.seconds}, {self.limit})'

    def clean(self):
        now = time.monotonic()
        while self.calls and now - self.calls[0] > self.seconds:
            self.calls.popleft()

    def can_use(self):
        self.clean()
        return len(self.calls) < self.limit

    def wait_time(self) -> float:
        self.clean()
        if not self.limit or len(self.calls) < self.limit:
            return 0.0
        oldest = self.calls[0]
        now = time.monotonic()
        return self.seconds - (now - oldest)

    def mark(self):
        self.calls.append(time.monotonic())
