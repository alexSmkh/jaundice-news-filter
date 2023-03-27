from typing import List, Tuple
import aiohttp
import asyncio

import pymorphy2

from jaundice_rate.adapters import SANITIZERS
from jaundice_rate.settings import NEGATIVE_WORDS_PATH, TEST_JAUNDICE_ARTICLE_URLS
from jaundice_rate.text_tools import calculate_jaundice_rate, split_by_words
from jaundice_rate.utils import read_file_async


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def fetch_articles(article_urls: List[str]) -> List[str]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        for article_url in article_urls:
            tasks.append(asyncio.create_task(fetch(session, article_url)))

        return await asyncio.gather(*tasks)


def calculate_article_rating(
    morph: pymorphy2.MorphAnalyzer,
    url: str,
    html_article: str,
    charged_words: List[str],
) -> Tuple[str, float, int]:
    article_text = SANITIZERS['inosmi_ru'](html_article, True)
    article_words = split_by_words(morph, article_text)
    rating = calculate_jaundice_rate(article_words, charged_words)
    words_count = len(article_words)
    return url, rating, words_count


async def main() -> None:
    morph = pymorphy2.MorphAnalyzer()
    read_charged_words_task = asyncio.create_task(read_file_async(NEGATIVE_WORDS_PATH))

    html_articles = await fetch_articles(TEST_JAUNDICE_ARTICLE_URLS)

    charged_words = (await read_charged_words_task).split('\n')
    urls_ratings_words_count = []
    for url, html_article in zip(TEST_JAUNDICE_ARTICLE_URLS, html_articles):
        urls_ratings_words_count.append(
            calculate_article_rating(morph, url, html_article, charged_words)
        )

    for url, rating, words_count in urls_ratings_words_count:
        print(f'{url}\nРейтинг: {rating}\nКоличество слов: {words_count}\n')


if __name__ == '__main__':
    asyncio.run(main())
