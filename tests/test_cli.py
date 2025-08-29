"""Command-line interface tests for podfeedfilter main module.

Tests CLI functionality using both subprocess.run() for external
command invocation and direct main() function calls with sys.argv
monkeypatching. Validates argument parsing, config file handling,
error conditions, and proper exit codes with output verification.
"""
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
import yaml

from podfeedfilter.__main__ import main


def test_cli_subprocess_with_basic_config(tmp_path):
    """Test CLI invocation via subprocess.run with basic config."""
    # Create a test config file - use a URL that doesn't require mocking
    # We'll just test that the subprocess runs without error, even if no
    # output is created
    config_content = {
        "feeds": [
            {
                "url": "http://nonexistent.example.com/feed.xml",
                "output": str(tmp_path / "test_output.xml"),
                "include": ["Tech"],
                "exclude": ["advertisement"]
            }
        ]
    }

    config_path = tmp_path / "test_config.yaml"
    with open(config_path, 'w', encoding="utf-8") as f:
        yaml.dump(config_content, f)

    # Run the CLI command via subprocess
    result = subprocess.run([
        sys.executable, "-m", "podfeedfilter",
        "-c", str(config_path)
    ], capture_output=True, text=True)

    # Check command executed successfully (it should exit cleanly even if no
    # files are created)
    assert result.returncode == 0, (
        f"Command failed with stderr: {result.stderr}"
    )

    # The output file may not be created if the feed is empty/unreachable, but
    # command should exit cleanly
    # This test verifies the CLI interface works correctly


def test_cli_subprocess_with_splits_config(tmp_path):
    """Test CLI invocation via subprocess.run with splits configuration."""
    # Create a test config with splits - use non-existent URL for subprocess
    # test
    config_content = {
        "feeds": [
            {
                "url": "http://nonexistent.example.com/feed.xml",
                "splits": [
                    {
                        "output": str(tmp_path / "tech_episodes.xml"),
                        "include": ["Tech"],
                        "exclude": ["advertisement"]
                    },
                    {
                        "output": str(tmp_path / "politics_episodes.xml"),
                        "include": ["Election"],
                        "exclude": ["tech"]
                    },
                    {
                        "output": str(tmp_path / "all_episodes.xml"),
                        "exclude": ["advertisement", "sponsored"]
                    }
                ]
            }
        ]
    }

    config_path = tmp_path / "splits_config.yaml"
    with open(config_path, 'w', encoding="utf8") as f:
        yaml.dump(config_content, f)

    # Run the CLI command via subprocess
    result = subprocess.run([
        sys.executable, "-m", "podfeedfilter",
        "-c", str(config_path)
    ], capture_output=True, text=True, check=False)

    # Check command executed successfully (should exit cleanly even if no files
    # created)
    assert result.returncode == 0, (
        f"Command failed with stderr: {result.stderr}"
    )

    # The output files may not be created if the feed is empty/unreachable, but
    # command should exit cleanly
    # This test verifies the CLI interface works correctly with splits
    # configuration


def test_cli_subprocess_with_nonexistent_config(tmp_path):
    """Test CLI invocation via subprocess.run with non-existent config file."""
    nonexistent_config = tmp_path / "nonexistent.yaml"

    # Run the CLI command via subprocess
    result = subprocess.run([
        sys.executable, "-m", "podfeedfilter",
        "-c", str(nonexistent_config)
    ], capture_output=True, text=True, check=False)

    # Check command failed as expected
    assert result.returncode != 0, (
        "Command should have failed with non-existent config"
    )
    assert (
        "No such file or directory" in result.stderr or
        "FileNotFoundError" in result.stderr
    )


def test_cli_subprocess_with_invalid_config(tmp_path):
    """Test CLI invocation via subprocess.run with invalid YAML config."""
    # Create invalid YAML config
    invalid_config = tmp_path / "invalid_config.yaml"
    with open(invalid_config, 'w', encoding="utf-8") as f:
        f.write("invalid: yaml: content:\n  - [broken")

    # Run the CLI command via subprocess
    result = subprocess.run([
        sys.executable, "-m", "podfeedfilter",
        "-c", str(invalid_config)
    ], capture_output=True, text=True, check=False)

    # Check command failed as expected
    assert result.returncode != 0, (
        "Command should have failed with invalid config"
    )


def test_cli_direct_main_call_with_basic_config(tmp_path,
                                                mock_feedparser_parse,
                                                monkeypatch, capsys):
    """
    Test main() function directly with monkeypatch.setattr(sys, 'argv', [...]).
    """
    # Create a test config file
    config_content = {
        "feeds": [
            {
                "url": "http://test/feed1",
                "output": str(tmp_path / "direct_output.xml"),
                "include": ["Tech"],
                "exclude": ["advertisement"]
            }
        ]
    }

    config_path = tmp_path / "direct_config.yaml"
    with open(config_path, 'w', encoding="utf-8") as f:
        yaml.dump(config_content, f)

    # Set up sys.argv for the main function
    test_argv = ["podfeedfilter", "-c", str(config_path)]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly
    main()

    # Capture stdout/stderr
    captured = capsys.readouterr()

    # Check expected output file was created
    output_file = tmp_path / "direct_output.xml"
    assert output_file.exists(), "Expected output file was not created"

    # Verify the output file contains valid XML (handle both single and double
    # quotes)
    content = output_file.read_text()
    assert (
        '<?xml version="1.0" encoding="UTF-8"?>' in content or
        "<?xml version='1.0' encoding='UTF-8'?>" in content
    ), (
        f"XML declaration not found in: {content[:200]}..."
    )
    assert (
        'version="2.0"' in content or
        "version='2.0'" in content
    ), (
        f"RSS version not found in: {content[:200]}..."
    )


