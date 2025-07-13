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
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    feeds = []
    for item in data.get('feeds', []):
        feeds.append(
            FeedConfig(
                url=item['url'],
                output=item.get('output', 'filtered.xml'),
                include=item.get('include', []) or [],
                exclude=item.get('exclude', []) or [],
            )
        )
    return feeds
