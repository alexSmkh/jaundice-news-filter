import ast
import asyncio

import aiohttp
import pymorphy2
import pytest
from pytest_mock import MockFixture

from jaundice_rate.jaundice_analysis import ProcessingStatus, process_article
from tests.helpers import load_fixture


@pytest.mark.asyncio()
async def test_process_article(mocker: MockFixture) -> None:
    article_html = await load_fixture('article_html.txt')
    charged_words = ast.literal_eval(await load_fixture('charged_words.txt'))

    (
        expected_url,
        expected_rating,
        expected_words_count,
        expected_status,
        _,
    ) = ast.literal_eval(await load_fixture('article_analysis_result.txt'))

    expected_url = 'http://inosmi.ru/article/1'
    morph = pymorphy2.MorphAnalyzer()

    mocker.patch('jaundice_rate.jaundice_analysis.fetch', return_value=article_html)

    processed_articles = []

    await process_article(
        morph,
        expected_url,
        processed_articles,
        charged_words,
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert expected_url == url
    assert expected_rating == rating
    assert expected_words_count == words_count
    assert expected_status == status
    assert analysis_time > 0.0


@pytest.mark.asyncio()
async def test_process_article_with_timeout(mocker: MockFixture) -> None:
    mocker.patch(
        'jaundice_rate.jaundice_analysis.fetch',
        side_effect=asyncio.exceptions.TimeoutError,
        return_value=None,
    )

    expected_url = 'http://inosmi.ru/article/1'
    processed_articles = []
    await process_article(
        pymorphy2.MorphAnalyzer(),
        expected_url,
        processed_articles,
        set(),
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert url == expected_url
    assert status == ProcessingStatus.TIMEOUT.value
    assert rating is None
    assert words_count is None
    assert analysis_time is None


@pytest.mark.asyncio()
async def test_process_article_when_resource_is_not_supported(mocker: MockFixture) -> None:
    mocker.patch(
        'jaundice_rate.jaundice_analysis.fetch',
        return_value='',
    )

    expected_url = 'http://example.com'
    processed_articles = []
    await process_article(
        pymorphy2.MorphAnalyzer(),
        expected_url,
        processed_articles,
        set(),
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert url == expected_url
    assert status == ProcessingStatus.RESOURCE_IS_NOT_SUPPORTED.value
    assert rating is None
    assert words_count is None
    assert analysis_time is None


@pytest.mark.asyncio()
async def test_process_article_when_article_not_found(mocker: MockFixture) -> None:
    mocker.patch(
        'jaundice_rate.jaundice_analysis.fetch',
        return_value='',
    )

    expected_url = 'http://inosmi.ru/article/1'
    processed_articles = []
    await process_article(
        pymorphy2.MorphAnalyzer(),
        expected_url,
        processed_articles,
        set(),
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert url == expected_url
    assert status == ProcessingStatus.PARSING_ERROR.value
    assert rating is None
    assert words_count is None
    assert analysis_time is None


@pytest.mark.asyncio()
async def test_process_article_with_too_long_analysis_time(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockFixture,
) -> None:
    monkeypatch.setattr('jaundice_rate.adapters.get_sanitizer', lambda *args: lambda *args: '')
    mocker.patch(
        'jaundice_rate.jaundice_analysis.fetch',
        return_value='',
    )

    max_allowed_analysis_time = 3

    async def mock_split_by_words(*args) -> list:  # noqa: ARG001, ANN002
        await asyncio.sleep(max_allowed_analysis_time + 0.1)
        return []

    monkeypatch.setattr('jaundice_rate.text_tools.split_by_words', mock_split_by_words)

    expected_url = 'http://inosmi.ru/article/1'
    processed_articles = []
    await process_article(
        pymorphy2.MorphAnalyzer(),
        expected_url,
        processed_articles,
        set(),
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert url == expected_url
    assert status == ProcessingStatus.TIMEOUT.value
    assert rating is None
    assert words_count is None
    assert analysis_time > max_allowed_analysis_time


@pytest.mark.asyncio()
async def test_process_article_when_client_error(mocker: MockFixture) -> None:
    mocker.patch(
        'jaundice_rate.jaundice_analysis.fetch',
        side_effect=aiohttp.ClientError,
        return_value=None,
    )

    expected_url = 'http://inosmi.ru/article/1'
    processed_articles = []
    await process_article(
        pymorphy2.MorphAnalyzer(),
        expected_url,
        processed_articles,
        set(),
        None,  # type: ignore
    )

    url, rating, words_count, status, analysis_time = processed_articles[0]

    assert url == expected_url
    assert status == ProcessingStatus.FETCH_ERROR.value
    assert rating is None
    assert words_count is None
    assert analysis_time is None
