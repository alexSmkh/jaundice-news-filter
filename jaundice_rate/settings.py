import os
from pathlib import Path


NEGATIVE_WORDS_PATH = os.path.join(
    Path(__file__).parent.resolve(),
    'charged_dict',
    'negative_words.txt',
)
POSITIVE_WORDS_PATH = os.path.join(
    Path(__file__).parent.resolve(),
    'charged_dict',
    'positive_words.txt',
)
TEST_JAUNDICE_ARTICLE_URLS = [
    'https://inosmi.ru/20230325/ryba-261669379.html',
    'https://inosmi.ru/20230325/kitay-261671429.html',
    'https://inosmi.ru/20230325/k3.html',
    'https://inosmi.ru/20230325/k3dfsf3.html',
    'https://inosmi.ru/20230325/kasdfagsgas3.html',
    'https://inosmi.ru/20230326/globalizatsiya--261684362.html',
    'https://inosmi.ru/20230328/severnye-potoki-261740087.html',
    'https://inosmi.ru/20230324/dollar-261661978.html',
    'https://ria.ru/20230328/rzhd-1861313840.html',
]
