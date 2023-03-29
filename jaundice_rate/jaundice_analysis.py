from enum import Enum
import logging
from typing import List, Tuple
import aiohttp
from async_timeout import timeout
import anyio
import asyncio

import pymorphy2
from jaundice_rate import adapters
from jaundice_rate import text_tools

from jaundice_rate.adapters.exceptions import ArticleNotFound, ResourceIsNotSupported
from jaundice_rate.settings import TEST_JAUNDICE_ARTICLE_URLS
from jaundice_rate.utils import calculation_time, read_charged_words


logger = logging.getLogger(__name__)


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    RESOURCE_IS_NOT_SUPPORTED = 'RESOURCE_IS_NOT_SUPPORTED'
    TIMEOUT = 'TIMEOUT'


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
) -> List[Tuple[str, float, int, str]]:
    try:
        analysis_time = None

        async with timeout(5):
            html_article = await fetch(session, url)

        sanitizer = adapters.get_sanitizer(url)
        article_text = sanitizer(html_article, True)

        try:
            with calculation_time() as get_analysis_time:
                async with timeout(3):
                    article_words = await text_tools.split_by_words(morph, article_text)
                    rating = await text_tools.calculate_jaundice_rate(article_words, charged_words)
                    words_count = len(article_words)
        finally:
            analysis_time = get_analysis_time()

    except asyncio.exceptions.TimeoutError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.TIMEOUT.value, analysis_time),
        )
    except aiohttp.ClientError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.FETCH_ERROR.value, None),
        )
    except ArticleNotFound:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.PARSING_ERROR.value, None),
        )
    except ResourceIsNotSupported:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.RESOURCE_IS_NOT_SUPPORTED.value, None),
        )

    print((url, rating, words_count, ProcessingStatus.OK.name, analysis_time))
    processed_articles.append((url, rating, words_count, ProcessingStatus.OK.name, analysis_time))


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    morph = pymorphy2.MorphAnalyzer()
    charged_words = await read_charged_words()
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

    for url, rating, words_count, status, analysis_time in processed_articles:
        print(f'{url}\nСтатус: {status}\nРейтинг: {rating}\nКоличество слов: {words_count}')
        logger.info(f'Analysis time: {analysis_time} sec.\n')


if __name__ == '__main__':
    asyncio.run(main())
