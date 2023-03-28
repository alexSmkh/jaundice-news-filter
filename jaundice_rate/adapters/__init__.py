from urllib.parse import urlparse
from . import inosmi_ru

from .exceptions import ArticleNotFound, ResourceIsNotSupported

__all__ = ['SANITIZERS', 'ArticleNotFound', 'get_sanitizer']

SANITIZERS = {
    'inosmi.ru': inosmi_ru.sanitize,
}


def get_sanitizer(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    sanitizer = SANITIZERS.get(domain)

    if sanitizer is None:
        raise ResourceIsNotSupported

    return sanitizer
