from .limit import Limit

class Token:
    def __init__(self, value: str | None, limits: list[Limit]):
        self.value = value
        self.limits = limits

    def can_use(self) -> bool:
        return all(l.can_use() for l in self.limits)

    def wait_time(self) -> float:
        return max((l.wait_time() for l in self.limits), default=0.0)

    def mark(self):
        for l in self.limits:
            l.mark()
