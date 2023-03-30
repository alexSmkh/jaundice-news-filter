from aiohttp import web

import logging
from typing import List
import aiohttp
import anyio
import asyncio

import pymorphy2
from jaundice_rate.jaundice_analysis import process_article
from jaundice_rate.utils import read_charged_words


logger = logging.getLogger(__name__)
MORPH = pymorphy2.MorphAnalyzer()
CHARGED_WORDS = None


async def load_charged_words() -> List[str]:
    global CHARGED_WORDS
    CHARGED_WORDS = await read_charged_words()


async def handle_articles(request):
    article_urls = request.query.get('urls', '')

    if not article_urls:
        return web.json_response({"error": "Bad Request"}, status=400)

    article_urls = article_urls.split(',')

    if len(article_urls) > 10:
        return web.json_response(
            {"error": "too many urls in request, should be 10 or less"},
            status=400,
        )

    processed_articles = []
    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as tg:
            for url in article_urls:
                tg.start_soon(
                    process_article,
                    MORPH,
                    url,
                    processed_articles,
                    CHARGED_WORDS,
                    session,
                )

    response = []
    for url, rating, words_count, status, _ in processed_articles:
        response.append({
            'status': status,
            'url': url,
            'score': rating,
            'words_count': words_count,
        })

    return web.json_response(response)


app = web.Application()
app.add_routes(
    [
        web.get('/', handle_articles),
    ],
)


if __name__ == '__main__':
    asyncio.run(load_charged_words())
    web.run_app(app)
