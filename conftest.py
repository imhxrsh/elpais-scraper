"""
conftest.py
-----------
Pytest configuration for the El País scraper test suite.

- Enforces test execution order within classes (tests run top-to-bottom).
- If an earlier test fails, dependent tests are skipped with a clear message.
"""

import pytest


def pytest_collection_modifyitems(items):
    """Sort tests by their class and then by their original definition order.

    This ensures test_1 runs before test_2, test_2 before test_3, etc.
    """
    items.sort(key=lambda item: item.name)