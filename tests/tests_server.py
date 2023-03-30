import pytest
from aiohttp import web
# from pytest_aiohttp import aiohttp_server, aiohttp_client

from jaundice_rate.server import handle_articles, load_charged_words


@pytest.mark.asyncio
async def create_app():
    app = web.Application()
    app.router.add_route('GET', '/', handle_articles)
    return app


@pytest.mark.asyncio
async def test_handle_articles_valid_request(aiohttp_client):
    client = await aiohttp_client(await create_app())
    resp = await client.get(
        '/',
        params={'urls': 'https://example.com/article1,https://example.com/article2'},
    )
    assert resp.status == 200
    data = await resp.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_handle_articles_invalid_request(aiohttp_client):
    client = await aiohttp_client(await create_app())
    resp = await client.get('/')
    assert resp.status == 400
    data = await resp.json()
    assert 'error' in data


@pytest.mark.asyncio
async def test_handle_articles_too_many_urls(aiohttp_client):
    client = await aiohttp_client(await create_app())
    urls = ','.join(['https://example.com/article' + str(i) for i in range(11)])
    resp = await client.get('/', params={'urls': urls})
    assert resp.status == 400
    data = await resp.json()
    assert 'error' in data
