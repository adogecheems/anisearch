import copy
import csv
import time
from typing import List, Dict, Any

from . import *
from . import plugins


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
        self.timefmt: Optional[str] = None
        self.animes: List[Anime] | None = None
        self.anime: Anime | None = None

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
            self.settimefmt(timefmt)
            kwargs['timefmt'] = self.timefmt

        plugin = plugins.get_plugin(plugin_name)(**kwargs)

        log.info(f"Successfully loaded plugin: {plugin_name}")
        return plugin

    def settimefmt(self, timefmt: str) -> None:
        """
        Set and validate the time format.

        Args:
            timefmt: Time format string

        Raises:
            TimeFormatError: If time format is invalid
        """
        try:
            time.strftime(timefmt, time.localtime())
        except Exception as e:
            raise TimeFormatError(f"Invalid time format {timefmt} : {e!r}")

        self.timefmt = timefmt

        if self.animes is not None:
            for anime in self.animes:
                anime.set_timefmt(timefmt)

    def search(self, keyword: str,
               collected: Optional[bool] = None,
               proxies: Optional[dict] = None,
               system_proxy: Optional[bool] = None,
               **extra_options) -> List[Anime] | None:
        """
        Search for anime using the given keyword.

        Args:
            keyword: Search keyword
            collected: Whether to collect results
            proxies: Proxy settings
            system_proxy: Whether to use system proxy
            **extra_options: Additional search options (as param strings)

        Returns:
            List of found animes or None if search fails

        Raises:
            SearchRequestError: If search request fails
            SearchParseError: If search result parsing fails
        """
        self.animes = None

        kwargs = {
            'keyword': keyword,
            **({} if collected is None else {'collected': collected}),
            **({} if not proxies else {'proxies': proxies}),
            **({} if system_proxy is None else {'system_proxy': system_proxy}),
            **extra_options
        }

        try:
            self.animes = self.plugin.search(**kwargs)
        except Exception as e:
            log.error(f"Search failed for '{keyword}': {e!r}")
            raise
        else:
            log.info(f"Search completed successfully: {keyword}")

        return self.animes

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
            raise ValueError("No search results available.")

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
            raise ValueError("No search results available.")

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
            raise SaveCSVError(f"Failed to save CSV file '{filename}': {e!r}")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
