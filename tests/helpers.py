import ast
import os
from pathlib import Path

from aiofile import async_open


async def load_fixture(filename, eval=False):
    fixture_path = os.path.join(
        Path(__file__).parent.resolve(),
        'fixtures',
        filename,
    )
    async with async_open(fixture_path, 'r') as f:
        content = await f.read()

    if eval:
        return ast.literal_eval(content)
    return content
