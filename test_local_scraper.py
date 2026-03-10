import os
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from testcases import BaseTestElPaisScraper, IMAGES_BASE


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def driver():
    """Create a local Chrome WebDriver instance."""
    opts = Options()
    opts.add_argument("--headless=new")  # keep disabled to see browser
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=es")

    drv = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=opts
    )

    yield drv
    drv.quit()


@pytest.fixture(scope="module")
def shared_data():
    """Module-scoped dict to share state across ordered tests.

    Sets image_dir to images/local_<timestamp>/ so each run is preserved.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_dir = os.path.join(IMAGES_BASE, f"local_{timestamp}")
    os.makedirs(image_dir, exist_ok=True)
    return {"image_dir": image_dir}


# ── tests ────────────────────────────────────────────────────────────────────


class TestElPaisLocal(BaseTestElPaisScraper):
    """Local test suite — inherits all 5 test steps from BaseTestElPaisScraper."""
    pass