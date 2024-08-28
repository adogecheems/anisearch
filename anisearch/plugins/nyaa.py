import time
from typing import Optional, List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from ._webget import get_html
from ..anime.Anime import Anime
from ..search import log

BASE_URL = "https://nyaa.si/?"


class Nyaa(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    def search(self, keyword: str, collected: bool = False, proxies: Optional[dict] = None,
               system_proxy: bool = False) -> List[Anime]:
        animes: List[Anime] = []
        page = 1
        params = {'q': keyword, 'c': "1_0"}

        if collected:
            log.warning("Nyaa search does not support collection.")

        while True:
            params['p'] = page
            url = BASE_URL + urlencode(params)
            try:
                html = get_html(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                bs = BeautifulSoup(html, self._parser)
                tbody = bs.find('tbody')

                if not tbody or tbody.string == "\n":
                    break

                for tr in tbody.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) < 5:
                        continue
                    release_time = tds[4].string
                    release_time = time.strftime(self._timefmt, time.strptime(release_time, '%Y-%m-%d %H:%M'))

                    title = tds[1].a.get("title")
                    magnet_links = tds[2].find_all("a")
                    if len(magnet_links) < 2:
                        continue
                    magnet = magnet_links[1].get("href")
                    size = tds[3].string

                    log.debug(f"Successfully got: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                page += 1

            except Exception as e:
                log.error(f"Error occurred while processing page {page}: {e}")
                break

        log.info(f"This search is complete: {keyword}")
        return animes