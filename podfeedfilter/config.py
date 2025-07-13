from dataclasses import dataclass, field
from typing import List
import yaml

@dataclass
class FeedConfig:
    url: str
    output: str
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)

def load_config(path: str) -> List[FeedConfig]:
    """Parse the YAML config into a list of FeedConfig objects."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    feeds: List[FeedConfig] = []
    for item in data.get("feeds", []):
        url = item["url"]
        # Support splitting a single source feed into multiple outputs.
        splits = item.get("splits") or item.get("split")
        if splits:
            for split in splits:
                feeds.append(
                    FeedConfig(
                        url=url,
                        output=split.get("output", "filtered.xml"),
                        include=split.get("include", []) or [],
                        exclude=split.get("exclude", []) or [],
                    )
                )
            continue

        feeds.append(
            FeedConfig(
                url=url,
                output=item.get("output", "filtered.xml"),
                include=item.get("include", []) or [],
                exclude=item.get("exclude", []) or [],
            )
        )

    return feeds
