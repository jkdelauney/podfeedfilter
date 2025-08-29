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
import time
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


def process_feed(cfg: FeedConfig, no_check_modified: bool = False):
    """Process a single feed: download, filter, and generate output feed."""
    output_path = Path(cfg.output)
    existing_entries: list[feedparser.FeedParserDict] = []
    existing_ids: set[str] = set()

    # Determine if we should use conditional fetching
    use_conditional_fetch = cfg.check_modified and not no_check_modified

    # Get existing file modification time for conditional requests
    file_mtime = None
    if output_path.exists():
        file_mtime = output_path.stat().st_mtime if use_conditional_fetch else None
        parsed = feedparser.parse(output_path)
        for entry in parsed.entries:
            existing_entries.append(entry)
            entry_id = str(entry.get('id') or entry.get('link'))
            existing_ids.add(entry_id)

    # Fetch the remote feed (conditionally if enabled)
    last_modified_ts = None
    if use_conditional_fetch:
        # Try conditional fetch
        try:
            content, last_modified_ts = _conditional_fetch(cfg.url, file_mtime)
            if content is None:
                # Feed hasn't been modified, nothing to do
                return
            remote = feedparser.parse(content)
        except (requests.RequestException, ValueError) as e:
            # Fallback to regular fetch if conditional fetch fails
            print(f"Warning: Conditional fetch failed for {cfg.url}: {e}")
            print("Falling back to regular fetch...")
            remote = feedparser.parse(cfg.url)
    else:
        # Use regular fetch
        remote = feedparser.parse(cfg.url)

    remote_feed = cast(feedparser.FeedParserDict, remote.feed)
    new_entries = []
    for entry in remote.entries:
        entry_id = entry.get('id') or entry.get('link')
        if entry_id in existing_ids:
            continue
        if _entry_passes(entry, cfg.include, cfg.exclude):
            new_entries.append(entry)

    # If no existing entries and no new ones, nothing to do
    if not existing_entries and not new_entries:
        return

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
        fg.podcast.itunes_block('yes')

    for entry in existing_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)
    for entry in new_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fg.rss_file(str(output_path))
    
    # Set the output file's modification time to match Last-Modified header
    # ONLY when new episodes were actually added to the output file
    if use_conditional_fetch and new_entries:
        # Only update timestamp when we have new episodes to add
        if last_modified_ts is not None:
            # Use server's Last-Modified timestamp
            os.utime(output_path, (last_modified_ts, last_modified_ts))
        # If no Last-Modified header, preserve existing timestamp by not updating it
        # This ensures the file timestamp reflects when it was last meaningfully updated
