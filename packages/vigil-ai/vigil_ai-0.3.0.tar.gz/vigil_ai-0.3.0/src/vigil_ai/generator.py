"""AI-powered pipeline generation using foundation models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel

from vigil_ai.cache import cached
from vigil_ai.models import ModelDomain, get_model
from vigil_ai.retry import with_retry

console = Console()


@with_retry
def _call_model_api(model_name: str | None, prompt: str, max_tokens: int = 4096, domain: ModelDomain | None = None, **kwargs: Any) -> str:
    """Make API call to foundation model with retry logic.

    Args:
        model_name: Model name (if None, uses domain or default)
        prompt: Prompt text
        max_tokens: Maximum tokens to generate
        domain: Scientific domain (if model_name is None)
        **kwargs: Additional model parameters

    Returns:
        Generated text
    """
    model = get_model(name=model_name, domain=domain)
    return model.generate(prompt, max_tokens=max_tokens, **kwargs)


@cached
def generate_pipeline(
    description: str,
    template: str = "genomics-starter",
    model: str | None = None,
    domain: ModelDomain | None = None,
) -> str:
    """Generate a Snakemake pipeline from natural language description.

    Args:
        description: Natural language description of the analysis
        template: Base template to use (genomics-starter, imaging-starter, etc.)
        model: Model name (if None, uses domain or default)
        domain: Scientific domain to infer model (biology, chemistry, etc.)

    Returns:
        Generated Snakefile content

    Examples:
        >>> # Use default model (Claude)
        >>> pipeline = generate_pipeline(
        ...     "Filter variants by quality >30, annotate with Ensembl, calculate Ti/Tv ratio"
        ... )
        >>>
        >>> # Use domain-specific model
        >>> pipeline = generate_pipeline(
        ...     "Analyze protein sequences",
        ...     domain=ModelDomain.BIOLOGY
        ... )
        >>>
        >>> # Use specific model
        >>> pipeline = generate_pipeline(
        ...     "Process chemical structures",
        ...     model="galactica-6.7b"
        ... )
    """

    # Build context-aware prompt
    prompt = f"""You are an expert in creating Snakemake workflows for reproducible science.

Generate a Snakemake pipeline (Snakefile) that implements the following analysis:

{description}

Use the {template} template as a base. The pipeline should:
1. Follow Snakemake best practices
2. Use clear rule names
3. Include input/output specifications
4. Reference script files in ../lib/steps/
5. Be production-ready and realistic

Output ONLY the Snakefile content with no explanations or markdown formatting.
Start directly with the rules."""

    try:
        return _call_model_api(model, prompt, max_tokens=4096, domain=domain)

    except Exception as e:
        console.print(f"[red]Error generating pipeline: {e}[/red]")
        raise


def ai_create(
    description: str,
    output: Optional[Path] = None,
    template: str = "genomics-starter",
    model: str | None = None,
    domain: ModelDomain | None = None,
    dry_run: bool = False,
) -> None:
    """Create a Vigil pipeline from natural language description.

    This is the CLI-friendly version that writes to file and provides feedback.

    Args:
        description: Natural language description of the analysis
        output: Output file path (default: app/code/pipelines/Snakefile)
        template: Base template to use
        model: Model name (if None, uses domain or default)
        domain: Scientific domain for model selection
        dry_run: If True, only print the generated pipeline without saving

    Examples:
        >>> ai_create("Filter variants >30, calculate Ti/Tv")
        ✓ Pipeline created: app/code/pipelines/Snakefile

        >>> ai_create("Process images, segment cells, count", dry_run=True)
        [prints generated pipeline]
    """
    if output is None:
        output = Path("app/code/pipelines/Snakefile")

    model_desc = model or domain or "default"
    console.print(
        Panel(
            f"[cyan]Generating pipeline with AI...[/cyan]\\n\\n"
            f"Description: {description}\\n"
            f"Template: {template}\\n"
            f"Model: {model_desc}",
            title="Vigil AI",
        )
    )

    try:
        pipeline_content = generate_pipeline(description, template, model, domain)

        if dry_run:
            console.print("\\n[bold]Generated Pipeline:[/bold]\\n")
            console.print(pipeline_content)
            return

        # Write to file
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(pipeline_content)

        console.print(f"\\n[green]✓[/green] Pipeline created: {output}")
        console.print("\\n[bold]Next steps:[/bold]")
        console.print("  1. Review the generated pipeline")
        console.print("  2. Create necessary step scripts in app/code/lib/steps/")
        console.print("  3. vigil run --cores 4")

    except Exception as e:
        console.print(f"\\n[red]✗ Failed to create pipeline: {e}[/red]")
        raise


@cached
def generate_step_script(
    description: str,
    rule_name: str = "",
    inputs: list[str] | None = None,
    outputs: list[str] | None = None,
    language: str = "python",
    model: str | None = None,
    domain: ModelDomain | None = None,
) -> str:
    """Generate a step script for a Snakemake rule.

    Args:
        description: What the step should do (used as cache key)
        rule_name: Name of the rule
        inputs: List of input file patterns
        outputs: List of output file patterns
        language: Programming language (python, r, shell)
        model: Model name (if None, uses domain or default)
        domain: Scientific domain for model selection

    Returns:
        Generated script content

    Examples:
        >>> script = generate_step_script(
        ...     "Filter variants by quality score",
        ...     rule_name="filter_variants",
        ...     inputs=["variants.csv"],
        ...     outputs=["filtered.parquet"],
        ... )
    """
    inputs = inputs or []
    outputs = outputs or []

    prompt = f"""Generate a {language} script for a Snakemake rule that does:

{description}

Rule name: {rule_name}
Inputs: {', '.join(inputs)}
Outputs: {', '.join(outputs)}

The script should:
1. Access inputs via snakemake.input
2. Access outputs via snakemake.output
3. Access params via snakemake.params (if any)
4. Include proper error handling
5. Be production-ready

Output ONLY the script code with no explanations."""

    return _call_model_api(model, prompt, max_tokens=2048, domain=domain)
