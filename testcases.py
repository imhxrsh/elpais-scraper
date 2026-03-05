"""
testcases.py — Shared test cases for El País Opinion scraper.
Subclass BaseTestElPaisScraper and provide `driver` + `shared_data` fixtures.
"""

import os
from utils import (
    accept_cookies, fetch_articles, get_article_content,
    download_image, translate_text, count_repeated_words,
)

IMAGES_BASE = os.path.join(os.path.dirname(__file__), "images")


class BaseTestElPaisScraper:

    def test_1_website_is_in_spanish(self, driver, shared_data):
        """Verify El País loads in Spanish."""
        driver.get("https://elpais.com/")
        accept_cookies(driver)
        lang = driver.find_element("tag name", "html").get_attribute("lang")
        print(f"\n  Page lang: {lang}")
        assert lang and lang.startswith("es"), f"Expected 'es', got '{lang}'"

    def test_2_navigate_to_opinion_and_fetch_articles(self, driver, shared_data):
        """Navigate to Opinion section and fetch up to 5 articles."""
        driver.get("https://elpais.com/opinion/")
        accept_cookies(driver)
        import time; time.sleep(3)

        articles = fetch_articles(driver, limit=5)
        shared_data["articles"] = articles

        for i, a in enumerate(articles, 1):
            print(f"  {i}. {a['title']}")

        assert len(articles) >= 1, "No articles found"

    def test_3_scrape_content_and_download_images(self, driver, shared_data):
        """Scrape article content (Spanish) and download cover images."""
        articles = shared_data.get("articles", [])
        assert articles, "No articles — test_2 may have failed"

        image_dir = shared_data.get("image_dir", IMAGES_BASE)
        titles_es = []

        for idx, art in enumerate(articles, 1):
            titles_es.append(art["title"])
            print(f"\n  Article {idx}: {art['title']}")

            # Try listing image, then fallback to detail page image
            content, detail_img = get_article_content(driver, art["url"])
            img_url = art["image_url"] or detail_img
            if img_url:
                download_image(img_url, image_dir, f"article_{idx}.jpg")
            else:
                print("     [image] No cover image available.")

            print(f"     Content: {content[:300]}{'…' if len(content) > 300 else ''}")

        shared_data["titles_es"] = titles_es
        assert len(titles_es) == len(articles)

    def test_4_translate_titles_to_english(self, driver, shared_data):
        """Translate all titles from Spanish to English."""
        titles_es = shared_data.get("titles_es", [])
        assert titles_es, "No titles — test_3 may have failed"

        titles_en = []
        for es in titles_es:
            en = translate_text(es)
            titles_en.append(en)
            print(f"  ES: {es}\n  EN: {en}\n")

        shared_data["titles_en"] = titles_en
        assert all(t for t in titles_en), "One or more translations failed"

    def test_5_analyze_repeated_words(self, driver, shared_data):
        """Find words repeated more than twice across translated titles."""
        titles_en = shared_data.get("titles_en", [])
        assert titles_en, "No translations — test_4 may have failed"

        repeated = count_repeated_words(titles_en)
        if repeated:
            for word, cnt in repeated.items():
                print(f"  '{word}' → {cnt}")
        else:
            print("  No words repeated more than twice.")
        assert isinstance(repeated, dict)