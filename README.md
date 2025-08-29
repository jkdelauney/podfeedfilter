# podfeedfilter

This project collects episodes from multiple podcast feeds, filters them
according to simple keyword rules, and writes a new RSS file for each feed.
It is designed to run from the command line or via cron.

## Configuration

Feed URLs and filter rules are stored in a YAML file. Each feed block
contains the source URL and one or more output definitions. Each output has an
optional list of keywords for inclusion or exclusion. An output may also
override the resulting feed's `title` and `description` fields.
When a feed defines `splits`, those act as additional outputs and can be mixed
with a base output.

Example `feeds.yaml`:

```yaml
feeds:
  - url: "https://example.com/podcast1.rss"
    # main filtered output
    output: "podcast1_filtered.xml"
    exclude:
      - "politics"
    private: true  # Add iTunes block tag (default: true)
    # additional splits using their own rules
    splits:
      - output: "podcast1_tech.xml"
        title: "Podcast 1 Tech"
        description: "Only the tech related episodes"
        include:
          - "python"
          - "code"
        private: false  # This split will be public
      - output: "podcast1_misc.xml"
        exclude:
          - "advertisement"
        # private defaults to true
  - url: "https://example.com/podcast2.rss"
    output: "podcast2_filtered.xml"
    title: "Podcast 2 Filtered"
    description: "Episodes without politics"
    exclude:
      - "politics"
    private: false  # Make this feed public
```

An episode is kept if it does not match any words in the `exclude` list and,
when an `include` list is provided, it contains at least one of those words in
its title or description. When a feed defines multiple `splits`, each split is
treated as a separate output file with its own include and exclude rules.

### Bandwidth Optimization Configuration

By default, all feeds use HTTP conditional requests with `Last-Modified` headers to avoid unnecessary downloads. This can be disabled per-feed if needed:

```yaml
feeds:
  - url: "https://example.com/unreliable-feed.rss"
    output: "unreliable.xml"
    check_modified: false  # Always download this feed
  - url: "https://example.com/normal-feed.rss"
    output: "normal.xml"
    # check_modified: true (default - uses conditional requests)
```

The `check_modified` option can also be set on individual splits to override the parent feed's setting.

### Privacy Control

Each output feed can be marked as private or public using the `private` field:

- `private: true` (default) - Adds `<itunes:block>yes</itunes:block>` to tell podcast directories not to list the feed if discovered
- `private: false` - Creates a public feed without the iTunes block tag
- The `private` setting can be configured independently for main feeds and each split
- If not specified, feeds default to private for security
- **Type Safety**: The private field accepts any value and converts it to boolean (e.g., `0`, `""`, `[]`, `null` become `false`; `1`, `"yes"`, `[1,2,3]` become `true`)

## Requirements

- Python 3.10+ (uses modern type hint syntax)

## Usage

Install requirements and run the filter:

```bash
pip install -r requirements.txt  # once
python -m podfeedfilter -c feeds.yaml
```

Running the command multiple times will append only newly discovered episodes
to the output files. It is safe to invoke from a cron job.

### Bandwidth Optimization

The application automatically uses HTTP conditional requests with `Last-Modified` headers to reduce bandwidth usage. When a feed server supports `Last-Modified` headers:

- The application saves the server's `Last-Modified` timestamp as the output file's modification time
- On subsequent runs, it sends an `If-Modified-Since` header with the previous timestamp
- If the feed hasn't changed (HTTP 304 Not Modified), no download or processing occurs
- This significantly reduces bandwidth usage and processing time for unchanged feeds

**Smart Timestamp Management**: Output file timestamps are only updated when new episodes are actually added to the filtered feed. This ensures that split feeds maintain meaningful "last updated" times that reflect when content was last changed, not just when the source feed was checked.

This optimization is enabled by default and works transparently without configuration changes.

## Command line options

- `-c/--config` – path to the configuration YAML file (default `feeds.yaml`)
- `-n/--no-check-modified` – disable Last-Modified header checking and always fetch feeds (useful for debugging or forcing updates)
- `-p/--private {true,false}` – override private setting for all feeds in the config file

### Privacy Override Examples

```bash
# Make all feeds private regardless of config settings
python -m podfeedfilter -c feeds.yaml --private true

# Make all feeds public regardless of config settings
python -m podfeedfilter -c feeds.yaml --private false

# Use config file settings (default behavior)
python -m podfeedfilter -c feeds.yaml
```

## Development

### Running Tests

The project uses pytest for testing. To run the full test suite:

```bash
pytest -q
```

This will run 127 tests covering various aspects of the feed filtering functionality.

### Test Coverage

The project is configured to track test coverage for the core modules (`config.py` and `filterer.py`) with a target of >90% line coverage. To run tests with coverage reporting:

```bash
pytest -q --cov=podfeedfilter.config --cov=podfeedfilter.filterer --cov-report=term-missing --cov-fail-under=90
```

The coverage configuration is also included in `pytest.ini`, so running `pytest` will automatically include coverage reporting. Coverage reports are generated in both terminal and HTML formats (in `htmlcov/` directory).

Current coverage: **100%** for both `config.py` and `filterer.py`.

### Installing Development Dependencies

To install testing dependencies:

```bash
pip install -r requirements-dev.txt
```

Alternatively, install testing dependencies manually:

```bash
pip install pytest pytest-cov
```

## AI Assistant Documentation

**For AI coding assistants (Claude, Cursor, Copilot, Cline, etc.)**: This project includes comprehensive documentation for AI assistants in `AGENT.md`. This file contains detailed architecture information, development guidelines, testing procedures, and codebase structure that AI assistants should reference for context-aware code assistance.

## Project layout

- `podfeedfilter/` – package containing the code.
- `feeds.yaml` – sample configuration file.
- `requirements.txt` – core Python dependencies.
- `requirements-dev.txt` – development and testing dependencies.
- `pytest.ini` – pytest configuration with coverage settings.
- `tests/` – test suite directory.
- `AGENT.md` – **AI assistant documentation** (architecture, guidelines, testing)
- `EDGE_CASE_TESTS.md` – edge case testing documentation.
