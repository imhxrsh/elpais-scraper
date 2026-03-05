"""
test_browserstack_scraper.py
-----------------------------
BrowserStack cross-browser test for El País Opinion scraper.
The SDK intercepts webdriver.Chrome() and routes to BrowserStack's grid.
Test logic is inherited from testcases.py.
Images are saved under images/bstack_<uuid>/ per parallel session.

Run:
    browserstack-sdk pytest -s -v test_browserstack_scraper.py
"""

import os
import uuid
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from testcases import BaseTestElPaisScraper, IMAGES_BASE


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def driver():
    """
    The BrowserStack SDK intercepts standard webdriver.Chrome()
    calls and re-routes them to BrowserStack's Selenium Grid
    automatically. No --headless needed for remote browsers.
    """
    opts = Options()
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=es")
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(15)
    yield drv
    drv.quit()


@pytest.fixture(scope="module")
def shared_data(driver):
    """Module-scoped dict to share state across ordered tests.

    Sets image_dir to images/bstack_<session_id>/ so each parallel
    BrowserStack session saves images to its own folder.
    """
    # Use the BrowserStack session ID for a meaningful folder name
    session_id = driver.session_id or str(uuid.uuid4())[:8]
    image_dir = os.path.join(IMAGES_BASE, f"bstack_{session_id}")
    os.makedirs(image_dir, exist_ok=True)
    return {"image_dir": image_dir}


# ── tests ────────────────────────────────────────────────────────────────────


class TestElPaisBrowserStack(BaseTestElPaisScraper):
    """BrowserStack test suite — inherits all 5 test steps from BaseTestElPaisScraper."""
    pass