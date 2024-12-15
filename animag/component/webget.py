import os
from functools import lru_cache
from typing import Optional, Dict, Union

import requests
from requests import RequestException, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning

from .. import log, SearchRequestError

RETRYING_NUM = 3
DEFAULT_TIMEOUT = 10
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
}


class RequestSession:
    """Session manager for HTTP requests with retry mechanism."""

    def __init__(self):
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        """Create and configure a requests session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=RETRYING_NUM,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(DEFAULT_HEADERS)
        return session

    def close(self):
        """Close the session."""
        self.session.close()


@lru_cache(maxsize=32)
def get_system_proxies() -> Dict[str, str]:
    """
    Get system proxy settings.

    Returns:
        Dict[str, str]: Proxy configuration dictionary
    """
    proxies = {}
    http_proxy = os.environ.get('http_proxy')
    https_proxy = os.environ.get('https_proxy')

    if http_proxy:
        proxies['http'] = http_proxy
    if https_proxy:
        proxies['https'] = https_proxy

    if not proxies:
        log.warning("No system proxy found.")

    return proxies


def validate_response(response: Response, url: str) -> bytes:
    """
    Validate HTTP response.

    Args:
        response: Response object to validate
        url: URL of the request

    Returns:
        bytes: Response content

    Raises:
        SearchRequestError: If response is invalid
    """
    if response.status_code != 200:
        raise SearchRequestError(f"Invalid status code {response.status_code} for URL: {url}")

    content_type = response.headers.get('Content-Type', '')
    if not content_type.startswith("text/html"):
        raise SearchRequestError(f"Invalid content type '{content_type}' for URL: {url}")

    return response.content


def get_html(
        url: str,
        proxies: Optional[Dict[str, str]] = None,
        system_proxy: bool = False,
        verify: bool = True
) -> bytes:
    """
    Get HTML content from URL with retry mechanism.

    Args:
        url: Target URL
        proxies: Proxy configuration
        system_proxy: Whether to use system proxy
        verify: Whether to verify SSL certificates

    Returns:
        bytes: HTML content

    Raises:
        SearchRequestError: If request fails
    """
    if not verify:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if system_proxy:
        proxies = get_system_proxies()

    session = RequestSession()
    try:
        log.debug(f"Making request to URL: {url}")
        response = session.session.get(
            url,
            proxies=proxies,
            verify=verify,
            timeout=DEFAULT_TIMEOUT
        )
        return validate_response(response, url)

    except RequestException as e:
        raise SearchRequestError(f"Request failed for URL {url}: {e!r}")

    finally:
        session.close()
