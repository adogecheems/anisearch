import copy
import csv
import time
from typing import List, Optional

from . import plugins
from . import *


class Searcher:
    def __init__(self, plugin_name: str = 'dmhy',
                 parser: Optional[str] = None, verify: Optional[bool] = None, timefmt: Optional[str] = None,
                 no_search_errors: bool = False):
        """
        Initialize Searcher object.

        Args:
        - plugin_name: Name of the plugin, default is 'dmhy'
        - parser: Name of the parser
        - verify: Whether to verify
        - timefmt: Time format
        """
        if no_search_errors:
            log.warning("Search errors will not be raised.")
            self.search = no_errors(self.search)

        self.reset()
        self.plugin = self._load_plugin(plugin_name, parser, verify, timefmt)
        log.debug("New searcher object created.")

    def _load_plugin(self, plugin_name, parser, verify, timefmt):
        kwargs = {}
        if parser is not None:
            kwargs['parser'] = parser
        if verify is not None:
            kwargs['verify'] = verify
        if timefmt is not None:
            self.set_timefmt(timefmt)
            kwargs['timefmt'] = self._timefmt

        plugin = plugins.get_plugin(plugin_name)(**kwargs)
        log.info(f"Successfully loaded plugin: {plugin_name}.")
        return plugin

    def set_timefmt(self, timefmt: str) -> None:
        """
        Set and validate the time format.

        Args:
        - timefmt: Time format string
        """
        time.strftime(timefmt, time.localtime())
        self._timefmt = timefmt

    def reset(self) -> None:
        """Reset the search object."""
        self.animes: List[Anime] | None = None
        self.anime: Anime | None = None
        self.if_selected: bool = False

    def search(self, keyword: str, collected: Optional[bool] = None, proxies: Optional[dict] = None,
               system_proxy: Optional[bool] = None, **extra_options) -> List[Anime] | None:
        """
        Search for anime using the given keyword.

        Args:
        - keyword: Search keyword
        - collected: Whether to collect results
        - proxies: Proxy settings
        - system_proxy: Whether to use system proxy

        Returns:
        - True if search is successful, False otherwise.
        """
        self.reset()

        kwargs = {'keyword': keyword}
        if collected is not None:
            kwargs['collected'] = collected
        if proxies:
            kwargs['proxies'] = proxies
        if system_proxy:
            kwargs['system_proxy'] = system_proxy
        kwargs.update(extra_options)

        try:
            self.animes = self.plugin.search(**kwargs)
        except Exception as e:
            log.info(f"Failed to search with the plugin: {self.plugin.name} with error: {e!r}.")
            self.animes = None
            raise

        log.info(f"This search is completed: {keyword}.")
        return self.animes

    def select(self, index: int) -> None:
        """
        Select an anime from the search results.

        Args:
        - index: Index of the anime in the results list
        """
        if not (0 <= index < len(self.animes)):
            raise IndexError("Invalid selection index.")

        self.anime = self.animes[index]
        self.if_selected = True

    def size_format(self, unit: str = 'MB') -> None:
        """
        Convert the size of the selected anime to the specified unit.

        Args:
        - unit: Target size unit, default is 'MB'
        """
        if not self.if_selected:
            raise ValueError("No item selected. Please use select() method first.")

        self.anime.size_format(unit)

    def size_format_all(self, unit: str = 'MB') -> None:
        """
        Convert the size of all anime in the search results to the specified unit.

        Args:
        - unit: Target size unit, default is 'MB'
        """
        try:
            animes = copy.deepcopy(self.animes)
            for anime in animes:
                anime.size_format(unit)
        except:
            raise
        else:
            self.animes = animes


    def save_csv(self, filename: str) -> None:
        """
        Save the selected anime details to a CSV file.

        Args:
        - filename: Name of the CSV file
        """
        fieldnames = ["time", "title", "size", "magnet"]

        try:
            with open(filename, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for anime in self.animes:
                    writer.writerow({
                        "time": anime.time,
                        "title": anime.title,
                        "size": anime.size,
                        "magnet": anime.magnet
                    })

        except Exception as e:
            log.error(f"Failed to save CSV file: {filename} with error: {e}.")
            raise SaveCSVError()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
