import functools
from typing import Optional

from .. import log


class SearchError(Exception):
    def __init__(self, msg: Optional[str] = None):
        super().__init__(msg)
        log.error(msg)


class SearchRequestError(SearchError):
    pass


class SearchParserError(SearchError):
    pass


class SaveCSVError(SearchError):
    pass


class SizeFormatError(SearchError):
    pass


class PluginImportError(SearchError):
    pass


def no_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Caught error: {e!r}")

    return wrapper
