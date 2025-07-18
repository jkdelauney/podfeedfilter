"""
Example tests demonstrating usage of config fixtures.
"""
import pytest
import yaml
from pathlib import Path


def test_basic_include_exclude_config(basic_include_exclude_config):
    """Test that basic include/exclude config fixture works."""
    # The fixture returns a Path object to a temporary copy
    assert isinstance(basic_include_exclude_config, Path)
    assert basic_include_exclude_config.exists()

    # Load and verify the config content
    with open(basic_include_exclude_config, 'r') as f:
        config = yaml.safe_load(f)

    assert 'include_patterns' in config
    assert 'exclude_patterns' in config
    assert '*.mp3' in config['include_patterns']
    assert '*.txt' in config['exclude_patterns']


def test_splits_config(splits_config):
    """Test that splits config fixture works."""
    assert isinstance(splits_config, Path)
    assert splits_config.exists()

    with open(splits_config, 'r') as f:
        config = yaml.safe_load(f)

    assert 'splits' in config
    assert len(config['splits']) == 3
    assert config['splits'][0]['name'] == 'episodes'
    assert config['splits'][1]['name'] == 'interviews'
    assert config['splits'][2]['name'] == 'music'


def test_missing_keys_config(missing_keys_config):
    """Test that missing keys config fixture works."""
    assert isinstance(missing_keys_config, Path)
    assert missing_keys_config.exists()

    with open(missing_keys_config, 'r') as f:
        config = yaml.safe_load(f)

    # This config should have missing keys
    assert 'include_patterns' in config
    assert 'exclude_patterns' not in config  # This key is missing


def test_bad_syntax_config(bad_syntax_config):
    """Test that bad syntax config fixture works."""
    assert isinstance(bad_syntax_config, Path)
    assert bad_syntax_config.exists()

    # This should raise an error due to bad YAML syntax
    with pytest.raises(yaml.YAMLError):
        with open(bad_syntax_config, 'r') as f:
            yaml.safe_load(f)


def test_empty_config(empty_config):
    """Test that empty config fixture works."""
    assert isinstance(empty_config, Path)
    assert empty_config.exists()

    with open(empty_config, 'r') as f:
        config = yaml.safe_load(f)

    # Empty config should return None
    assert config is None


def test_complex_config(complex_config):
    """Test that complex config fixture works."""
    assert isinstance(complex_config, Path)
    assert complex_config.exists()

    with open(complex_config, 'r') as f:
        config = yaml.safe_load(f)

    assert 'global_settings' in config
    assert 'splits' in config
    assert 'output_settings' in config
    assert len(config['splits']) == 2


def test_temp_config_from_fixture(temp_config_from_fixture):
    """Test the generic temp config fixture helper."""
    # Test copying a specific config
    temp_config = temp_config_from_fixture('basic_include_exclude')
    assert isinstance(temp_config, Path)
    assert temp_config.exists()

    # Test that it raises error for non-existent config
    with pytest.raises(FileNotFoundError):
        temp_config_from_fixture('non_existent_config')


def test_all_temp_configs(all_temp_configs):
    """Test that all temp configs fixture works."""
    assert isinstance(all_temp_configs, dict)

    expected_configs = [
        'basic_include_exclude',
        'splits_config',
        'missing_keys',
        'bad_syntax',
        'empty_config',
        'complex_config'
    ]

    for config_name in expected_configs:
        assert config_name in all_temp_configs
        assert isinstance(all_temp_configs[config_name], Path)
        assert all_temp_configs[config_name].exists()


def test_config_files_fixture(config_files):
    """Test that config_files fixture provides original paths."""
    assert isinstance(config_files, dict)

    expected_configs = [
        'basic_include_exclude',
        'splits_config',
        'missing_keys',
        'bad_syntax',
        'empty_config',
        'complex_config'
    ]

    for config_name in expected_configs:
        assert config_name in config_files
        assert isinstance(config_files[config_name], Path)
        # Note: These point to the original files in tests/data/configs/
        # They should exist but should NOT be modified in tests
        assert config_files[config_name].exists()
