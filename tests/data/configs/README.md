# Config Fixtures

This directory contains YAML configuration files for testing various scenarios in the podfeedfilter project.

## Available Config Files

### 1. `basic_include_exclude.yaml`
Basic configuration with simple include/exclude patterns.
- **Use case**: Testing basic filtering functionality
- **Contents**: Simple include patterns for audio files, exclude patterns for text files

### 2. `splits_config.yaml`
Configuration using splits to create multiple outputs.
- **Use case**: Testing split functionality where content is divided into multiple categories
- **Contents**: Three splits (episodes, interviews, music) with different filter criteria

### 3. `missing_keys.yaml`
Configuration with missing required keys.
- **Use case**: Testing error handling for incomplete configurations
- **Contents**: Has include_patterns but missing exclude_patterns

### 4. `bad_syntax.yaml`
Configuration with invalid YAML syntax.
- **Use case**: Testing error handling for malformed YAML files
- **Contents**: Contains various YAML syntax errors (unclosed brackets, bad indentation)

### 5. `empty_config.yaml`
Empty configuration file.
- **Use case**: Testing edge case handling for empty configs
- **Contents**: Only contains a comment

### 6. `complex_config.yaml`
Complex configuration with multiple features.
- **Use case**: Testing comprehensive configuration parsing
- **Contents**: Global settings, splits with advanced filtering, output settings

## Using Config Fixtures in Tests

The `conftest.py` file provides several fixtures for working with these config files:

### Individual Config Fixtures

```python
def test_basic_config(basic_include_exclude_config):
    """Test using a specific config fixture."""
    # The fixture copies the config to tmp_path and returns the path
    assert basic_include_exclude_config.exists()
    
    with open(basic_include_exclude_config, 'r') as f:
        config = yaml.safe_load(f)
    # ... test logic
```

### Generic Config Fixture

```python
def test_any_config(temp_config_from_fixture):
    """Test using the generic config fixture helper."""
    # Copy any config by name
    config_path = temp_config_from_fixture('splits_config')
    assert config_path.exists()
    # ... test logic
```

### All Configs at Once

```python
def test_all_configs(all_temp_configs):
    """Test using all configs at once."""
    # Returns a dict with all config names -> paths
    assert 'basic_include_exclude' in all_temp_configs
    assert 'splits_config' in all_temp_configs
    # ... test logic
```

### Original Config Paths

```python
def test_original_paths(config_files):
    """Test getting original config file paths."""
    # Returns paths to original files (don't modify these!)
    original_path = config_files['basic_include_exclude']
    # ... read-only operations
```

## Test Scenarios

### Valid Config Tests
- Use `basic_include_exclude_config`, `splits_config`, `complex_config`
- Test successful parsing and configuration loading
- Verify expected keys and values are present

### Error Handling Tests
- Use `missing_keys_config` for testing missing required keys
- Use `bad_syntax_config` for testing YAML parsing errors
- Use `empty_config` for testing empty file handling

### Edge Case Tests
- Test with various combinations of include/exclude patterns
- Test split configurations with overlapping criteria
- Test complex nested configurations

## Notes

- All fixture functions automatically copy configs to `tmp_path` for safe modification
- Original config files in this directory should not be modified during tests
- Use `temp_config_from_fixture` for dynamic config selection
- The fixtures handle cleanup automatically via pytest's `tmp_path` fixture
