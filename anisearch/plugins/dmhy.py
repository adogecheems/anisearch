import time
from typing import Optional, List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from .url_get import get_url
from ..anime.Anime import Anime
from ..search import log

BASE_URL = "https://dmhy.org/topics/list/page/{}?"


class Dmhy(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    def search(self, keyword: str, if_collected: bool = True, proxies: Optional[dict] = None,
               system_proxy: bool = False) -> List[Anime]:
        animes: List[Anime] = []
        page = 1
        params = {'keyword': keyword}
        if if_collected:
            params['sort_id'] = "31"

        while True:
            url = BASE_URL.format(page) + urlencode(params)
            try:
                html = get_url(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                bs = BeautifulSoup(html, self._parser)
                topic = bs.find(id="topic_list")

                if not topic:
                    break

                for tr in topic.tbody.find_all("tr"):
                    tds = tr.find_all("td")
                    release_time = tds[0].span.string
                    release_time = time.strftime(self._timefmt, time.strptime(release_time, '%Y/%m/%d %H:%M'))

                    title = tds[2].find("a").get_text(strip=True)
                    magnet = tds[3].find(class_="download-arrow").get("href")
                    size = tds[4].string

                    log.debug(f"Successfully got: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                page += 1
            except Exception as e:
                log.error(f"Error occurred while processing page {page}: {e}")
                break

        log.info(f"This search is complete: {keyword}")
        return animes
