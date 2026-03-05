# El País Opinion Scraper

Selenium + Pytest scraper that extracts articles from the **Opinion** section of [El País](https://elpais.com), translates titles to English, performs word-frequency analysis, and runs cross-browser tests on **BrowserStack** across 5 parallel threads.

## What It Does

1. **Opens El País** and verifies the site is displayed in Spanish
2. **Navigates to the Opinion section** and fetches the first 5 articles
3. **Scrapes each article's** title, body content (in Spanish), and downloads cover images
4. **Translates all titles** from Spanish → English using Google Translate (`deep-translator`)
5. **Analyses translated titles** for words repeated more than twice
6. **Runs cross-browser** on BrowserStack across 5 platforms in parallel

## Project Structure

```
.
├── main.py                      # CLI entry-point (--local / --browserstack)
├── testcases.py                 # Shared test class & helpers (all 5 test steps)
├── test_local_scraper.py        # Local test runner (headless Chrome)
├── test_browserstack_scraper.py # BrowserStack test runner (SDK-intercepted)
├── utils.py                     # Utilities: image download, translation, word count
├── browserstack.yml             # BrowserStack SDK config
├── conftest.py                  # Pytest config (test ordering)
├── pytest.ini                   # Suppresses Selenium deprecation warnings
├── requirements.txt             # Python dependencies
└── images/                      # Downloaded cover images (per-run subdirectories)
    ├── local_20260305_143022/   #   Local run (timestamped)
    └── bstack_abc123def456/     #   BrowserStack session (session ID)
```

| File                           | Purpose                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------ |
| `main.py`                      | CLI wrapper — pass `--local` or `--browserstack`                                                 |
| `testcases.py`                 | All scraping logic + `BaseTestElPaisScraper` with 5 test methods. Both runners inherit from this |
| `test_local_scraper.py`        | Defines headless Chrome driver, inherits test cases                                              |
| `test_browserstack_scraper.py` | Defines BrowserStack driver (SDK-intercepted), inherits test cases                               |
| `utils.py`                     | `download_image()`, `translate_text()`, `count_repeated_words()`                                 |
| `browserstack.yml`             | 5 platforms, 1 thread each = 5 parallel threads                                                  |

## BrowserStack Platforms

| #   | Platform                        | Browser         |
| --- | ------------------------------- | --------------- |
| 1   | Windows 11                      | Chrome (latest) |
| 2   | macOS Sonoma                    | Safari (latest) |
| 3   | Windows 11                      | Edge (latest)   |
| 4   | iPhone 14 (iOS 16)              | Safari          |
| 5   | Samsung Galaxy S23 (Android 13) | Chrome          |

## Prerequisites

- Python 3.9+
- Google Chrome + ChromeDriver (for local runs)
- BrowserStack account (for cross-browser runs)

## Installation

```bash
git clone https://github.com/imhxrsh/elpais-scraper.git
cd elpais-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Set your BrowserStack credentials as environment variables:

```bash
export BROWSERSTACK_USERNAME="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"
```

## Usage

### Run Locally

```bash
python main.py --local
# or directly
pytest -s -v test_local_scraper.py
```

### Run on BrowserStack

```bash
python main.py --browserstack
# or directly
browserstack-sdk pytest -s -v test_browserstack_scraper.py
```

## Test Cases

Each test is reported individually (5 tests × 5 platforms = 25 results on BrowserStack):

| Test                                            | Validates                                                   |
| ----------------------------------------------- | ----------------------------------------------------------- |
| `test_1_website_is_in_spanish`                  | `<html lang="es-…">` is present                             |
| `test_2_navigate_to_opinion_and_fetch_articles` | Opinion page loads, ≥1 article found with valid title & URL |
| `test_3_scrape_content_and_download_images`     | Article body scraped, cover images downloaded               |
| `test_4_translate_titles_to_english`            | All titles translated, no empty translations                |
| `test_5_analyze_repeated_words`                 | Word frequency analysis returns valid results               |

## Output

- Article titles and content printed to console
- Cover images saved to separate folders per run (no overwrites):
    - Local: `images/local_20260305_143022/`
    - BrowserStack: `images/bstack_<session_id>/` (one folder per parallel browser)
- Translated titles and word counts printed at end of run
- BrowserStack results visible on the [Automate Dashboard](https://automate.browserstack.com/)
