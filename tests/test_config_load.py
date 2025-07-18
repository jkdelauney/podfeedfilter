"""
Unit tests for config.load_config function.

Test scenarios:
• Correct parsing of base output + splits into multiple FeedConfig objects.
• Defaults for optional fields.
• Handling empty feeds: list.
• Error conditions (missing url, invalid YAML) expecting exceptions.
"""
import pytest
import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List

from podfeedfilter.config import load_config, FeedConfig


class TestLoadConfig:
    """Test class for load_config function."""

    def test_basic_config_with_output_and_splits(self, tmp_path):
        """Test correct parsing of base output + splits into multiple FeedConfig objects."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    output: "base_output.xml"
    include: ["python", "programming"]
    exclude: ["boring"]
    title: "Base Feed"
    description: "Base feed description"
    splits:
      - output: "split1.xml"
        include: ["advanced"]
        exclude: ["beginner"]
        title: "Advanced Topics"
        description: "Advanced programming topics"
      - output: "split2.xml"
        include: ["beginner"]
        title: "Beginner Topics"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        # Should have 3 FeedConfig objects: 1 base + 2 splits
        assert len(result) == 3
        
        # Check base config
        base_config = result[0]
        assert base_config.url == "https://example.com/feed.xml"
        assert base_config.output == "base_output.xml"
        assert base_config.include == ["python", "programming"]
        assert base_config.exclude == ["boring"]
        assert base_config.title == "Base Feed"
        assert base_config.description == "Base feed description"
        
        # Check first split
        split1 = result[1]
        assert split1.url == "https://example.com/feed.xml"
        assert split1.output == "split1.xml"
        assert split1.include == ["advanced"]
        assert split1.exclude == ["beginner"]
        assert split1.title == "Advanced Topics"
        assert split1.description == "Advanced programming topics"
        
        # Check second split
        split2 = result[2]
        assert split2.url == "https://example.com/feed.xml"
        assert split2.output == "split2.xml"
        assert split2.include == ["beginner"]
        assert split2.exclude == []  # Default empty list
        assert split2.title == "Beginner Topics"
        assert split2.description is None  # Default None

    def test_splits_only_no_base_output(self, tmp_path):
        """Test feed with only splits and no base output."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    splits:
      - output: "split1.xml"
        include: ["tech"]
      - output: "split2.xml"
        include: ["science"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        # Should have only 2 FeedConfig objects from splits
        assert len(result) == 2
        
        assert result[0].url == "https://example.com/feed.xml"
        assert result[0].output == "split1.xml"
        assert result[0].include == ["tech"]
        
        assert result[1].url == "https://example.com/feed.xml"
        assert result[1].output == "split2.xml"
        assert result[1].include == ["science"]

    def test_split_vs_splits_key_compatibility(self, tmp_path):
        """Test that both 'split' and 'splits' keys work."""
        config_content = """
feeds:
  - url: "https://example.com/feed1.xml"
    splits:
      - output: "from_splits.xml"
        include: ["tech"]
  - url: "https://example.com/feed2.xml"
    split:
      - output: "from_split.xml"
        include: ["science"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert len(result) == 2
        assert result[0].output == "from_splits.xml"
        assert result[1].output == "from_split.xml"

    def test_defaults_for_optional_fields(self, tmp_path):
        """Test defaults for optional fields."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    output: "test.xml"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert len(result) == 1
        config = result[0]
        
        # Check required fields
        assert config.url == "https://example.com/feed.xml"
        assert config.output == "test.xml"
        
        # Check optional fields have correct defaults
        assert config.include == []
        assert config.exclude == []
        assert config.title is None
        assert config.description is None

    def test_default_output_filename(self, tmp_path):
        """Test that default output filename is used when not specified."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    include: ["python"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert len(result) == 1
        assert result[0].output == "filtered.xml"

    def test_none_values_converted_to_empty_lists(self, tmp_path):
        """Test that None values for include/exclude are converted to empty lists."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    output: "test.xml"
    include: null
    exclude: null
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert len(result) == 1
        config = result[0]
        
        assert config.include == []
        assert config.exclude == []

    def test_empty_feeds_list(self, tmp_path):
        """Test handling empty feeds: list."""
        config_content = """
feeds: []
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_feeds_key(self, tmp_path):
        """Test handling missing feeds key."""
        config_content = """
some_other_key: "value"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_empty_config_file(self, tmp_path):
        """Test handling completely empty config file."""
        config_content = ""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_missing_url_raises_key_error(self, tmp_path):
        """Test that missing url raises KeyError."""
        config_content = """
feeds:
  - output: "test.xml"
    include: ["python"]
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        with pytest.raises(KeyError, match="url"):
            load_config(str(config_file))

    def test_invalid_yaml_raises_yaml_error(self, tmp_path):
        """Test that invalid YAML raises yaml.YAMLError."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    include: ["python"
    # Missing closing bracket
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        with pytest.raises(yaml.YAMLError):
            load_config(str(config_file))

    def test_nonexistent_file_raises_file_not_found_error(self):
        """Test that non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/path/config.yaml")

    def test_multiple_feeds_with_mixed_configurations(self, tmp_path):
        """Test multiple feeds with various configurations."""
        config_content = """
feeds:
  - url: "https://example.com/feed1.xml"
    output: "feed1.xml"
    include: ["python"]
    
  - url: "https://example.com/feed2.xml"
    splits:
      - output: "feed2_split1.xml"
        include: ["tech"]
      - output: "feed2_split2.xml"
        exclude: ["boring"]
        
  - url: "https://example.com/feed3.xml"
    output: "feed3.xml"
    title: "Custom Feed"
    splits:
      - output: "feed3_split.xml"
        title: "Split Feed"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        # Should have 5 FeedConfig objects: 1 + 0 + 2 + 1 + 1 = 5
        assert len(result) == 5
        
        # Check that all have correct URLs
        expected_urls = [
            "https://example.com/feed1.xml",
            "https://example.com/feed2.xml",
            "https://example.com/feed2.xml",
            "https://example.com/feed3.xml",
            "https://example.com/feed3.xml"
        ]
        
        for i, config in enumerate(result):
            assert config.url == expected_urls[i]

    def test_feed_with_only_url_no_base_output(self, tmp_path):
        """Test feed with only URL and no other configuration doesn't create base output."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        # Should be empty because no output, include, exclude, title, or description
        assert len(result) == 0

    def test_base_output_created_with_any_optional_field(self, tmp_path):
        """Test that base output is created when any optional field is present."""
        test_cases = [
            {"output": "test.xml"},
            {"include": ["python"]},
            {"exclude": ["boring"]},
            {"title": "Test Feed"},
            {"description": "Test description"}
        ]
        
        for i, extra_config in enumerate(test_cases):
            config_content = f"""
feeds:
  - url: "https://example.com/feed{i}.xml"
"""
            # Add the extra configuration
            for key, value in extra_config.items():
                if isinstance(value, str):
                    config_content += f'    {key}: "{value}"\n'
                else:
                    config_content += f'    {key}: {value}\n'
            
            config_file = tmp_path / f"config{i}.yaml"
            config_file.write_text(config_content)
            
            result = load_config(str(config_file))
            
            assert len(result) == 1, f"Failed for config with {extra_config}"
            assert result[0].url == f"https://example.com/feed{i}.xml"

    def test_dataclass_fields_validation(self, tmp_path):
        """Test that FeedConfig objects have correct field types."""
        config_content = """
feeds:
  - url: "https://example.com/feed.xml"
    output: "test.xml"
    include: ["python", "programming"]
    exclude: ["boring", "ads"]
    title: "Test Feed"
    description: "Test description"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = load_config(str(config_file))
        
        assert len(result) == 1
        config = result[0]
        
        # Check types
        assert isinstance(config.url, str)
        assert isinstance(config.output, str)
        assert isinstance(config.include, list)
        assert isinstance(config.exclude, list)
        assert isinstance(config.title, str)
        assert isinstance(config.description, str)
        
        # Check values
        assert config.url == "https://example.com/feed.xml"
        assert config.output == "test.xml"
        assert config.include == ["python", "programming"]
        assert config.exclude == ["boring", "ads"]
        assert config.title == "Test Feed"
        assert config.description == "Test description"
