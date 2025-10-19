# 📚 Link Miner

**Linkminer** is a command-line tool that recursively crawls a website and downloads files of specified types (e.g., PDFs, videos, documents). Originally built to fetch KCSE past papers, it's now a general-purpose file scraper.

---

## 🚀 Features

- 🎯 Download specific file types (`.pdf`, `.mp4`, `.docx`, etc.)
- 🔁 Recursive crawling with configurable depth
- ⚙ Supports config files and CLI arguments
- 💾 Skips files that already exist
- 🎨 ASCII banner + colorized output for a better UX

---

## 📦 Installation

### 🔧 From source:

```bash
git clone https://github.com/skye-cyber/kcse-fetcher.git
cd kcse-fetcher
pip install .
```
**OR**
```bash
pip install linkminer
```
---
## 🧪 Usage
🔹 Basic (CLI only):


python -m kcse_fetcher https://example.com --types pdf mp4 --depth 2


🔹 Using a config file:

```json
{
  "url": "https://example.com",
  "types": ["pdf", "mp4"],
  "depth": 3,
  "output": "downloads"
}
```
- Then Run:
```bash
python -m kcse_fetcher -c config.json
```
---
## ⚙ Options
Option	Description
url	Starting URL to crawl
--types	File extensions to download
--depth	Max recursion depth (None = no limit)
--output	Output directory
--config	Path to JSON config file

---
## 🛠 Example Output
```less
[i] Crawling: https://example.com
[i] File types: pdf, mp4
[i] Output dir: downloads
[i] Depth limit: 2

[✓] Downloaded: kcse_2021_english.pdf
[✓] Downloaded: kcse_2021_kiswahili.pdf
[•] Skipped (exists): kcse_2021_chemistry.pdf
```

---
## 📘 License
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
  See the LICENSE file for more details. See the [LICENSE](LICENSE) file for details.
  
---
## 💡 Author
``Skye - Wambua``
- Made with 💻 and ☕ in Kenya


---
