import importlib
from abc import ABCMeta, abstractmethod


class PluginMeta(ABCMeta):
    plugins = {}

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not getattr(cls, 'abstract'):
            PluginMeta.plugins[name] = cls


class BasePlugin(metaclass=PluginMeta):
    abstract = True

    @abstractmethod
    def search(self, keyword, proxies, system_proxy):
        """
        Abstract method to search for a keyword.

        Args:
        - keyword: Search keyword
        - proxies: Proxy settings
        - system_proxy: Whether to use system proxy
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
    importlib.import_module(f".{name}", package=__name__)
    return PluginMeta.plugins.get(name.title())
