"""Configuration loading and data structures for podcast feeds.

Defines the FeedConfig dataclass for individual feed configurations
and provides load_config() function to parse YAML files. Supports
feed splitting where single source URLs can generate multiple filtered
output files with different include/exclude criteria.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class FeedConfig:
    """Configuration for a single podcast feed filtering task."""
    url: str
    output: str
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    title: str | None = None
    description: str | None = None
    check_modified: bool = True
    private: bool = True


def load_config(path: str) -> List[FeedConfig]:
    """Parse the YAML config into a list of FeedConfig objects."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    feeds: List[FeedConfig] = []
    for item in data.get("feeds", []):
        url = item["url"]

        # create a base output if one is defined
        if (
            "output" in item
            or item.get("include")
            or item.get("exclude")
            or item.get("title")
            or item.get("description")
        ):
            feeds.append(
                FeedConfig(
                    url=url,
                    output=item.get("output", "filtered.xml"),
                    include=item.get("include", []) or [],
                    exclude=item.get("exclude", []) or [],
                    title=item.get("title"),
                    description=item.get("description"),
                    check_modified=item.get("check_modified", True),
                    private=bool(item.get("private", True)),
                )
            )

        # Support splitting a single source feed into multiple outputs.
        splits = item.get("splits") or item.get("split") or []
        for split in splits:
            feeds.append(
                FeedConfig(
                    url=url,
                    output=split.get("output", "filtered.xml"),
                    include=split.get("include", []) or [],
                    exclude=split.get("exclude", []) or [],
                    title=split.get("title"),
                    description=split.get("description"),
                    check_modified=split.get("check_modified", item.get("check_modified", True)),
                    private=bool(split.get("private", True)),
                )
            )

    return feeds
