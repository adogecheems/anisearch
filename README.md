# Anisearch

anisearch 是一个功能齐全的 Python 库，用于搜索动画磁力链接。它还提供了一个灵活的插件系统，允许用户从不同的来源搜索动画信息

## 功能特点

- 支持多个搜索源
- 强大的可扩展性
- CSV 导出功能
- 代理支持

## 安装

你可以直接使用 pip 安装 anisearch：

```
pip install Anisearch-lib
```

## 使用示例

以下是使用 anisearch 的基本示例：

```python
from anisearch import AniSearch

# 创建 AniSearch 实例
searcher = AniSearch()

# __init__()方法可选的参数：
# plugin_name: 搜索源名称，默认为 'dmhy'
# parser: beautifulsoup 解析器，在'dmhy'中默认为'lxml'
# verify: 是否验证 SSL 证书，在'dmhy'中默认为False
# time_fmt: 时间格式，默认为'%Y-%m-%d %H:%M:%S'

# 以上参数的默认值在选择不同的插件的时候可能会有所不同

# 搜索动画
searcher.search('我推的孩子')

# search()方法可选的参数：
# collected: 是否只搜索季度合集，默认为True
# proxies: 代理url
#
# 使用代理
# proxies = {
#     'http': 'http://10.10.1.10:3128',
#     'https': 'http://10.10.1.10:1080',
# } # 别当真，就是示例而已
# searcher.search("我推的孩子", proxies=proxies)
# system_proxy: 是否使用系统代理(好像总是不能工作)

# 搜索成功的话会出现如下字样:
# This search is complete: 我推的孩子

# 输出搜索结果列表
print(searcher.animes)

# 展示部分输出（在2024年八月的结果）
# [Anime('2024/03/21 13:25', '【动漫国字幕组】[【我推的孩子】][01-11][BDRip][AVC_AAC][1080P][简体][MP4]', '7.3GB', 'magnet:?xt=urn:btih:P76PROAB5JRUAPHIST63HGRUOMW7SEWU&dn=&tr=...

# 如果一切正常，选择第一个搜索结果（当然也可以选择其他的）
searcher.select(0)

# 选择后anime属性可用
print(searcher.anime.title)
print(searcher.anime.size)

# 输出：
# '【动漫国字幕组】[【我推的孩子】][01-11][BDRip][AVC_AAC][1080P][简体][MP4]'
# '7.3GB'
```

## 主要组件

### AniSearch 类

`AniSearch` 是主要的搜索类，提供以下方法：

- `search(keyword, collected=None, proxies=None, system_proxy=None, **extra_options)`: 搜索动画
- `select(index)`: 从搜索结果中选择一个动画
- `size_format(unit='MB')`: 转换选定动画的文件大小
- `save_csv(filename)`: 将搜索结果保存到 CSV 文件（所有结果）

** extra_options 参数会被并入爬取时的查询字符串中，可以用于指定额外的分类或选项，具体的查询字符串请自行查看搜索源搜索时的 url

![查询字符串](https://cdn.mmoe.work/img/url.png)

### Anime 类

`Anime` 类代表一个动画条目，包含以下属性：

- `time`: 发布时间
- `title`: 动画标题
- `size`: 文件大小
- `magnet`: 磁力链接

其__eq__方法被实现为比较两个 Anime 实例磁力链接的哈希值。

### 插件系统

AniSearch 使用基于元类的插件系统来支持不同的搜索源插件系统来支持不同的搜索源

### 已实现的插件

- `dmhy`: 动漫花园搜索源（需要代理，速度较快）
- `comicat`: 漫猫搜索源（实现很慢，慎用）
- `kisssub`: 爱恋搜索源（实现很慢，慎用，需要代理）
- `miobt`：MioBT 搜索源（实现很慢，慎用，需要代理）
- `nyaa`: nyaa.si 搜索源（需要代理，速度超群，不能使用季度合集搜索）
- `acgrip`: acg.rip 搜索源（需要代理，速度适中，不能使用季度合集搜索，由于站点的自身原因，获取的magnet是种子的下载链接）

## 创建自定义插件
要创建自定义插件，您需要继承 BasePlugin 类并实现 search 方法，anisearch 提供了一个实用的http请求函数 `anisearch.plugins._webget.get_html()`，可以直接使用。以下是一个简单的示例：

```python
# 运行此代码，没有异常说明自定义插件创建成功，已经注册在插件系统中
from anisearch.plugins import BasePlugin
from anisearch.anime.Anime import Anime
from anisearch.plugins._webget import get_html

class Custom(BasePlugin):
    abstract = False
    
    def __init__(self, parser, verify, timefmt) -> None:
        super().__init__(parser, verify, timefmt)

    def search(self, keyword, if_collected=True, proxies=None, system_proxy=False, **extra_options):
        html = get_html("<url>", proxies=None, system_proxy=False, verify=True)
        
        # 这里实现您的搜索逻辑
        
        # 返回一个 Anime 对象的列表
        return [Anime("2023/06/01 12:00", "Custom Anime", "1.5GB", "magnet:?xt=urn:btih:..."), ...]
```

### 使用自定义插件示例

```python
searcher_custom = AniSearch(plugin_name='custom')

# 如果文件没有放在项目plugins目录下，需要手动引入模块
# 请务必将类名（遵守pep8命名规范）、插件名、文件名保持一致，大小写会自动处理

searcher_custom.search("我推的孩子")
```

## 命令行界面（CLI）使用

anisearch 附赠了一个命令行界面，可以直接在终端中使用。

### 基本用法

```
anisearch -k <关键词> [选项]
```

### 参数说明

- `-k`, `--keyword`: (必需) 搜索关键词
- `-p`, `--plugin`: (可选) 搜索插件，默认为 `dmhy`
- `-n`, `--not-collected`: (可选) 不启用默认的季度全集搜索

### 示例

1. 基本搜索：

```
anisearch -k "我推的孩子"
```

2. 使用特定搜索插件搜索：

```
anisearch -k "我推的孩子" -p nyaa
```

### 使用流程

1. 运行搜索命令后，程序会显示搜索结果列表，包括序号、标题和文件大小
2. 用户可以输入想要选择的项目的序号
3. 如果选择了有效的序号，程序会显示所选项目的标题和磁力链接
4. 输入 0 可以退出选择过程

## 贡献

欢迎贡献！请随时提交 pull requests 或开启 issues 来改进这个项目

## 许可证

AGPLv3