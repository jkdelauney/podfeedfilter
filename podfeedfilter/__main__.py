"""Command-line interface for podfeedfilter.

Serves as the main entry point when running `python -m podfeedfilter`.
Provides the main() function that parses command-line arguments,
loads YAML configuration files, and processes each configured feed.
"""
import argparse
from .config import load_config
from .filterer import process_feed


def main() -> None:
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(description="Filter podcast feeds")
    parser.add_argument(
        "-c", "--config", default="feeds.yaml", help="Path to feed "
        "configuration"
    )
    parser.add_argument(
        "-n", "--no-check-modified", action="store_true",
        help="Disable Last-Modified header checking and always fetch feeds"
    )
    args = parser.parse_args()
    feeds = load_config(args.config)
    for feed in feeds:
        process_feed(feed, no_check_modified=args.no_check_modified)


if __name__ == "__main__":
    main()
