import os
import re
import requests
from collections import Counter
from deep_translator import GoogleTranslator

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ─────────────────────────────────────────────────────────────
# Wait helpers
# ─────────────────────────────────────────────────────────────

def wait_for_element(driver, by, locator, timeout=10):
    """Wait until a single element is present."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, locator))
    )


def wait_for_elements(driver, by, locator, timeout=10):
    """Wait until multiple elements are present."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((by, locator))
    )


def wait_for_clickable(driver, by, locator, timeout=10):
    """Wait until element is clickable."""
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, locator))
    )


def wait_for_page_load(driver, timeout=10):
    """Wait until page fully loads."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


# ─────────────────────────────────────────────────────────────
# Cookie / popup handling
# ─────────────────────────────────────────────────────────────

def accept_cookies(driver):
    """Dismiss Didomi + El País cookie popup if present."""
    locators = [
        (By.ID, "didomi-notice-agree-button"),
        (By.XPATH, "//button[contains(text(),'ACEPTAR') or contains(text(),'Aceptar')]"),
    ]

    for locator in locators:
        try:
            wait_for_clickable(driver, locator[0], locator[1], timeout=5).click()
            break
        except Exception:
            continue


# ─────────────────────────────────────────────────────────────
# Image helpers
# ─────────────────────────────────────────────────────────────

def _get_image_url(el):
    """Extract image URL from img/srcset/picture."""
    selectors = ["img", "picture source"]

    for sel in selectors:
        try:
            node = el.find_element(By.CSS_SELECTOR, sel)

            src = node.get_attribute("src") or node.get_attribute("data-src")
            if src and "data:image" not in src and "blank.png" not in src:
                return src

            srcset = node.get_attribute("srcset")
            if srcset:
                return srcset.split(",")[0].strip().split(" ")[0]

        except Exception:
            continue

    return None


def download_image(url, dest_folder, filename):
    """Download image from URL."""
    if not url:
        return None

    os.makedirs(dest_folder, exist_ok=True)
    path = os.path.join(dest_folder, filename)

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        with open(path, "wb") as f:
            f.write(resp.content)

        print(f"  [image] Saved: {path}")
        return path

    except Exception as e:
        print(f"  [image] Failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# Article scraping
# ─────────────────────────────────────────────────────────────

def fetch_articles(driver, limit=5):
    """Return up to `limit` articles from the page."""
    wait_for_elements(driver, By.CSS_SELECTOR, "article")

    articles = []

    for el in driver.find_elements(By.CSS_SELECTOR, "article"):
        if len(articles) >= limit:
            break

        try:
            link = el.find_element(By.CSS_SELECTOR, "h2 a")
            title = link.text.strip()
            url = link.get_attribute("href")

            if not title or not url:
                continue

            articles.append({
                "title": title,
                "url": url,
                "image_url": _get_image_url(el),
            })

        except Exception:
            continue

    return articles


def get_article_content(driver, url):
    """Open article in new tab and extract content + cover image."""
    driver.execute_script("window.open(arguments[0]);", url)
    driver.switch_to.window(driver.window_handles[-1])

    wait_for_page_load(driver)
    accept_cookies(driver)

    # Article body
    paragraphs = driver.find_elements(By.CSS_SELECTOR, "article .a_c p")
    if not paragraphs:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")

    content = "\n".join(
        p.text.strip() for p in paragraphs if p.text.strip()
    )

    # Cover image
    image_url = None
    selectors = ["article img", "figure img", "picture source"]

    for sel in selectors:
        try:
            node = driver.find_element(By.CSS_SELECTOR, sel)

            src = node.get_attribute("src") or node.get_attribute("data-src")
            if src and "data:image" not in src and "blank.png" not in src:
                image_url = src
                break

            srcset = node.get_attribute("srcset")
            if srcset:
                image_url = srcset.split(",")[0].strip().split(" ")[0]
                break

        except Exception:
            continue

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return content, image_url


# ─────────────────────────────────────────────────────────────
# Translation
# ─────────────────────────────────────────────────────────────

def translate_text(text, source="es", target="en"):
    """Translate text using Google Translate."""
    try:
        return GoogleTranslator(source=source, target=target).translate(text) or text
    except Exception as e:
        print(f"  [translate] Error: {e}")
        return text


# ─────────────────────────────────────────────────────────────
# Word analysis
# ─────────────────────────────────────────────────────────────

STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "by","from","is","are","was","were","be","been","have","has","had",
    "do","does","did","will","would","could","should","may","might","can",
    "that","this","it","its","not","no","as","if","than","he","she",
    "they","we","you","my","your","his","her","our","their","who","what",
    "which","so","about","into","over","after","before","between",
    "under","up",
}


def count_repeated_words(headers, min_count=3):
    """Return words repeated >= min_count times."""
    words = []

    for h in headers:
        tokens = re.findall(r"[a-zA-Z]+", h.lower())
        words.extend(
            t for t in tokens
            if t not in STOP_WORDS and len(t) > 1
        )

    counter = Counter(words)

    return {
        word: count
        for word, count in counter.most_common()
        if count >= min_count
    }