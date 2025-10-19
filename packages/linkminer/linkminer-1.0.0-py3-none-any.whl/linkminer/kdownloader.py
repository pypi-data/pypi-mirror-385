import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# Match patterns like "2021 K.C.S.E Past Papers" or "K.C.S.E 2019 Papers"
TARGET_PATTERN = re.compile(
    r"\b(20[0-2][0-9]|19[9-9][0-9])\b.*\bK\.?C\.?S\.?E\b.*\bPast Papers\b",
    re.IGNORECASE,
)


def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"[!] Failed to fetch: {url} ({e})")
        return None


def find_all_past_paper_links(base_url):
    print(f"[i] Searching for 'K.C.S.E Past Papers' links on: {base_url}")
    soup = get_soup(base_url)
    if not soup:
        return []

    links = []
    for a in soup.find_all("a", href=True):
        text = a.get_text(strip=True)
        if TARGET_PATTERN.search(text):
            full_url = urljoin(base_url, a["href"])
            links.append((text, full_url))

    print(f"[+] Found {len(links)} matching year-specific past paper pages.")
    return links


def extract_pdf_links(page_url):
    soup = get_soup(page_url)
    if not soup:
        return []

    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            pdf_links.append(urljoin(page_url, href))
    return pdf_links


def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def download_pdf(pdf_url, output_dir):
    filename = sanitize_filename(os.path.basename(urlparse(pdf_url).path))
    output_path = os.path.join(output_dir, filename)

    if os.path.exists(output_path):
        print(f"[•] Already downloaded: {filename}")
        return

    try:
        with requests.get(pdf_url, stream=True, headers=HEADERS, timeout=15) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            with open(output_path, "wb") as f, tqdm(
                total=total_size, unit="B", unit_scale=True, desc=filename, leave=False
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))
        print(f"[✓] Downloaded: {filename}")
    except Exception as e:
        print(f"[!] Failed to download {pdf_url} ({e})")


def main(base_url):
    paper_pages = find_all_past_paper_links(base_url)
    if not paper_pages:
        print("[x] No past paper links found. Exiting.")
        return

    for label, link in paper_pages:
        print(f"\n[→] Scraping papers from: {label}")
        year_match = re.search(r"20\d{2}|19\d{2}", label)
        year_folder = (
            f"kcse_papers_{year_match.group()}" if year_match else "kcse_papers_misc"
        )
        os.makedirs(year_folder, exist_ok=True)

        pdfs = extract_pdf_links(link)
        print(f"[+] Found {len(pdfs)} PDF(s)")

        for pdf_url in pdfs:
            download_pdf(pdf_url, year_folder)

    print("\n[✓] All downloads complete.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python kdownloader.py <website_url>")
        sys.exit(1)

    main(sys.argv[1])
