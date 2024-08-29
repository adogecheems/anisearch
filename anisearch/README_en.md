# Anisearch

anisearch is a full-featured Python library for searching anime magnet links. It also provides a flexible plugin system that allows users to search animation information from different sources

## Features

- Support multiple search sources
- Powerful extensibility
- CSV export function
- Proxy support

## Installation

You can install anisearch directly using pip:

```
pip install Anisearch-lib
```

## Usage example

Here is a basic example of using anisearch:

```python
from anisearch import AniSearch

# Create an AniSearch instance
searcher = AniSearch()

# Optional parameters for the __init__() method:
# plugin_name: Search source name, defaults to 'dmhy'
# parser: beautifulsoup parser, defaults to 'lxml' in 'dmhy'
# verify: Whether to verify SSL certificates, defaults to False in 'dmhy'
# time_fmt: Time format, defaults to '%Y-%m-%d %H:%M:%S'

# The default values of the above parameters may be different when different plug-ins are selected

# Search animation
searcher.search('我推的孩子')

# Optional parameters of the search() method:
# collected: Whether to search only quarterly collections, default is True
# proxies: proxy url
#
# Use proxy
# proxies = {
# 'http': 'http://10.10.1.10:3128',
# 'https': 'http://10.10.1.10:1080',
# } # Don't take it seriously, it's just an example
# searcher.search("我推的孩子", proxies=proxies)
# system_proxy: Whether to use system proxy (it seems that it always doesn't work)

# If the search is successful, the following words will appear:
# This search is complete: 我推的孩子

# Output search result list
print(searcher.animes)

# Show partial output (results in August 2024)
# [Anime('2024/03/21 13:25', '【动漫国字幕组】[【我推的孩子】][01-11][BDRip][AVC_AAC][1080P][Simplified][MP4]', '7.3GB', 'magnet:?xt=urn:btih:P76PROAB5JRUAPHIST63HGRUOMW7SEWU&dn=&tr=...

# If everything is OK, select the first search result (you can also select others)

searcher.select(0)

# After selection, the anime attribute is available
print(searcher.anime.title)
print(searcher.anime.size)

# Output:
# '【动漫国字幕组】[【我推的孩子】][01-11][BDRip][AVC_AAC][1080P][Simplified][MP4]'
# '7.3GB'
```

## Main components

### AniSearch class

`AniSearch` is the main search class, providing the following methods:

- `search(keyword, collected=None, proxies=None, system_proxy=None, **extra_options)`: Search for animations

- `select(index)`: Select an animation from the search results

- `size_format(unit='MB')`: Convert the file size of the selected animation

- `save_csv(filename)`: Save the search results to a CSV file (all results)

** The extra_options parameter will be incorporated into the query string during crawling, which can be used to specify additional categories or options. For specific query strings, please check the search source search. url

![querystring](https://cdn.mmoe.work/img/url.png)

### Anime class

The `Anime` class represents an anime entry and contains the following properties:

- `time`: release time
- `title`: animation title
- `size`: file size
- `magnet`: magnet link

Its __eq__ method is implemented to compare the hash values ​​of the magnet links of two Anime instances.

### Plugin system

AniSearch uses a metaclass-based plugin system to support different search sources

### Implemented plugins

- `dmhy`: Anime Garden search source (faster)

- `comicat`: Manmao search source (very slow to implement, use with caution, it is recommended to search only for quarterly collections)

- `kisssub`: Love search source (same as above)

- `miobt`: MioBT search source (same as above)

- `nyaa`: nyaa.si search source (superb speed, can not use quarterly collection search)

- `acgrip`: acg.rip search source (moderate speed, can not use quarterly collection search, due to the site's own reasons, the magnet obtained is the download link of the seed)

- `tokyotosho`: Tokyo Library search source (moderate speed, cannot use quarterly collection search)

## Create a custom plugin
To create a custom plugin, you need to inherit the BasePlugin class and implement the search method. Anisearch provides a practical http request function `anisearch.plugins._webget.get_html()`, which can be used directly. Here is a simple example:

```python
# Run this code. If there is no exception, it means that the custom plug-in is created successfully and has been registered in the plug-in system
from anisearch.plugins import BasePlugin
from anisearch.anime.Anime import Anime
from anisearch.plugins._webget import get_html

class Custom(BasePlugin):
    abstract = False

    def __init__(self, parser, verify, timefmt) -> None:
        super().__init__(parser, verify, timefmt)
    
    def search(self, keyword, collected=True, proxies=None, system_proxy=False, **extra_options):
        html = get_html("<url>", proxies=proxies, system_proxy=system_proxy, verify=self._verify)
        
        # Implement your search logic here
        
        # Return a list of Anime objects
        return [Anime("2023/06/01 12:00", "Custom Anime", "1.5GB", "magnet:?xt=urn:btih:..."), ...]
```

### Example of using a custom plugin

```python
searcher_custom = AniSearch(plugin_name='custom')

# If the file is not placed in the project plugins directory, you need to manually import it to the namespace

# Please make sure to keep the class name (comply with the pep8 naming convention), plugin name, and file name consistent, and the case will be automatically processed

searcher_custom.search("我推孩子")

```

## Command line interface (CLI) usage

anisearch comes with a command line interface that can be used directly in the terminal.

### Basic usage

```
anisearch -k <keyword> [options]
```

### Parameter description

- `-k`, `--keyword`: (required) Search keyword

- `-p`, `--plugin`: (optional) Search plugin, default is `dmhy`

- `-c`, `--collected`: (optional) Whether to search only quarterly collections

### Example

1. Basic search:

```
anisearch -k "我推的孩子"
```

2. Search using a specific search plugin:

```
anisearch -k "我推的孩子" -p nyaa
```

### Usage process

1. After running the search command, the program will display a list of search results, including serial number, title and file size
2. Users can enter the serial number of the item they want to select
3. If a valid serial number is selected, the program will display the title and magnet link of the selected item
4. Enter 0 Can opt out of the selection process

## Contributions

Contributions are welcome! Please feel free to submit pull requests or open issues to improve this project

## License

AGPLv3