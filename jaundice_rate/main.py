import aiohttp
import asyncio

from jaundice_rate.adapters import SANITIZERS
from jaundice_rate.adapters.html_tools import remove_all_tags


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20230325/kitay-261671429.html')
        print(SANITIZERS['inosmi_ru'](html))


if __name__ == '__main__':
    asyncio.run(main())
