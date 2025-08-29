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
    parser.add_argument(
        "-p", "--private", choices=["true", "false"],
        help="Override private setting for all feeds (true/false)"
    )
    args = parser.parse_args()
    feeds = load_config(args.config)

    # Apply CLI private override if specified
    private_override = None
    if args.private is not None:
        private_override = args.private.lower() == "true"

    for feed in feeds:
        if private_override is not None:
            feed.private = private_override
        process_feed(feed, no_check_modified=args.no_check_modified)


if __name__ == "__main__":
    main()
