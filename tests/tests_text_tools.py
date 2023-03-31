import pymorphy2
import pytest

from jaundice_rate.text_tools import calculate_jaundice_rate, split_by_words


@pytest.mark.asyncio()
async def test_split_by_words() -> None:
    morph = pymorphy2.MorphAnalyzer()

    assert await split_by_words(morph, 'Во-первых, он хочет, чтобы') == [
        'во-первых',
        'хотеть',
        'чтобы',
    ]

    assert await split_by_words(morph, '«Удивительно, но это стало началом!»') == [
        'удивительно',
        'это',
        'стать',
        'начало',
    ]


@pytest.mark.asyncio()
async def test_calculate_jaundice_rate() -> None:
    assert -0.01 < await calculate_jaundice_rate([], set()) < 0.01

    jaundice_rate = await calculate_jaundice_rate(
        ['все', 'аутсайдер', 'побег'], {'аутсайдер', 'банкротство'},
    )
    assert 33.0 < jaundice_rate < 34.0
