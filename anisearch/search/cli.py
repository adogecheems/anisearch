import argparse
from typing import Dict, Any

from rich.console import Console
from rich.table import Table

from .AniSearch import AniSearch

console = Console()


def search(search_params: Dict[str, Any]) -> AniSearch:
    try:
        searcher = AniSearch()
        searcher.search(**search_params)
        return searcher
    except Exception as e:
        console.print(f"[bold red]搜索出错: {str(e)}[/bold red]")
        return None


def print_results(searcher: AniSearch) -> None:
    if not searcher.animes:
        console.print("[bold yellow]搜索结果为空[/bold yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("序号", style="dim", justify="right", width=4)
    table.add_column("标题", style="dim", width=60, overflow="fold")
    table.add_column("大小", style="cyan", justify="right", width=10)

    for idx, anime in enumerate(searcher.animes, start=1):
        table.add_row(str(idx), anime.title, anime.size)

    console.print(table)


def get_user_selection(max_index: int) -> int:
    while True:
        try:
            index = int(input("选择一个并输入其序号 (输入 0 退出): "))
            if 0 <= index <= max_index:
                return index
            console.print(f"[bold red]请输入 0 到 {max_index} 之间的数字[/bold red]")
        except ValueError:
            console.print("[bold red]请输入有效的数字[/bold red]")


def handle_search(args: argparse.Namespace) -> None:
    search_params = {'keyword': args.keyword}
    if args.collected is not None:
        search_params['collected'] = args.collected

    searcher = search(search_params)
    if searcher and searcher.animes:
        print_results(searcher)
        selection = get_user_selection(len(searcher.animes))
        if selection > 0:
            index = selection - 1
            searcher.select(index)

            console.print(f"[bold green]已选择 {searcher.anime.title}[/bold green]")
            console.print(f"[bold green]其磁链为: [/bold green][bold yellow]{searcher.anime.magnet}[/bold yellow]")
        else:
            console.print("[bold yellow]已退出选择[/bold yellow]")
    elif searcher is None:
        console.print("[bold red]搜索失败，无法进行选择[/bold red]")
    else:
        console.print("[bold yellow]搜索结果为空[/bold yellow]")


def main() -> None:
    parser = argparse.ArgumentParser(description="动漫磁力搜索工具:")
    subparsers = parser.add_subparsers(dest='command')

    search_parser = subparsers.add_parser('search',
                                          help='搜索动漫磁链，不知道可用的参数请参阅https://github.com/adogecheems/anisearch'
                                          )
    search_parser.add_argument('-p', '--plugin', type=str, help='搜索使用的插件', default='dmhy')
    search_parser.add_argument('-k', '--keyword', type=str, help='搜索关键词', required=True)
    search_parser.add_argument('-c', '--collected', type=bool, help='是否只在季度全集里搜索')

    args = parser.parse_args()

    if args.command == 'search':
        handle_search(args)
    else:
        parser.print_help()
