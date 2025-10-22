"""Tests for vigil_ai.optimizer module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vigil_ai.optimizer import ai_optimize, ai_optimize_command


@pytest.fixture
def sample_snakefile(tmp_path):
    """Create a sample Snakefile for testing."""
    snakefile = tmp_path / "Snakefile"
    snakefile.write_text("""
rule filter_variants:
    input: "data/variants.csv"
    output: "artifacts/filtered.parquet"
    shell: "python filter.py {input} {output}"

rule annotate:
    input: "artifacts/filtered.parquet"
    output: "artifacts/annotated.parquet"
    shell: "python annotate.py {input} {output}"
""")
    return snakefile


@pytest.fixture
def mock_optimize_response():
    """Mock optimization response."""
    return """Rule: filter_variants
Issue: Sequential processing of variants
Suggestion: Add threads directive and use parallel processing
Impact: 4x faster with 4 cores

Rule: annotate
Issue: Repeated API calls to Ensembl
Suggestion: Implement local caching for annotation queries
Impact: 10x faster on reruns
"""


@pytest.fixture
def mock_claude_api(mock_optimize_response):
    """Mock _call_claude_api helper."""
    with patch("vigil_ai.optimizer._call_claude_api") as mock:
        mock.return_value = mock_optimize_response
        yield mock


class TestAIOptimize:
    """Tests for ai_optimize function."""

    def test_optimize_success(self, mock_claude_api, sample_snakefile, monkeypatch):
        """Test successful optimization analysis."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        result = ai_optimize(snakefile=sample_snakefile)

        assert "optimization_suggestions" in result
        assert "filter_variants" in result["optimization_suggestions"]
        assert "annotate" in result["optimization_suggestions"]

    def test_optimize_with_focus(self, mock_claude_api, sample_snakefile, monkeypatch):
        """Test optimization with specific focus."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        result = ai_optimize(snakefile=sample_snakefile, focus="speed")

        assert "optimization_suggestions" in result
        assert isinstance(result["optimization_suggestions"], str)

    def test_optimize_no_snakefile(self, tmp_path, monkeypatch):
        """Test optimization fails when Snakefile doesn't exist."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        nonexistent = tmp_path / "nonexistent" / "Snakefile"

        with pytest.raises(FileNotFoundError):
            ai_optimize(snakefile=nonexistent)

    def test_optimize_no_api_key(self, sample_snakefile, monkeypatch):
        """Test optimization fails without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ai_optimize(snakefile=sample_snakefile)

    def test_optimize_api_error(self, sample_snakefile, monkeypatch):
        """Test optimization handles API errors."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Disable caching to ensure API is called
        with patch("vigil_ai.optimizer.get_cached_response") as cache_mock:
            cache_mock.return_value = None

            with patch("vigil_ai.optimizer._call_claude_api") as api_mock:
                api_mock.side_effect = Exception("API Error")

                with pytest.raises(Exception):
                    ai_optimize(snakefile=sample_snakefile)


class TestAIOptimizeCommand:
    """Tests for ai_optimize_command CLI function."""

    def test_optimize_command_success(self, mock_claude_api, sample_snakefile, monkeypatch):
        """Test optimization command execution."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        ai_optimize_command(snakefile=sample_snakefile)

        # Should not raise exception

    def test_optimize_command_with_output(
        self, mock_claude_api, sample_snakefile, tmp_path, monkeypatch
    ):
        """Test saving optimization suggestions to file."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        output_file = tmp_path / "suggestions.md"
        ai_optimize_command(snakefile=sample_snakefile, output=output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "filter_variants" in content

    def test_optimize_command_with_focus(
        self, mock_claude_api, sample_snakefile, monkeypatch
    ):
        """Test optimization with specific focus area."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        ai_optimize_command(snakefile=sample_snakefile, focus="cost")

        # Should not raise exception
