"""High-level pipeline generation task interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vigil_ai.generator import ai_create, generate_pipeline
from vigil_ai.models import ModelDomain


class PipelineGenerator:
    """High-level interface for generating scientific workflows.

    This class provides a simple, task-focused API for generating Snakemake
    pipelines from natural language descriptions.

    Args:
        domain: Scientific domain (biology, chemistry, materials, general)
        model: Specific model to use (overrides domain selection)
        template: Base template to use (default: genomics-starter)

    Examples:
        >>> # Create generator for biology
        >>> gen = PipelineGenerator(domain="biology")
        >>> pipeline = gen.create("Filter variants by quality >30")
        >>>
        >>> # Use specific model
        >>> gen = PipelineGenerator(model="galactica-6.7b")
        >>> pipeline = gen.create("Analyze protein sequences")
        >>>
        >>> # Save to file
        >>> gen.create_and_save(
        ...     "Process chemical structures",
        ...     output="workflow.smk"
        ... )
    """

    def __init__(
        self,
        domain: str | ModelDomain | None = None,
        model: str | None = None,
        template: str = "genomics-starter",
    ) -> None:
        """Initialize pipeline generator.

        Args:
            domain: Scientific domain for model selection
            model: Specific model name
            template: Workflow template to use
        """
        self.domain = ModelDomain(domain) if isinstance(domain, str) else domain
        self.model = model
        self.template = template

    def create(self, description: str, **kwargs: Any) -> str:
        """Generate a pipeline from natural language.

        Args:
            description: Natural language description of the workflow
            **kwargs: Additional parameters for generate_pipeline

        Returns:
            Generated Snakefile content

        Examples:
            >>> gen = PipelineGenerator(domain="biology")
            >>> pipeline = gen.create(
            ...     "Filter variants >30, annotate with Ensembl, calculate Ti/Tv"
            ... )
        """
        return generate_pipeline(
            description=description,
            template=kwargs.get("template", self.template),
            model=kwargs.get("model", self.model),
            domain=kwargs.get("domain", self.domain),
        )

    def create_and_save(
        self,
        description: str,
        output: str | Path = "app/code/pipelines/Snakefile",
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Path:
        """Generate and save a pipeline.

        Args:
            description: Natural language description
            output: Output file path
            dry_run: If True, only print without saving
            **kwargs: Additional parameters

        Returns:
            Path to saved file (or None if dry_run)

        Examples:
            >>> gen = PipelineGenerator(domain="chemistry")
            >>> path = gen.create_and_save(
            ...     "Screen drug candidates",
            ...     output="drug_screening.smk"
            ... )
        """
        output_path = Path(output)

        ai_create(
            description=description,
            output=output_path if not dry_run else None,
            template=kwargs.get("template", self.template),
            model=kwargs.get("model", self.model),
            domain=kwargs.get("domain", self.domain),
            dry_run=dry_run,
        )

        return output_path if not dry_run else None

    def preview(self, description: str, **kwargs: Any) -> str:
        """Preview a pipeline without saving.

        Args:
            description: Natural language description
            **kwargs: Additional parameters

        Returns:
            Generated pipeline content

        Examples:
            >>> gen = PipelineGenerator()
            >>> preview = gen.preview("Filter variants >30")
            >>> print(preview)
        """
        return self.create(description, **kwargs)

    def __repr__(self) -> str:
        """String representation."""
        model_info = self.model or self.domain or "default"
        return f"PipelineGenerator(model={model_info}, template={self.template})"
