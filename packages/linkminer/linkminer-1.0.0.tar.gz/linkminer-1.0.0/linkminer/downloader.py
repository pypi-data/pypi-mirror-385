from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm
from .utils import colored


def get_filepath(file_url, output_dir):
    parsed_url = urlparse(file_url)
    path = parsed_url.path
    filename = os.path.basename(path)
    directory = os.path.dirname(path)

    # Create the directory structure in the output directory
    output_path = os.path.join(output_dir, directory.lstrip("/"))
    os.makedirs(output_path, exist_ok=True)

    # Join the output path with the filename
    filepath = os.path.join(output_path, filename)
    return filepath


def download_file(file_url, output_dir):
    filename = os.path.basename(urlparse(file_url).path)
    # filepath = os.path.join(output_dir, filename)
    filepath = get_filepath(file_url, output_dir)

    if os.path.exists(filepath):
        print("[•]", colored(f" Skipped (exists): {filepath}", "yellow"))
        return

    try:
        with requests.get(file_url, stream=True, timeout=15) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            with open(filepath, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename, leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        print(colored(f"[✓] Downloaded: {filepath}", "green"))
    except Exception as e:
        print(colored(f"[!] Failed to download {file_url}: {e}", "red"))


# Thread-safe print (for clean tqdm progress)
print_lock = Lock()


def async_download_file(file_url, output_dir):
    filename = os.path.basename(urlparse(file_url).path)
    filepath = os.path.join(output_dir, filename)

    if os.path.exists(filepath):
        with print_lock:
            print("[•]", colored(f" Skipped (exists): {filename}", "yellow"))
        return

    try:
        with requests.get(file_url, stream=True, timeout=15) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            with open(filepath, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename, leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

        with print_lock:
            print(colored(f"[✓] Downloaded: {filename}", "green"))
    except Exception as e:
        with print_lock:
            print(colored(f"[!] Failed to download {file_url}: {e}", "red"))


def download_files_concurrently(urls, output_dir, max_workers=4):
    """
    Download multiple files in parallel using threads.
    """
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(async_download_file, url, output_dir): url for url in urls
        }

        for future in as_completed(future_to_url):
            # Errors are handled inside download_file, so we just force completion
            _ = future.result()
