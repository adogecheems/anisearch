import re
import time
from typing import Optional, List
from urllib.parse import urlencode

from bs4 import BeautifulSoup

from . import BasePlugin
from .Anime import Anime
from ._webget import get_html
from .. import log

BASE_URL = "https://www.tokyotosho.info/search.php?"

def extract_info(text):
    size_match = re.search(r"Size:\s([\d.]+(?:MB|GB|KB))", text)
    size = size_match.group(1) if size_match else None

    date_match = re.search(r"Date:\s([\d-]+\s[\d:]+)\sUTC", text)
    date = time.strptime(date_match.group(1), "%Y-%m-%d %H:%M") if date_match else None

    return size, date

class Tokyotosho(BasePlugin):
    abstract = False

    def __init__(self, parser: str = 'lxml', verify: bool = False, timefmt: str = r'%Y/%m/%d %H:%M') -> None:
        super().__init__(parser, verify, timefmt)

    def search(self, keyword: str, collected: bool = False, proxies: Optional[dict] = None,
               system_proxy: bool = False, **extra_options) -> List[Anime]:
        animes: List[Anime] = []
        page = 1
        params = {'terms': keyword, 'type': 1, **extra_options}

        if collected:
            log.warning("Tokyotosho search does not support collection.")

        while True:
            params['page'] = page
            url = BASE_URL + urlencode(params)
            try:
                html = get_html(url, verify=self._verify, proxies=proxies, system_proxy=system_proxy)
                bs = BeautifulSoup(html, self._parser)
                table = bs.find(class_='listing')

                if not table or not table.find(class_='category_0'):
                    break

                for row in list(zip(*[iter(table.find_all(class_='category_0'))]*2)):
                    top = row[0].find(class_='desc-top')
                    if not top:
                        continue
                    title = top.get_text(strip=True)
                    magnet = top.a['href'] if top.a else None

                    bottom = row[1].find(class_='desc-bot')
                    if not bottom:
                        continue
                    size, release_time = extract_info(bottom.text)
                    release_time = time.strftime(self._timefmt, release_time) if release_time else None

                    log.debug(f"Successfully got: {title}")

                    animes.append(Anime(release_time, title, size, magnet))

                page += 1

            except Exception as e:
                log.error(f"Error occurred while processing page {page}: {e}")
                break

        return animes
