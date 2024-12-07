import os

import cloudscraper
import requests
from requests import RequestException

from .. import log


def get_html(url, proxies=None, system_proxy=False, verify=True):
    if system_proxy:
        http_proxy = os.environ.get('http_proxy')
        https_proxy = os.environ.get('https_proxy')
        if http_proxy or https_proxy:
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            log.warning("No system proxy found.")

    counter = 0
    while counter < 3:
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


        except RequestException as e:
            counter += 1

            log.exception(f"A network problem occurred, retrying: {counter}.")

    log.error(f"This search was aborted due to network reasons: {e}.")
    raise e
