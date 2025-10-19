import argparse
import os
from .config import load_config
from .crawler import crawl_and_download
from .utils import print_banner, colored
from .tempMan import TempFileManager, read_temp_file, write_temp_file
from .crawler import setBURL

default_download = os.path.join(
    os.path.expanduser("~"), "Downloads/linkminer_downloads"
)


def get_links(arg):
    """Handle either a single URL or a file containing multiple URLs."""
    fpath = os.path.abspath(arg)
    if os.path.isfile(fpath) and fpath.endswith(".txt"):
        with open(fpath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return [arg]


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description=colored("Web Content Crawler + Downloader", "cyan")
    )
    parser.add_argument(
        "url",
        help="Starting URL to crawl, or path to .txt file of URLs",
    )
    parser.add_argument(
        "-t", "--types", nargs="+", help="File types to download (e.g. pdf mp4 jpg)"
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=None,
        help="Recursion depth limit (default: unlimited)",
    )
    parser.add_argument(
        "-o", "--output", default=default_download, help="Output directory"
    )
    parser.add_argument("-c", "--config", help="Path to config JSON file")

    args = parser.parse_args()
    config = load_config(args.config, args)

    print("[i]", colored(f" File types: {', '.join(config['types'])}", "green"))
    print("[i]", colored(f" Output dir: {config['output']}", "green"))
    print("[i]", colored(f" Depth limit: {config['depth'] or '∞'}", "green"))

    links = get_links(args.url)
    os.makedirs(config["output"], exist_ok=True)

    for link in links:
        if link.strip():
            if link.startswith("#"):
                continue
            with TempFileManager() as temp_file:
                temp_file_name = temp_file.name
                write_temp_file(temp_file_name, link)

                print("[i]", colored(f" Crawling: {link}", "cyan"))
                crawl_and_download(config, link, tmp=temp_file_name)


if __name__ == "__main__":
    main()
