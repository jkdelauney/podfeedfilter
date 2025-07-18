"""
Shared pytest fixtures and test helpers for podfeedfilter tests.
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

import pytest
import yaml
import feedparser


# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def test_data_dir():
    """Provide the path to the test data directory."""
    return TEST_DATA_DIR


@pytest.fixture
def sample_rss_feed():
    """Load a sample RSS feed from test data."""
    rss_file = TEST_DATA_DIR / "sample_feed.xml"
    return rss_file.read_text() if rss_file.exists() else None


@pytest.fixture
def sample_yaml_config():
    """Load a sample YAML configuration from test data."""
    yaml_file = TEST_DATA_DIR / "sample_config.yaml"
    if yaml_file.exists():
        with open(yaml_file, 'r') as f:
            return yaml.safe_load(f)
    return None


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml',
                                     delete=False) as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_feeds_config():
    """Provide a mock feeds configuration for testing."""
    return {
        'feeds': [
            {
                'name': 'Test Podcast',
                'url': 'https://example.com/feed.xml',
                'filters': {
                    'include_keywords': ['tech', 'python'],
                    'exclude_keywords': ['boring']
                }
            },
            {
                'name': 'Another Podcast',
                'url': 'https://another.com/feed.xml',
                'filters': {
                    'max_age_days': 30,
                    'min_duration_minutes': 10
                }
            }
        ]
    }


@pytest.fixture
def mock_rss_item():
    """Provide a mock RSS item for testing."""
    return {
        'title': 'Test Episode',
        'description': 'This is a test episode about Python programming',
        'link': 'https://example.com/episode/123',
        'pubDate': 'Mon, 01 Jan 2024 12:00:00 GMT',
        'guid': 'episode-123',
        'enclosure': {
            'url': 'https://example.com/audio/episode-123.mp3',
            'type': 'audio/mpeg',
            'length': '12345678'
        }
    }


def create_test_rss_feed(title: str, items: list) -> str:
    """Helper function to create a test RSS feed XML string."""
    rss_template = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{title}</title>
        <description>Test podcast feed</description>
        <link>https://example.com</link>
        <language>en</language>
        {items}
    </channel>
</rss>"""

    items_xml = ""
    for item in items:
        item_xml = f"""
        <item>
            <title>{item.get('title', 'Test Item')}</title>
            <description>{item.get('description',
                                   'Test description')}</description>
            <link>{item.get('link', 'https://example.com/item')}</link>
            <pubDate>{item.get('pubDate', 'Mon, 01 Jan 2024 12:00:00 GMT'
                               )}</pubDate>
            <guid>{item.get('guid', 'test-guid')}</guid>
        </item>"""
        items_xml += item_xml

    return rss_template.format(title=title, items=items_xml)


def create_test_yaml_config(config_dict: Dict[str, Any]) -> str:
    """Helper function to create a test YAML configuration string."""
    return yaml.dump(config_dict, default_flow_style=False)


# Config fixture helpers
CONFIG_DIR = TEST_DATA_DIR / "configs"


@pytest.fixture
def config_files():
    """Provide paths to all available config files."""
    return {
        "basic_include_exclude": CONFIG_DIR / "basic_include_exclude.yaml",
        "splits_config": CONFIG_DIR / "splits_config.yaml",
        "missing_keys": CONFIG_DIR / "missing_keys.yaml",
        "bad_syntax": CONFIG_DIR / "bad_syntax.yaml",
        "empty_config": CONFIG_DIR / "empty_config.yaml",
        "complex_config": CONFIG_DIR / "complex_config.yaml",
    }


@pytest.fixture
def temp_config_from_fixture(tmp_path):
    """Helper to copy a config fixture to a temporary path.

    Returns a function that takes a config name and returns the temp path.
    """
    def _copy_config(config_name: str) -> Path:
        """Copy a config fixture to tmp_path and return the path.

        Args:
            config_name: Name of the config (e.g., 'basic_include_exclude')

        Returns:
            Path to the copied config file in tmp_path
        """
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"Config fixture '{config_name}' not found at "
                f"{config_path}"
            )

        temp_config_path = tmp_path / f"{config_name}.yaml"
        shutil.copy2(config_path, temp_config_path)
        return temp_config_path

    return _copy_config


