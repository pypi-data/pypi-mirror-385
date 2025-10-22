"""Tests for vigil_ai.debugger module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vigil_ai.debugger import ai_debug, ai_debug_command


@pytest.fixture
def mock_debug_response():
    """Mock AI debug response."""
    return """Root Cause:
The error indicates that the input file 'variants.csv' is missing.

Suggested fixes:
1. Check that your data file exists in app/data/samples/
2. Verify the file name matches exactly (case-sensitive)
3. Run: ls app/data/samples/ to see available files

Prevention:
Add input validation before running the pipeline.
"""


@pytest.fixture
def mock_claude_api(mock_debug_response):
    """Mock _call_claude_api helper."""
    with patch("vigil_ai.debugger._call_claude_api") as mock:
        mock.return_value = mock_debug_response
        yield mock


class TestAIDebug:
    """Tests for ai_debug function."""

    def test_ai_debug_success(self, mock_claude_api, monkeypatch):
        """Test successful error analysis."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        result = ai_debug("FileNotFoundError: variants.csv not found")

        assert "Root Cause" in result
        assert "Suggested fixes" in result
        assert "variants.csv" in result.lower()

    def test_ai_debug_with_context(self, mock_claude_api, monkeypatch):
        """Test debugging with additional context."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        context = {
            "Snakefile": "rule filter:\n  input: 'variants.csv'",
            "Error log": "FileNotFoundError",
        }

        result = ai_debug("Error message", context=context)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_ai_debug_no_api_key(self, monkeypatch):
        """Test debugging fails without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ai_debug("Test error")

    def test_ai_debug_api_error(self, monkeypatch):
        """Test debugging handles API errors."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        with patch("vigil_ai.debugger._call_claude_api") as mock:
            mock.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                ai_debug("Test error")


class TestAIDebugCommand:
    """Tests for ai_debug_command CLI function."""

    def test_debug_command_with_file(self, mock_claude_api, monkeypatch, tmp_path):
        """Test debugging with error log file."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        error_log = tmp_path / "error.log"
        error_log.write_text("FileNotFoundError: variants.csv")

        ai_debug_command(error_log=error_log)

        # Should not raise an exception

    def test_debug_command_no_log_file(self, tmp_path, capsys):
        """Test debugging without log file."""
        # Create a fake Snakemake log directory
        snakemake_log = tmp_path / ".snakemake" / "log"
        snakemake_log.mkdir(parents=True)

        # No logs present
        import os
        os.chdir(tmp_path)

        ai_debug_command()

        captured = capsys.readouterr()
        assert "No error logs found" in captured.out or "error" in captured.out.lower()

    def test_debug_command_interactive_mode(self, mock_claude_api, monkeypatch):
        """Test interactive debugging mode."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        with patch("sys.stdin.read", return_value="Test error message"):
            ai_debug_command(interactive=True)

        # Should not raise exception
