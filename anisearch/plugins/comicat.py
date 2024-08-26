import time
import re
from typing import Optional, List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from .url_get import get_url
from ..anime.Anime import Anime
from ..search import log

BASE_URL = "https://comicat.org/search.php?"

def get_magnet(script: str) -> str:
    pattern = re.compile(r"Config$'(hash_id|announce)'$ = \"(.*?)\"")

    matches = pattern.findall(script)
    data = {key: value for key, value in matches}

    return f"magnet:?xt=urn:btih:{data['hash_id']}&dn={data['announce']}"


class Comicat(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    def search(self, keyword: str, collected: bool = True, proxies: Optional[dict] = None,
               system_proxy: bool = False) -> List[Anime]:
        animes: List[Anime] = []
        page = 1
        params = {'keyword': keyword}
        if collected:
            params['complete'] = 1

        while True:
            params['page'] = page

            url = BASE_URL + urlencode(params)
            try:
                html = get_url(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                bs = BeautifulSoup(html, self._parser)
                data = bs.find(id="data_list")

                if prev_data.tr == data.tr:
                    break

                prev_data = data

                for tr in data.find_all("tr"):
                    tds = tr.find_all("td")
                    release_time = tds[0].string
                    release_time = time.strftime(self._timefmt, time.strptime(release_time, '%Y/%m/%d'))

                    title = tds[2].a.get_text(strip=True)
                    link = tds[2].a.href
                    size = tds[3].string

                    link_html = get_url(link, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                    link_bs = BeautifulSoup(link_html, self._parser)
                    script = link_bs.find("script", text=lambda text: "Config['bt_data_title']" in text).string

                    magnet = get_magnet(script)

                    log.debug(f"Successfully got: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                page += 1
            except Exception as e:
                log.error(f"Error occurred while processing page {page}: {e}")
                break
