from typing import List, Tuple
import aiohttp
import anyio
import asyncio

import pymorphy2

from jaundice_rate.adapters import SANITIZERS, get_sanitizer
from jaundice_rate.adapters.exceptions import ArticleNotFound, ResourceIsNotSupported
from jaundice_rate.settings import NEGATIVE_WORDS_PATH, TEST_JAUNDICE_ARTICLE_URLS, ProcessingStatus
from jaundice_rate.text_tools import calculate_jaundice_rate, split_by_words
from jaundice_rate.utils import read_file_async


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_article(
    morph: pymorphy2.MorphAnalyzer,
    url: str,
    processed_articles: List[Tuple[str, float, int, str]],
    charged_words: List[str],
    session: aiohttp.ClientSession,
) -> Tuple[str, float, int]:
    try:
        html_article = await fetch(session, url)
        sanitizer = get_sanitizer(url)
        article_text = sanitizer(html_article, True)
    except aiohttp.ClientError:
        return processed_articles.append((url, None, None, ProcessingStatus.FETCH_ERROR.value))
    except ArticleNotFound:
        return processed_articles.append((url, None, None, ProcessingStatus.PARSING_ERROR.value))
    except ResourceIsNotSupported:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.RESOURCE_IS_NOT_SUPPORTED_ERROR.value),
        )

    article_words = split_by_words(morph, article_text)
    rating = calculate_jaundice_rate(article_words, charged_words)
    words_count = len(article_words)
    processed_articles.append((url, rating, words_count, ProcessingStatus.OK.name))


async def main() -> None:
    morph = pymorphy2.MorphAnalyzer()
    charged_words = (await read_file_async(NEGATIVE_WORDS_PATH)).strip().split('\n')
    processed_articles = []

    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as tg:
            for url in TEST_JAUNDICE_ARTICLE_URLS:
                tg.start_soon(
                    process_article,
                    morph,
                    url,
                    processed_articles,
                    charged_words,
                    session,
                )

    for url, rating, words_count, status in processed_articles:
        print(f'{url}\nСтатус: {status}\nРейтинг: {rating}\nКоличество слов: {words_count}\n')


if __name__ == '__main__':
    asyncio.run(main())
