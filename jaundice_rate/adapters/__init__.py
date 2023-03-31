from urllib.parse import urlparse

from . import inosmi_ru
from .exceptions import ArticleNotFoundError, ResourceIsNotSupportedError

__all__ = ['SANITIZERS', 'ArticleNotFoundError', 'get_sanitizer']

SANITIZERS = {
    'inosmi.ru': inosmi_ru.sanitize,
}


def get_sanitizer(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    sanitizer = SANITIZERS.get(domain)

    if sanitizer is None:
        raise ResourceIsNotSupportedError

    return sanitizer
