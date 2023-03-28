import contextlib
import time
from aiofile import async_open


async def read_file_async(filepath: str, mode: str = 'r') -> str:
    async with async_open(filepath, mode) as f:
        content = await f.read()
    return content


@contextlib.contextmanager
def calculation_time():
    start = time.monotonic()
    yield lambda: time.monotonic() - start
