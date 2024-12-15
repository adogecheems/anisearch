import importlib
from abc import ABCMeta, abstractmethod
from typing import List

from .. import *


class PluginMeta(ABCMeta):
    plugins = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not getattr(cls, 'abstract'):
            PluginMeta.plugins[name] = cls
            cls.name = name


class BasePlugin(metaclass=PluginMeta):
    abstract = True

    def __init__(self,
                 parser: Optional[str] = None,
                 verify: Optional[bool] = None,
                 timefmt: Optional[str] = None):
        self._parser = parser
        self._verify = verify
        self._timefmt = timefmt

    @abstractmethod
    def search(self, keyword: str,
               collected: Optional[bool] = None,
               proxies: Optional[dict] = None,
               system_proxy: Optional[bool] = None,
               **extra_options) -> List[Anime] | None:
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
    except:
        raise PluginImportError(f"The plugin {name} cannot be imported, maybe you must import it manually.")

    return PluginMeta.plugins.get(name.title())
