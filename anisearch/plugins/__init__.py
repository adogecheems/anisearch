import importlib
from abc import ABCMeta, abstractmethod

from .. import log


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
    def search(self, keyword, collected, proxies, system_proxy, **extra_options):
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
    except ImportError:
        log.info(f"The plugin {name} cannot be automatically imported, please import it manually")

    return PluginMeta.plugins.get(name.title())
