import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning, ParserRejectedMarkup
import warnings
from urllib.parse import urljoin, urlparse
from .downloader import download_file
from .utils import colored
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from .tempMan import read_temp_file

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

base_url = None


def setBURL(temp_file_name):
    b_url = read_temp_file(temp_file_name)
    return b_url


def fetch_url(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(colored(f"[!] Error fetching {url}: {e}", "red"))
        return None


def extract_links(html, base_url):
    try:
        soup = BeautifulSoup(html, "lxml")  # Try using lxml parser
    except ParserRejectedMarkup:
        try:
            soup = BeautifulSoup(html, "html5lib")  # Try using html5lib parser
        except ParserRejectedMarkup:
            try:
                soup = BeautifulSoup(html, "html.parser")
            except ParserRejectedMarkup as e:
                print(f"Failed to parse HTML: {e}")
                return []
    return [urljoin(base_url, a.get("href")) for a in soup.find_all("a", href=True)]


def is_valid_extension(url, extensions):
    return any(url.lower().endswith(f".{ext.lower()}") for ext in extensions)


def crawl_and_download(
    config, url, visited=None, downloaded=None, depth=0, executor=None, tmp=None
):
    Burl = None
    if tmp:
        Burl = setBURL(tmp)
    try:
        if visited is None:
            visited = set()
        if downloaded is None:
            downloaded = set()
        if executor is None:
            executor = ThreadPoolExecutor(max_workers=5)

        if url in visited:
            return
        visited.add(url)

        html = fetch_url(url)
        if not html:
            return

        links = extract_links(html, url)
        if not links:
            print(colored("[x] No links found on this page.", "yellow"))
            return

        futures = []
        for link in links:
            if is_valid_extension(link, config["types"]) and link not in downloaded:
                downloaded.add(link)
                futures.append(executor.submit(download_file, link, config["output"]))

        for future in as_completed(futures):
            future.result()  # Raise exception if any occurred

        if config.get("depth") in [None, ""] or depth < int(config["depth"]):
            for link in links:
                if urlparse(link).netloc == urlparse(url).netloc and (
                    Burl is None or link.startswith(Burl)
                ):
                    crawl_and_download(
                        config, link, visited, downloaded, depth + 1, executor
                    )

        if depth == 0:
            print(colored("\n[✓] Crawl complete for:", "green"), url)

    except KeyboardInterrupt:
        print(colored("KeyboardInterrupt...", "red"))
        sys.exit()
