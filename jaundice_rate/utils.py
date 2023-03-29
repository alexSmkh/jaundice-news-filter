import contextlib
import time
from typing import List, Set
from aiofile import async_open
import anyio

from jaundice_rate.settings import NEGATIVE_WORDS_PATH, POSITIVE_WORDS_PATH


async def read_file_async(filepath: str, mode: str = 'r', result: List = None) -> str:
    async with async_open(filepath, mode) as f:
        content = await f.read()
    if result is None:
        return content
    return result.append(content)


@contextlib.contextmanager
def calculation_time():
    start = time.monotonic()
    yield lambda: time.monotonic() - start


async def read_charged_words() -> Set[str]:
    raw_charged_words = []
    async with anyio.create_task_group() as tg:
        for words_path in [NEGATIVE_WORDS_PATH, POSITIVE_WORDS_PATH]:
            tg.start_soon(read_file_async, words_path, 'r', raw_charged_words)

    charged_words = set()
    for words in raw_charged_words:
        splited = words.strip().split('\n')
        charged_words.update(splited)

    return charged_words
