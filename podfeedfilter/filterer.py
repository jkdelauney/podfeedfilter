"""Core podcast feed processing and filtering functionality.

Provides process_feed() function to download RSS feeds, filter episodes
based on include/exclude keywords, and generate filtered output feeds.
Includes helper functions _text_matches(), _entry_passes(), and
_copy_entry() for content matching and feed generation.
"""
from __future__ import annotations
from pathlib import Path
from typing import cast
import email.utils
import os
import feedparser
import requests
from feedgen.feed import FeedGenerator
from .config import FeedConfig


def _text_matches(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    for kw in keywords:
        if kw.lower() in lower:
            return True
    return False


def _entry_passes(entry: feedparser.FeedParserDict, include: list[str],
                  exclude: list[str]) -> bool:
    content = (
        f"{entry.get('title', '')} "
        f"{entry.get('description', '')} "
        f"{entry.get('summary', '')}"
    )
    if exclude and _text_matches(content, exclude):
        return False
    if include and not _text_matches(content, include):
        return False
    return True


def _conditional_fetch(url: str, since: float | None) -> tuple[bytes | None, float | None]:
    """Fetch URL with conditional request using If-Modified-Since header.

    Args:
        url: The URL to fetch
        since: Timestamp (Unix time) to use for If-Modified-Since header, or None

    Returns:
        Tuple of (content_bytes, last_modified_timestamp) if content was modified,
        or (None, None) if content was not modified (304 response)
    """
    headers = {}
    if since is not None:
        headers["If-Modified-Since"] = email.utils.formatdate(since, usegmt=True)

    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code == 304:
        return None, None

    resp.raise_for_status()

    lm_str = resp.headers.get("Last-Modified")
    lm_ts = None
    if lm_str:
        try:
            lm_ts = email.utils.parsedate_to_datetime(lm_str).timestamp()
        except (ValueError, TypeError):
            # If we can't parse the Last-Modified header, ignore it
            pass

    return resp.content, lm_ts


def _copy_entry(fe, entry: feedparser.FeedParserDict) -> None:
    """Copy relevant fields from a parsed entry into a feedgen entry."""
    fe.id(entry.get("id", entry.get("link")))
    if "title" in entry:
        fe.title(entry["title"])
    if "link" in entry:
        fe.link(href=entry["link"])
    description = entry.get("summary") or entry.get("description")
    if description:
        fe.description(description)
    if "published" in entry:
        fe.published(entry["published"])
    if "author" in entry:
        fe.author({"name": entry["author"]})
    if "content" in entry:
        for content in entry["content"]:
            fe.content(content.get("value", ""), type=content.get("type"))
    if "enclosures" in entry:
        for enc in entry["enclosures"]:
            fe.enclosure(enc.get("href"), enc.get("length"), enc.get("type"))


def _load_existing_entries(output_path: Path) -> tuple[list[feedparser.FeedParserDict], set[str]]:
    """Load existing entries and IDs from output file."""
    existing_entries: list[feedparser.FeedParserDict] = []
    existing_ids: set[str] = set()

    if output_path.exists():
        parsed = feedparser.parse(output_path)
        for entry in parsed.entries:
            existing_entries.append(entry)
            entry_id = entry.get('id') or entry.get('link')
            if entry_id is not None:
                existing_ids.add(str(entry_id))

    return existing_entries, existing_ids


def _fetch_remote_feed(cfg: FeedConfig, use_conditional_fetch: bool,
                      file_mtime: float | None
                      ) -> tuple[feedparser.util.FeedParserDict | None, float | None]:
    """Fetch remote feed with conditional fetching if enabled."""
    last_modified_ts = None

    if use_conditional_fetch:
        try:
            content, last_modified_ts = _conditional_fetch(cfg.url, file_mtime)
            if content is None:
                # Feed hasn't been modified, return None to signal early exit
                return None, None
            remote = feedparser.parse(content)
        except (requests.RequestException, ValueError) as e:
            print(f"Warning: Conditional fetch failed for {cfg.url}: {e}")
            print("Falling back to regular fetch...")
            remote = feedparser.parse(cfg.url)
    else:
        remote = feedparser.parse(cfg.url)

    return remote, last_modified_ts


def _filter_new_entries(remote_entries: list, existing_ids: set[str],
                       cfg: FeedConfig) -> list[feedparser.FeedParserDict]:
    """Filter remote entries for new items that pass include/exclude criteria."""
    new_entries = []
    for entry in remote_entries:
        entry_id = entry.get('id') or entry.get('link')
        # Skip entries without valid IDs or entries that already exist
        if entry_id is None or str(entry_id) in existing_ids:
            continue
        if _entry_passes(entry, cfg.include, cfg.exclude):
            new_entries.append(entry)
    return new_entries


def _setup_feed_generator(cfg: FeedConfig, remote_feed: feedparser.FeedParserDict) -> FeedGenerator:
    """Set up the FeedGenerator with metadata and settings."""
    fg = FeedGenerator()
    fg.load_extension('podcast')

    feed_title = cfg.title if cfg.title is not None else remote_feed.get(
        'title', 'Filtered Feed')
    fg.title(feed_title)

    if remote_feed.get('link'):
        fg.link(href=remote_feed['link'])

    feed_description = (
        cfg.description
        if cfg.description is not None
        else remote_feed.get('description', '')
    )
    fg.description(feed_description)

    # Add iTunes block tag if private is True (default)
    if cfg.private:
        fg.podcast.itunes_block('yes')  # pylint: disable=no-member

    return fg


def _add_entries_to_feed(fg: FeedGenerator, existing_entries: list[feedparser.FeedParserDict],
                        new_entries: list[feedparser.FeedParserDict]) -> None:
    """Add all entries (existing + new) to the feed generator."""
    for entry in existing_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)
    for entry in new_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)


def _update_file_timestamp(output_path: Path, last_modified_ts: float | None) -> None:
    """Update file timestamp if Last-Modified header is available."""
    if last_modified_ts is not None:
        os.utime(output_path, (last_modified_ts, last_modified_ts))


def process_feed(cfg: FeedConfig, no_check_modified: bool = False):
    """Process a single feed: download, filter, and generate output feed."""
    output_path = Path(cfg.output)

    # Load existing entries and determine conditional fetch settings
    existing_entries, existing_ids = _load_existing_entries(output_path)
    use_conditional_fetch = cfg.check_modified and not no_check_modified
    file_mtime = (
        output_path.stat().st_mtime
        if (output_path.exists() and use_conditional_fetch)
        else None
    )

    # Fetch remote feed
    remote, last_modified_ts = _fetch_remote_feed(cfg, use_conditional_fetch, file_mtime)
    if remote is None:
        # Feed hasn't been modified, nothing to do
        return

    remote_feed = cast(feedparser.FeedParserDict, remote.feed)

    # Filter new entries
    new_entries = _filter_new_entries(remote.entries, existing_ids, cfg)

    # Exit early if no content to process
    if not existing_entries and not new_entries:
        return

    # Generate output feed
    fg = _setup_feed_generator(cfg, remote_feed)
    _add_entries_to_feed(fg, existing_entries, new_entries)

    # Write output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fg.rss_file(str(output_path))

    # Update file timestamp if needed
    if use_conditional_fetch and new_entries:
        _update_file_timestamp(output_path, last_modified_ts)
