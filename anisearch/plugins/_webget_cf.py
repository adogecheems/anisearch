import os
import requests
import cloudscraper
from ..search import log


def get_html(url, proxies=None, system_proxy=False, verify=True):
    if system_proxy:
        http_proxy = os.environ.get('http_proxy')
        https_proxy = os.environ.get('https_proxy')
        if http_proxy or https_proxy:
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            log.warning("No system proxy found.")
            raise requests.exceptions.ProxyError("No system proxy found.")

    try:
        if not verify:
            requests.packages.urllib3.disable_warnings()

        scraper = cloudscraper.create_scraper(delay=5, browser={
            'browser': 'chrome',
            'platform': 'linux',
            'mobile': False,
        })

        response = scraper.get(url, proxies=proxies, verify=verify)

        log.debug(f"A request has been made to url: {url}")
        return response.content

    except requests.RequestException as e:
        log.exception(f"The search was aborted due to network reasons: {e}")
        raise
