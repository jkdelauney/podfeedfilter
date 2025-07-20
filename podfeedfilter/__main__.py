"""Command-line interface for podfeedfilter.

Serves as the main entry point when running `python -m podfeedfilter`.
Provides the main() function that parses command-line arguments,
loads YAML configuration files, and processes each configured feed.
"""
import argparse
from .config import load_config
from .filterer import process_feed


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter podcast feeds")
    parser.add_argument(
        "-c", "--config", default="feeds.yaml", help="Path to feed "
        "configuration"
    )
    args = parser.parse_args()
    feeds = load_config(args.config)
    for feed in feeds:
        process_feed(feed)


if __name__ == "__main__":
    main()
