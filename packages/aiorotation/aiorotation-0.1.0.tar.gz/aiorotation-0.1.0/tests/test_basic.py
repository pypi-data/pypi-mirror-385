import asyncio
from datetime import datetime

from aiorotation import Rotator

rotator = Rotator(rps=1, rpm=30, rph=99, tokens=['1tok', '2tok'])

async def main():
    requests = 100
    while requests:
        print(datetime.now(), 1)
        async with rotator.acquire() as token:
            print(datetime.now(), token)
        await asyncio.sleep(0.5)
        requests -= 1

asyncio.run(main())
