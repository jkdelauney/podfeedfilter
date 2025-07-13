# podfeedfilter

This project collects episodes from multiple podcast feeds, filters them
according to simple keyword rules, and writes a new RSS file for each feed.
It is designed to run from the command line or via cron.

## Configuration

Feed URLs and filter rules are stored in a YAML file. Each feed block
contains the source URL, output file location and optional lists of keywords
for inclusion or exclusion.

Example `feeds.yaml`:

```yaml
feeds:
  - url: "https://example.com/podcast1.rss"
    output: "podcast1_filtered.xml"
    include:
      - "python"
      - "code"
    exclude:
      - "politics"
  - url: "https://example.com/podcast2.rss"
    output: "podcast2_filtered.xml"
    include: []
    exclude:
      - "advertisement"
```

An episode is kept if it does not match any words in the `exclude` list and,
when an `include` list is provided, it contains at least one of those words in
its title or description.

## Usage

Install requirements and run the filter:

```bash
pip install -r requirements.txt  # once
python -m podfeedfilter -c feeds.yaml
```

Running the command multiple times will append only newly discovered episodes
to the output files. It is safe to invoke from a cron job.

## Command line options

- `-c/--config` – path to the configuration YAML file (default `feeds.yaml`).

## Project layout

- `podfeedfilter/` – package containing the code.
- `feeds.yaml` – sample configuration file.
- `requirements.txt` – Python dependencies.