@pytest.fixture
def basic_include_exclude_config(tmp_path):
    """Copy basic include/exclude config to tmp_path and return the path."""
    config_path = CONFIG_DIR / "basic_include_exclude.yaml"
    temp_config_path = tmp_path / "basic_include_exclude.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def splits_config(tmp_path):
    """Copy splits config to tmp_path and return the path."""
    config_path = CONFIG_DIR / "splits_config.yaml"
    temp_config_path = tmp_path / "splits_config.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def missing_keys_config(tmp_path):
    """Copy config with missing keys to tmp_path and return the path."""
    config_path = CONFIG_DIR / "missing_keys.yaml"
    temp_config_path = tmp_path / "missing_keys.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def bad_syntax_config(tmp_path):
    """Copy config with bad syntax to tmp_path and return the path."""
    config_path = CONFIG_DIR / "bad_syntax.yaml"
    temp_config_path = tmp_path / "bad_syntax.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def empty_config(tmp_path):
    """Copy empty config to tmp_path and return the path."""
    config_path = CONFIG_DIR / "empty_config.yaml"
    temp_config_path = tmp_path / "empty_config.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def complex_config(tmp_path):
    """Copy complex config to tmp_path and return the path."""
    config_path = CONFIG_DIR / "complex_config.yaml"
    temp_config_path = tmp_path / "complex_config.yaml"
    shutil.copy2(config_path, temp_config_path)
    return temp_config_path


@pytest.fixture
def all_temp_configs(tmp_path):
    """Copy all config fixtures to tmp_path and return a dict of paths."""
    configs = {}
    config_names = [
        "basic_include_exclude",
        "splits_config",
        "missing_keys",
        "bad_syntax",
        "empty_config",
        "complex_config"
    ]

    for config_name in config_names:
        config_path = CONFIG_DIR / f"{config_name}.yaml"
        temp_config_path = tmp_path / f"{config_name}.yaml"
        shutil.copy2(config_path, temp_config_path)
        configs[config_name] = temp_config_path

    return configs


# Feedparser monkeypatch fixture
FEED_FILES_DIR = TEST_DATA_DIR / "feeds"


@pytest.fixture
def mock_feedparser_parse(monkeypatch):
    """Monkeypatch feedparser.parse to return pre-parsed objects from
    static XML files.

    This fixture intercepts feedparser.parse(url) calls and returns
    pre-parsed feed objects from static XML files when test URLs are used.
    This prevents network I/O while still exercising the real parsing logic.

    Test URL mapping:
    - http://test/feed1 -> normal_feed.xml
    - http://test/feed2 -> minimal_feed.xml
    - http://test/feed3 -> empty_feed.xml
    - http://test/feed4 -> malformed_feed.xml
    - http://test/feed5 -> future_episodes_feed.xml
    - http://test/complex -> complex_feed.xml

    For any other URL, the original feedparser.parse is called.
    """
    original_parse = feedparser.parse

    def mock_parse(url_or_file, etag=None, modified=None, agent=None,
                   referrer=None, handlers=None, request_headers=None,
                   response_headers=None, resolve_relative_uris=None,
                   sanitize_html=None):
        """Mock feedparser.parse that returns pre-parsed objects for test
            URLs."""
        # Define the mapping of test URLs to XML files
        test_url_mapping = {
            'http://test/feed1': 'normal_feed.xml',
            'http://test/feed2': 'minimal_feed.xml',
            'http://test/feed3': 'empty_feed.xml',
            'http://test/feed4': 'malformed_feed.xml',
            'http://test/feed5': 'future_episodes_feed.xml',
            'http://test/complex': 'complex_feed.xml',
        }

        # Check if this is a test URL
        if isinstance(url_or_file, str) and url_or_file in test_url_mapping:
            xml_filename = test_url_mapping[url_or_file]
            xml_file_path = FEED_FILES_DIR / xml_filename

            if xml_file_path.exists():
                # Parse the static XML file instead of making a network request
                return original_parse(
                    str(xml_file_path),
                    etag=etag,
                    modified=modified,
                    agent=agent,
                    referrer=referrer,
                    handlers=handlers,
                    request_headers=request_headers,
                    response_headers=response_headers,
                    resolve_relative_uris=resolve_relative_uris,
                    sanitize_html=sanitize_html)
            else:
                # If the XML file doesn't exist, return an empty feed
                empty_feed_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed Not Found</title>
    <link>http://test/notfound</link>
    <description>Test feed XML file not found</description>
  </channel>
</rss>'''
                return feedparser.parse(empty_feed_xml)

        # For non-test URLs, use the original feedparser.parse
        return original_parse(url_or_file,
                              etag=etag,
                              modified=modified,
                              agent=agent,
                              referrer=referrer,
                              handlers=handlers,
                              request_headers=request_headers,
                              response_headers=response_headers,
                              resolve_relative_uris=resolve_relative_uris,
                              sanitize_html=sanitize_html)

    monkeypatch.setattr(feedparser, 'parse', mock_parse)
    return mock_parse


@pytest.fixture
def test_feed_urls():
    """Provide a mapping of test feed URLs to their corresponding XML files.

    This fixture provides a convenient way to access test URLs and their
    corresponding XML files for testing purposes.
    """
    return {
        'normal_feed': 'http://test/feed1',
        'minimal_feed': 'http://test/feed2',
        'empty_feed': 'http://test/feed3',
        'malformed_feed': 'http://test/feed4',
        'future_episodes_feed': 'http://test/feed5',
        'complex_feed': 'http://test/complex',
    }


# Test markers for convenience
pytestmark = pytest.mark.unit
