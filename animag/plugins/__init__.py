import importlib
from abc import ABCMeta, abstractmethod
from typing import List, Optional

from .. import log
from ..Anime import Anime


class PluginMeta(ABCMeta):
    plugins = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not getattr(cls, 'abstract'):
            PluginMeta.plugins[name] = cls


class BasePlugin(metaclass=PluginMeta):
    abstract = True

    def __init__(self, parser, verify, timefmt):
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    @abstractmethod
    def search(self, keyword: str, collected: bool, proxies: Optional[dict],
               system_proxy: bool, **extra_options) -> List[Anime]:
        """
        Abstract method to search for a keyword.

        Args:
        - keyword: Search keyword
        - collected: Collected data
        - proxies: Proxy settings
        - system_proxy: Whether to use system proxy
        - extra_options: Extra options for the search engine
        """
        pass


def get_plugin(name: str):
    """
    Get a plugin by its name.

    Args:
    - name: Name of the plugin

    Returns:
    - Plugin class if found, otherwise None
    """
    try:
        importlib.import_module(f".{name}", package=__name__)
    except ImportError as e:
        log.exception(f"The plugin {name} cannot be imported, maybe you must import it manually.")
        raise e
    except Exception as e:
        log.critical(f"Failed to load plugin {name} with unknown reasons: {e}.")
        raise e

    return PluginMeta.plugins.get(name.title())
