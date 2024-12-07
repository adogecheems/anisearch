import os

import requests
from requests import RequestException

from .. import log


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
    while counter < 3:
        try:
            if not verify:
                requests.packages.urllib3.disable_warnings()

            response = requests.get(url, headers=headers, proxies=proxies, verify=verify)
            log.debug(f"A request has been made to url: {url}.")
            return response.content

        except RequestException:
            counter += 1

            log.exception(f"A network problem occurred, retrying: {counter}.")

    log.error("This search was aborted due to network reasons.")
