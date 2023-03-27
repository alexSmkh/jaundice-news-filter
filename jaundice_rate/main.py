import aiohttp
import asyncio

import pymorphy2

from jaundice_rate.adapters import SANITIZERS
from jaundice_rate.settings import NEGATIVE_WORDS_PATH
from jaundice_rate.text_tools import calculate_jaundice_rate, split_by_words
from jaundice_rate.utils import read_file_async


async def fetch(session, url) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://inosmi.ru/20230325/kitay-261671429.html')
        morph = pymorphy2.MorphAnalyzer()

        article_text = SANITIZERS['inosmi_ru'](html, True)
        article_words = split_by_words(morph, article_text)
        charged_words = (await read_file_async(NEGATIVE_WORDS_PATH)).split('\n')
        rating = calculate_jaundice_rate(article_words, charged_words)
        print(f'Рейтинг: {rating}\nСлов в статье: {len(article_words)}')


if __name__ == '__main__':
    asyncio.run(main())
