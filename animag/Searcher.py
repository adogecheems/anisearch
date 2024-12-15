import copy
import csv
import time
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from . import plugins
from . import *


class Searcher:
    def __init__(self, plugin_name: str = 'dmhy',
                 parser: Optional[str] = None,
                 verify: Optional[bool] = None,
                 timefmt: Optional[str] = None,
                 no_search_errors: bool = False) -> None:
        """
        Initialize Searcher object.

        Args:
            plugin_name: Name of the plugin, default is 'dmhy'
            parser: Name of the parser
            verify: Whether to verify
            timefmt: Time format
            no_search_errors: If True, search errors will be suppressed

        Raises:
            ValueError: If time format is invalid
            PluginImportError: If plugin is not found
        """
        self._timefmt: Optional[str] = None
        self.animes: List[Anime] | None = None
        self.anime: Anime | None = None
        self.if_selected: bool = False

        if no_search_errors:
            log.warning("Search errors will not be raised.")
            self.search = no_errors(self.search)

        self.plugin = self._load_plugin(plugin_name, parser, verify, timefmt)
        log.debug("New searcher object created.")

    def _load_plugin(self, plugin_name: str,
                     parser: Optional[str],
                     verify: Optional[bool],
                     timefmt: Optional[str]) -> Any:
        """Load and configure the search plugin."""
        kwargs: Dict[str, Any] = {}

        if parser is not None:
            kwargs['parser'] = parser
        if verify is not None:
            kwargs['verify'] = verify
        if timefmt is not None:
            self.set_timefmt(timefmt)
            kwargs['timefmt'] = self._timefmt

        plugin = plugins.get_plugin(plugin_name)(**kwargs)

        log.info(f"Successfully loaded plugin: {plugin_name}")
        return plugin

    def set_timefmt(self, timefmt: str) -> None:
        """
        Set and validate the time format.

        Args:
            timefmt: Time format string

        Raises:
            ValueError: If time format is invalid
        """
        time.strftime(timefmt, time.localtime())
        self._timefmt = timefmt

    def reset(self) -> None:
        """Reset the search object to initial state."""
        self.animes = None
        self.anime = None
        self.if_selected = False

    @contextmanager
    def _handle_search_error(self, keyword: str):
        """Context manager for handling search errors."""
        try:
            yield
        except Exception as e:
            log.error(f"Search failed for '{keyword}': {e!r}")
            self.reset()
            raise
        else:
            log.info(f"Search completed successfully: {keyword}")

    def search(self, keyword: str,
               collected: Optional[bool] = None,
               proxies: Optional[dict] = None,
               system_proxy: Optional[bool] = None,
               **extra_options) -> Optional[List[Anime]]:
        """
        Search for anime using the given keyword.

        Args:
            keyword: Search keyword
            collected: Whether to collect results
            proxies: Proxy settings
            system_proxy: Whether to use system proxy
            **extra_options: Additional search options

        Returns:
            List of found animes or None if search fails

        Raises:
            SearchRequestError: If search request fails
            SearchParseError: If search result parsing fails
        """
        self.reset()

        kwargs = {
            'keyword': keyword,
            **({} if collected is None else {'collected': collected}),
            **({} if not proxies else {'proxies': proxies}),
            **({} if system_proxy is None else {'system_proxy': system_proxy}),
            **extra_options
        }

        with self._handle_search_error(keyword):
            self.animes = self.plugin.search(**kwargs)
            return self.animes

    def select(self, index: int) -> None:
        """
        Select an anime from the search results.

        Args:
            index: Index of the anime in the results list

        Raises:
            IndexError: If index is out of range
            ValueError: If no search results exist
        """
        if self.animes is None:
            raise ValueError("No search results available")

        if not (0 <= index < len(self.animes)):
            raise IndexError(f"Index {index} is out of range")

        self.anime = self.animes[index]
        self.if_selected = True

    def size_format(self, unit: str = 'MB') -> None:
        """
        Convert the size of the selected anime to the specified unit.

        Args:
            unit: Target size unit, default is 'MB'

        Raises:
            ValueError: If no item is selected
            SizeFormatError: If size format fails
        """
        if not self.if_selected or self.anime is None:
            raise ValueError("No item selected")

        self.anime.size_format(unit)

    def size_format_all(self, unit: str = 'MB') -> None:
        """
        Convert the size of all anime in the search results to the specified unit.

        Args:
            unit: Target size unit, default is 'MB'

        Raises:
            ValueError: If no search results exist
            SizeFormatError: If size format fails
        """
        if self.animes is None:
            raise ValueError("No search results available")

        try:
            formatted_animes = copy.deepcopy(self.animes)
            for anime in formatted_animes:
                anime.size_format(unit)
        except:
            raise
        else:
            self.animes = formatted_animes

    def save_csv(self, filename: str) -> None:
        """
        Save the search results to a CSV file.

        Args:
            filename: Name of the CSV file

        Raises:
            ValueError: If no search results exist
            SaveCSVError: If saving fails
        """
        if self.animes is None:
            raise ValueError("No search results available")

        fieldnames = ["time", "title", "size", "magnet"]

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
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
            log.error(f"Failed to save CSV file '{filename}': {e!r}")
            raise SaveCSVError()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
