import asyncio
import logging
from enum import Enum

import aiohttp
import anyio
import pymorphy2
from async_timeout import timeout

from jaundice_rate import adapters, text_tools
from jaundice_rate.adapters.exceptions import ArticleNotFoundError, ResourceIsNotSupportedError
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
    processed_articles: list[tuple],
    charged_words: set[str],
    session: aiohttp.ClientSession,
) -> None:
    analysis_time = None
    get_analysis_time = None

    try:
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
            if get_analysis_time is not None:
                analysis_time = get_analysis_time()

    except asyncio.exceptions.TimeoutError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.TIMEOUT.value, analysis_time),
        )
    except aiohttp.ClientError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.FETCH_ERROR.value, None),
        )
    except ArticleNotFoundError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.PARSING_ERROR.value, None),
        )
    except ResourceIsNotSupportedError:
        return processed_articles.append(
            (url, None, None, ProcessingStatus.RESOURCE_IS_NOT_SUPPORTED.value, None),
        )

    processed_articles.append(  # noqa: RET503
        (url, rating, words_count, ProcessingStatus.OK.name, analysis_time),
    )


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
        print(  # noqa: T201
            f'{url}\nСтатус: {status}\nРейтинг: {rating}\nКоличество слов: {words_count}',
        )
        logger.info('Analysis time: %s sec.\n', analysis_time)


if __name__ == '__main__':
    asyncio.run(main())