def test_cli_direct_main_call_with_splits_config(tmp_path,
                                                 mock_feedparser_parse,
                                                 monkeypatch, capsys):
    """Test main() function directly with splits configuration."""
    # Create a test config with splits
    config_content = {
        "feeds": [
            {
                "url": "http://test/feed1",
                "splits": [
                    {
                        "output": str(tmp_path / "direct_tech.xml"),
                        "include": ["Tech"],
                        "exclude": ["advertisement"]
                    },
                    {
                        "output": str(tmp_path / "direct_politics.xml"),
                        "include": ["Election"],
                        "exclude": ["tech"]
                    }
                ]
            }
        ]
    }

    config_path = tmp_path / "direct_splits_config.yaml"
    with open(config_path, 'w', encoding="utf-8") as f:
        yaml.dump(config_content, f)

    # Set up sys.argv for the main function
    test_argv = ["podfeedfilter", "-c", str(config_path)]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly
    main()

    # Capture stdout/stderr
    captured = capsys.readouterr()

    # Check all expected output files were created
    expected_files = [
        tmp_path / "direct_tech.xml",
        tmp_path / "direct_politics.xml"
    ]

    for output_file in expected_files:
        assert output_file.exists(), (
            f"Expected output file {output_file} was not created"
        )

        # Verify the output file contains valid XML (handle both single and
        # double quotes)
        content = output_file.read_text()
        assert (
            '<?xml version="1.0" encoding="UTF-8"?>' in content or
            "<?xml version='1.0' encoding='UTF-8'?>" in content
        ), (
            f"XML declaration not found in: {content[:200]}..."
        )
        assert (
            'version="2.0"' in content or
            "version='2.0'" in content
        ), (
            f"RSS version not found in: {content[:200]}..."
        )


def test_cli_direct_main_call_with_default_config(tmp_path,
                                                  mock_feedparser_parse,
                                                  monkeypatch, capsys):
    """Test main() function directly with default config file name."""
    # Create a test config file with default name
    config_content = {
        "feeds": [
            {
                "url": "http://test/feed1",
                "output": str(tmp_path / "default_output.xml"),
                "include": ["Tech"]
            }
        ]
    }

    # Create feeds.yaml in tmp_path (the default config name)
    config_path = tmp_path / "feeds.yaml"
    with open(config_path, 'w', encoding="utf-8") as f:
        yaml.dump(config_content, f)

    # Change to tmp_path so default config is found
    monkeypatch.chdir(tmp_path)

    # Set up sys.argv for the main function
    # (no -c argument, should use default)
    test_argv = ["podfeedfilter"]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly
    main()

    # Capture stdout/stderr
    captured = capsys.readouterr()

    # Check expected output file was created
    output_file = tmp_path / "default_output.xml"
    assert output_file.exists(), "Expected output file was not created"

    # Verify the output file contains valid XML
    # (handle both single and double quotes)
    content = output_file.read_text()
    assert (
        '<?xml version="1.0" encoding="UTF-8"?>' in content or
        "<?xml version='1.0' encoding='UTF-8'?>" in content
    ), (
        f"XML declaration not found in: {content[:200]}..."
    )
    assert (
        'version="2.0"' in content or
        "version='2.0'" in content
    ), (
        f"RSS version not found in: {content[:200]}..."
    )


def test_cli_direct_main_call_with_nonexistent_config(tmp_path,
                                                      monkeypatch, capsys):
    """Test main() function directly with non-existent config file."""
    nonexistent_config = tmp_path / "nonexistent.yaml"

    # Set up sys.argv for the main function
    test_argv = ["podfeedfilter", "-c", str(nonexistent_config)]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly and expect it to raise an exception
    with pytest.raises(FileNotFoundError):
        main()


def test_cli_direct_main_call_with_invalid_config(tmp_path, monkeypatch,
                                                  capsys):
    """Test main() function directly with invalid YAML config."""
    # Create invalid YAML config
    invalid_config = tmp_path / "invalid_config.yaml"
    with open(invalid_config, 'w', encoding="utf-8") as f:
        f.write("invalid: yaml: content:\n  - [broken")

    # Set up sys.argv for the main function
    test_argv = ["podfeedfilter", "-c", str(invalid_config)]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly and expect it to raise an exception
    with pytest.raises(yaml.YAMLError):
        main()


def test_cli_help_flag_subprocess():
    """Test CLI help flag via subprocess.run."""
    result = subprocess.run([
        sys.executable, "-m", "podfeedfilter",
        "--help"
    ], capture_output=True, text=True, check=False)

    # Check command executed successfully
    assert result.returncode == 0, (
        f"Help command failed with stderr: {result.stderr}"
    )

    # Check help text contains expected content
    assert "Filter podcast feeds" in result.stdout
    assert "--config" in result.stdout or "-c" in result.stdout


def test_cli_help_flag_direct_main(monkeypatch, capsys):
    """Test CLI help flag via direct main() call."""
    # Set up sys.argv for the main function
    test_argv = ["podfeedfilter", "--help"]
    monkeypatch.setattr(sys, 'argv', test_argv)

    # Call main() directly and expect SystemExit (argparse exits with help)
    with pytest.raises(SystemExit) as exc_info:
        main()

    # Check it exited with code 0 (success)
    assert exc_info.value.code == 0

    # Capture stdout/stderr
    captured = capsys.readouterr()

    # Check help text contains expected content
    assert "Filter podcast feeds" in captured.out
    assert "--config" in captured.out or "-c" in captured.out


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
