from __future__ import annotations
from pathlib import Path
import feedparser
from feedgen.feed import FeedGenerator
from .config import FeedConfig


def _text_matches(text: str, keywords: list[str]) -> bool:
    lower = text.lower()
    for kw in keywords:
        if kw.lower() in lower:
            return True
    return False


def _entry_passes(entry: feedparser.FeedParserDict, include: list[str], exclude: list[str]) -> bool:
    content = f"{entry.get('title', '')} {entry.get('description', '')} {entry.get('summary', '')}"
    if exclude and _text_matches(content, exclude):
        return False
    if include and not _text_matches(content, include):
        return False
    return True


def _copy_entry(fe, entry: feedparser.FeedParserDict):
    fe.id(entry.get('id', entry.get('link')))
    if 'title' in entry:
        fe.title(entry['title'])
    if 'link' in entry:
        fe.link(href=entry['link'])
    if 'summary' in entry:
        fe.description(entry['summary'])
    if 'published' in entry:
        fe.published(entry['published'])
    if 'author' in entry:
        fe.author({'name': entry['author']})
    if 'content' in entry:
        for content in entry['content']:
            fe.content(content.get('value', ''), type=content.get('type'))


def process_feed(cfg: FeedConfig):
    output_path = Path(cfg.output)
    existing_entries: list[feedparser.FeedParserDict] = []
    existing_ids: set[str] = set()

    if output_path.exists():
        parsed = feedparser.parse(output_path)
        for e in parsed.entries:
            existing_entries.append(e)
            existing_ids.add(e.get('id') or e.get('link'))

    remote = feedparser.parse(cfg.url)
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

    feed_title = cfg.title if cfg.title is not None else remote.feed.get('title', 'Filtered Feed')
    fg.title(feed_title)
    if remote.feed.get('link'):
        fg.link(href=remote.feed['link'])
    feed_description = cfg.description if cfg.description is not None else remote.feed.get('description', '')
    fg.description(feed_description)

    for entry in existing_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)
    for entry in new_entries:
        fe = fg.add_entry()
        _copy_entry(fe, entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fg.rss_file(str(output_path))
