import subprocess
import sys
import argparse


def main():
    parser = argparse.ArgumentParser(description="El País Opinion Scraper")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--local",
        action="store_true",
        help="Run the scraper locally using headless Chrome",
    )
    group.add_argument(
        "--browserstack",
        action="store_true",
        help="Run the scraper on BrowserStack (5 parallel threads)",
    )
    args = parser.parse_args()

    if args.local:
        print("=" * 70)
        print("Running LOCAL scraper …")
        print("=" * 70)
        cmd = [sys.executable, "-m", "pytest", "-s", "-v", "test_local_scraper.py"]
        subprocess.run(cmd, check=False)

    elif args.browserstack:
        print("=" * 70)
        print("Running on BROWSERSTACK (cross-browser, 5 parallel threads) …")
        print("=" * 70)
        cmd = ["browserstack-sdk", "pytest", "-s", "-v", "test_browserstack_scraper.py"]
        subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()