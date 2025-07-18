from __future__ import annotations
from pathlib import Path
import feedparser
from feedgen.feed import FeedGenerator
from .config import FeedConfig
from typing import cast


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


def process_feed(cfg: FeedConfig):
    output_path = Path(cfg.output)
    existing_entries: list[feedparser.FeedParserDict] = []
    existing_ids: set[str] = set()

    if output_path.exists():
        parsed = feedparser.parse(output_path)
        for entry in parsed.entries:
            existing_entries.append(entry)
            entry_id = str(entry.get('id') or entry.get('link'))
            existing_ids.add(entry_id)

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

    for entry in existing_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)
    for entry in new_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fg.rss_file(str(output_path))
