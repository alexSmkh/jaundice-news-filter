from pathlib import Path

from aiofile import async_open


async def load_fixture(filename: str) -> str:
    fixture_path = Path(
        Path(__file__).parent.resolve(),
        'fixtures',
        filename,
    )
    async with async_open(fixture_path, 'r') as f:
        return await f.read()
