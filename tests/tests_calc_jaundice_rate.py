import pytest
from typing import List
from unittest.mock import AsyncMock

from jaundice_rate.adapters import SANITIZERS
from jaundice_rate.main import fetch_articles, process_article
from jaundice_rate.settings import NEGATIVE_WORDS_PATH, TEST_JAUNDICE_ARTICLE_URLS
from jaundice_rate.text_tools import calculate_jaundice_rate, split_by_words


@pytest.fixture
def html_articles():
    return [
        '<html><body>Article 1</body></html>',
        '<html><body>Article 1</body></html>',
        '<html><body>Article 1</body></html>',
    ]


@pytest.fixture
def charged_words():
    return ['word1', 'word2', 'word3']


@pytest.fixture
def mock_fetch(mocker):
    async def mock_fetch_impl(*args, **kwargs):
        return "<html><body>Test Article</body></html>"

    mock = mocker.pacth('jaundice_rate.main.fetch', mock_fetch_impl)
    mock.side_effect = mock_fetch_impl
    return mock


async def test_calculate_article_rating(html_articles, charged_words):
    morph = None

    results = [
        process_article(morph, "https://example.com/1", html_articles[0], charged_words),
        process_article(morph, "https://example.com/2", html_articles[1], charged_words),
        process_article(morph, "https://example.com/3", html_articles[2], charged_words),
    ]

    assert len(results) == 3
    for result in results:
        assert isinstance(result, tuple)
        assert len(result) == 3
        assert isinstance(result[0], str)
        assert isinstance(result[1], float)
        assert isinstance(result[2], int)
