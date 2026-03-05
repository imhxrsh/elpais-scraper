"""
utils.py — All helper functions for the El País scraper.
"""

import os
import re
import time
import requests
from collections import Counter
from deep_translator import GoogleTranslator
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ── Cookie / popup handling ──────────────────────────────────────────────────

def accept_cookies(driver):
    """Dismiss Didomi + El País subscription popups if present."""
    for locator in [
        (By.ID, "didomi-notice-agree-button"),
        (By.XPATH, "//button[contains(text(),'ACEPTAR') or contains(text(),'Aceptar')]"),
    ]:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(locator)).click()
            time.sleep(1)
        except Exception:
            pass


# ── Image extraction ─────────────────────────────────────────────────────────

def _get_image_url(el):
    """Try to extract an image URL from an element via img src/srcset or picture>source."""
    for tag in ["img", "picture source"]:
        try:
            node = el.find_element(By.CSS_SELECTOR, tag)
            # Try direct src
            url = node.get_attribute("src") or node.get_attribute("data-src")
            if url and "data:image" not in url and "blank.png" not in url:
                return url
            # Fallback to srcset
            srcset = node.get_attribute("srcset")
            if srcset:
                return srcset.split(",")[0].strip().split(" ")[0]
        except Exception:
            continue
    return None


def download_image(url, dest_folder, filename):
    """Download image from URL to dest_folder/filename. Returns path or None."""
    if not url:
        return None
    os.makedirs(dest_folder, exist_ok=True)
    filepath = os.path.join(dest_folder, filename)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(f"  [image] Saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"  [image] Failed: {e}")
        return None


# ── Article scraping ─────────────────────────────────────────────────────────

def fetch_articles(driver, limit=5):
    """Scroll page, then return up to `limit` articles as list of dicts."""
    # Scroll to trigger lazy-loading (needed on mobile)
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

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
        except Exception:
            continue
        articles.append({
            "title": title,
            "url": url,
            "image_url": _get_image_url(el),
        })
    return articles


def get_article_content(driver, url):
    """Open article in new tab, return (body_text, cover_image_url)."""
    driver.execute_script("window.open(arguments[0]);", url)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)
    accept_cookies(driver)

    # Scrape body paragraphs
    paragraphs = driver.find_elements(By.CSS_SELECTOR, "article .a_c p")
    if not paragraphs:
        paragraphs = driver.find_elements(By.CSS_SELECTOR, "article p")
    content = "\n".join(p.text.strip() for p in paragraphs if p.text.strip())

    # Try to get cover image from detail page
    image_url = None
    for sel in ["article img", "figure img", "picture source"]:
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


# ── Translation ──────────────────────────────────────────────────────────────

def translate_text(text, source="es", target="en"):
    """Translate text using Google Translate."""
    try:
        return GoogleTranslator(source=source, target=target).translate(text) or text
    except Exception as e:
        print(f"  [translate] Error: {e}")
        return text


# ── Word analysis ────────────────────────────────────────────────────────────

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "that", "this", "it", "its", "not",
    "no", "as", "if", "than", "he", "she", "they", "we", "you", "my",
    "your", "his", "her", "our", "their", "who", "what", "which", "so",
    "about", "into", "over", "after", "before", "between", "under", "up",
}


def count_repeated_words(headers, min_count=3):
    """Return dict of words appearing >= min_count times across all headers."""
    words = []
    for h in headers:
        tokens = re.findall(r"[a-zA-Z]+", h.lower())
        words.extend(t for t in tokens if t not in STOP_WORDS and len(t) > 1)
    counter = Counter(words)
    return {w: c for w, c in counter.most_common() if c >= min_count}