"""Tests for vigil_ai.generator module."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from vigil_ai.generator import ai_create, generate_pipeline, generate_step_script


@pytest.fixture
def mock_api_response():
    """Mock API response text."""
    return """rule filter_variants:
    input: "data/samples/variants.csv"
    output: "artifacts/filtered.parquet"
    params: min_quality = 30
    script: "../lib/steps/filter.py"

rule calculate_metrics:
    input: "artifacts/filtered.parquet"
    output: "artifacts/metrics.json"
    script: "../lib/steps/metrics.py"
"""


@pytest.fixture
def mock_model_api(mock_api_response):
    """Mock _call_model_api helper."""
    with patch("vigil_ai.generator._call_model_api") as mock:
        mock.return_value = mock_api_response
        yield mock


class TestGeneratePipeline:
    """Tests for generate_pipeline function."""

    def test_generate_pipeline_success(self, mock_model_api, monkeypatch):
        """Test successful pipeline generation."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        result = generate_pipeline("Filter variants by quality >30")

        assert "rule filter_variants" in result
        assert "rule calculate_metrics" in result
        assert "input:" in result
        assert "output:" in result
        mock_model_api.assert_called_once()

    def test_generate_pipeline_no_api_key(self, monkeypatch):
        """Test pipeline generation fails without API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            generate_pipeline("Test description")

    def test_generate_pipeline_with_template(self, mock_model_api, monkeypatch):
        """Test pipeline generation with specific template."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        result = generate_pipeline(
            "Process images",
            template="imaging-starter"
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_pipeline_api_error(self, monkeypatch):
        """Test pipeline generation handles API errors."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        with patch("vigil_ai.generator._call_model_api") as mock:
            mock.side_effect = Exception("API Error")

            with pytest.raises(Exception, match="API Error"):
                generate_pipeline("Test")


class TestAICreate:
    """Tests for ai_create CLI function."""

    def test_ai_create_dry_run(self, mock_model_api, monkeypatch, capsys):
        """Test dry run mode prints pipeline."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        ai_create("Test description", dry_run=True)

        captured = capsys.readouterr()
        assert "rule filter_variants" in captured.out

    def test_ai_create_writes_file(self, mock_model_api, monkeypatch, tmp_path):
        """Test pipeline is written to file."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        output_file = tmp_path / "Snakefile"
        ai_create("Test description", output=output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "rule filter_variants" in content

    def test_ai_create_no_anthropic_package(self, monkeypatch):
        """Test error when anthropic package not installed."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Patch builtins.__import__ to raise ImportError for anthropic
        def mock_import(name, *args, **kwargs):
            if name == "anthropic":
                raise ImportError("No module named 'anthropic'")
            return __import__(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError, match="anthropic package required"):
                generate_pipeline("Test")


class TestGenerateStepScript:
    """Tests for generate_step_script function."""

    def test_generate_step_script_python(self, mock_model_api, monkeypatch):
        """Test Python script generation."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        # Set the mock return value
        script_content = '''import pandas as pd

# Load input
variants = pd.read_csv(snakemake.input[0])

# Filter by quality
filtered = variants[variants['quality_score'] > snakemake.params.min_quality]

# Save output
filtered.to_parquet(snakemake.output[0])
'''
        with patch("vigil_ai.generator._call_model_api") as mock:
            mock.return_value = script_content

            result = generate_step_script(
                "Filter variants by quality",
                rule_name="filter_variants",
                inputs=["variants.csv"],
                outputs=["filtered.parquet"],
            )

            assert "import pandas" in result
            assert "snakemake" in result
            mock.assert_called_once()

    def test_generate_step_script_r(self, monkeypatch):
        """Test R script generation."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

        script_content = "# R script\nlibrary(tidyverse)"

        with patch("vigil_ai.generator._call_model_api") as mock:
            mock.return_value = script_content

            result = generate_step_script(
                "Process data",
                rule_name="process_data",
                inputs=["input.csv"],
                outputs=["output.csv"],
                language="r",
            )

            assert isinstance(result, str)
            assert "library(tidyverse)" in result
            mock.assert_called_once()
