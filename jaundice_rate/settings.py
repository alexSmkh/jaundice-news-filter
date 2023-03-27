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
