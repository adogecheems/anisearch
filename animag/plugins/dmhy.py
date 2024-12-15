import time
from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from .. import *

BASE_URL = "https://dmhy.org/topics/list/page/{}?"


class Dmhy(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        super().__init__(parser, verify, timefmt)

    def search(self, keyword: str, collected: bool = False, proxies: Optional[dict] = None,
               system_proxy: bool = False, **extra_options) -> List[Anime] | None:
        animes: List[Anime] = []
        page = 1

        params = {'keyword': keyword, **extra_options}
        if collected:
            params['sort_id'] = "31"

        while True:
            log.debug(f"Processing the page of {page}")

            url = BASE_URL.format(page) + urlencode(params)
            html = get_html(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)

            try:
                bs = BeautifulSoup(html, self._parser)
                tbody = bs.find("tbody")

                if not tbody:
                    break

                for tr in tbody.find_all("tr"):
                    tds = tr.find_all("td")
                    release_time = tds[0].span.string
                    release_time = time.strftime(self._timefmt, time.strptime(release_time, '%Y/%m/%d %H:%M'))

                    title = tds[2].find_all("a")[-1].get_text(strip=True)
                    magnet = tds[3].find(class_="download-arrow")["href"]
                    size = tds[4].string

                    log.debug(f"Successfully got: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                page += 1

            except Exception as e:
                raise SearchParserError(f"A error occurred while processing the page of {page} with error {e!r}")

        return animes
