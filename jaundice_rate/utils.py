import contextlib
import time
from collections.abc import Callable, Generator

import anyio
from aiofile import async_open

from jaundice_rate.settings import NEGATIVE_WORDS_PATH, POSITIVE_WORDS_PATH


async def read_file_async(filepath: str, mode: str = 'r', result: list = []) -> list:  # noqa: B006
    async with async_open(filepath, mode) as f:
        content = await f.read()
    if not result:
        return content
    result.append(content)
    return result

@contextlib.contextmanager
def calculation_time() -> Generator[Callable[[], float], None, None]:
    start = time.monotonic()
    yield lambda: time.monotonic() - start


async def read_charged_words() -> set[str]:
    raw_charged_words = []
    async with anyio.create_task_group() as tg:
        for words_path in [NEGATIVE_WORDS_PATH, POSITIVE_WORDS_PATH]:
            tg.start_soon(read_file_async, words_path, 'r', raw_charged_words)

    charged_words = set()
    for words in raw_charged_words:
        splited = words.strip().split('\n')
        charged_words.update(splited)

    return charged_words
