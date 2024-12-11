import os

import requests
from requests import RequestException

from .. import log, SearchRequestError

RETRYING_NUM = 3


def get_html(url, proxies=None, system_proxy=False, verify=True):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
    }

    if system_proxy:
        http_proxy = os.environ.get('http_proxy')
        https_proxy = os.environ.get('https_proxy')
        if http_proxy or https_proxy:
            proxies = {'http': http_proxy, 'https': https_proxy}
        else:
            log.warning("No system proxy found.")

    counter = 0
    while True:
        try:
            if not verify:
                requests.packages.urllib3.disable_warnings()

            log.debug(f"A request has been made to the url: {url}.")
            response = requests.get(url, headers=headers, proxies=proxies, verify=verify)
            break

        except RequestException as e:
            counter += 1
            log.exception(f"A request exception occurred, retrying: {counter}.")

            if counter >= RETRYING_NUM:
                log.error(f"Failed to get the response by the url: {url}.")
                raise SearchRequestError() from e

    if response.status_code == 200 and response.headers['Content-Type'] == "text/html":
        return response.content
    else:
        log.error(f"Got a unknown response by the url: {url}.")
        raise SearchRequestError()
