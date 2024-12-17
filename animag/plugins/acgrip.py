import time
from typing import List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from .. import *

DOMAIN = "https://acg.rip"
BASE_URL = "https://acg.rip/page/{}?"


class Acgrip(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        log.warning("Using acg.rip searcher can only return torrent download addresses.")
        super().__init__(parser, verify, timefmt)

    def search(self, keyword: str, collected: bool = False, proxies: Optional[dict] = None,
               system_proxy: bool = False, **extra_options) -> List[Anime] | None:
        animes: List[Anime] = []
        page = 1

        params = {'term': keyword, **extra_options}
        if collected:
            log.warning("Acg.rip searcher does not support collection.")

        while True:
            log.debug(f"Processing the page of {page}")

            url = BASE_URL.format(page) + urlencode(params)
            html = get_html(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)

            try:
                bs = BeautifulSoup(html, self._parser)
                tr = bs.thead.find_next_sibling("tr")

                if tr is None:
                    break

                while tr:
                    tds = tr.find_all("td")

                    release_time = tds[0].find_all("div")[1].time.get("datetime")
                    release_time = time.strftime(self.timefmt, time.localtime(int(release_time)))

                    title = tds[1].find_all("a")[-1].get_text(strip=True)
                    magnet = DOMAIN + tds[2].a["href"]
                    size = tds[3].string

                    log.debug(f"Successfully got the magnet: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                    tr = tr.find_next_sibling("tr")

                page += 1

            except Exception as e:
                raise SearchParserError(f"A error occurred while processing the page of {page} with error {e!r}")

        return animes
