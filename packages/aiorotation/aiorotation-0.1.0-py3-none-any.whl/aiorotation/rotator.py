import asyncio
import time

from .limit import Limit
from .token import Token

class Rotator:
    def __init__(
        self,
        *,
        rps: int | None = None,
        rpm: int | None = None,
        rph: int | None = None,
        rpd: int | None = None,
        limits: list[Limit] | None = None,
        tokens: list[str] | None = None,
        timeout: float = 30.0,
    ):
        '''
        Automatically rotates tokens and enforces request rate limits.

        :param rps: Requests per second
        :param rpm: Requests per minute
        :param rph: Requests per hour
        :param rpd: Requests per day
        :param limits: Optional custom list of Limit objects.
                       Can be used together with rps/rpm/rph/rpd.
                       Duplicate time windows will raise a ValueError.
        :param tokens: Optional list of tokens for rotation
        :param timeout: Timeout in seconds for waiting between retries

        Examples:
            Rotator(rps=10)
            Rotator(rpm=100, tokens=['a', 'b', 'c'])
            Rotator(limits=[Limit(10, 5), Limit(60, 50)])
            Rotator(rps=1, limits=[Limit(1, 2)])  # duplicates → raises ValueError
        '''

        if all(i is None for i in (rps, rpm, rph, rpd, limits)):
            raise ValueError('Either rps, rpm, rph, rpd or limits must be specified at least')

        self.timeout = timeout
        self._lock = asyncio.Lock()
        
        all_limits = [Limit(s, l) for s, l in (
            (1, rps),
            (60, rpm),
            (3600, rph),
            (86400, rpd),
        ) if l is not None] + (limits or [])

        # check for duplicate time windows
        seen = {}
        for l in all_limits:
            if l.seconds in seen:
                raise ValueError(f'Duplicate limit period detected: {l.seconds} seconds')
            seen[l.seconds] = l.limit

        self.tokens = [
            Token(
                t,
                [Limit(l.seconds, l.limit) for l in all_limits]
            )
            for t in (tokens or [None])
        ]

    def acquire(self):
        return self._Context(self)

    class _Context:
        def __init__(self, parent: 'Rotator'):
            self.parent = parent
            self.token = None

        async def __aenter__(self):
            async with self.parent._lock:
                start = time.monotonic()

                while True:
                    best_token = min(self.parent.tokens, key=lambda t: t.wait_time())
                    wait = best_token.wait_time()

                    if wait == 0:
                        best_token.mark()
                        self.token = best_token.value
                        return self.token

                    if time.monotonic() - start + wait > self.parent.timeout:
                        if len(self.parent.tokens) > 1:
                            raise TimeoutError('All tokens busy for too long')
                        raise TimeoutError('Rate limit wait time exceeded')

                    await asyncio.sleep(wait)

        async def __aexit__(self, exc_type, exc, tb): # type: ignore
            pass
