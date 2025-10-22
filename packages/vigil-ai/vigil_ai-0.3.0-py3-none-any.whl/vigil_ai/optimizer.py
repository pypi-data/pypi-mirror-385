"""AI-powered workflow optimization."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from vigil_ai.cache import cache_key, cache_response, get_cached_response
from vigil_ai.config import get_config
from vigil_ai.retry import with_retry

console = Console()


@with_retry
def _call_claude_api(client: Any, model: str, prompt: str, max_tokens: int = 3072) -> str:
    """Make API call to Claude with retry logic.

    Args:
        client: Anthropic client
        model: Model to use
        prompt: Prompt text
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text
    """
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def ai_optimize(
    snakefile: Path | None = None,
    focus: str | None = None,
    model: str = "claude-3-5-sonnet-20241022",
) -> dict[str, str]:
    """Analyze workflow and suggest optimizations.

    Args:
        snakefile: Path to Snakefile to optimize
        focus: Specific aspect to optimize (speed, memory, cost, readability)
        model: Claude model to use

    Returns:
        Dictionary with optimization suggestions

    Examples:
        >>> suggestions = ai_optimize(focus="speed")
        >>> for rule, suggestion in suggestions.items():
        ...     print(f"{rule}: {suggestion}")
        filter_variants: Use parallel processing with --cores
        annotate: Cache results to avoid recomputation
        ...
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. Install with: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    if snakefile is None:
        snakefile = Path("app/code/pipelines/Snakefile")

    if not snakefile.exists():
        raise FileNotFoundError(f"Snakefile not found: {snakefile}")

    snakefile_content = snakefile.read_text()

    # Build the prompt
    focus_prompt = ""
    if focus:
        focus_prompt = f"Focus specifically on optimizing for: {focus}\\n\\n"

    prompt = f"""Analyze this Snakemake workflow and suggest optimizations.

{focus_prompt}Snakefile:
```
{snakefile_content}
```

Provide specific, actionable optimization suggestions for:
1. Performance (speed, parallelization)
2. Resource usage (memory, disk)
3. Cost (cloud execution)
4. Code quality (readability, maintainability)

Format each suggestion as:
Rule: <rule_name>
Issue: <what could be better>
Suggestion: <how to improve>
Impact: <expected improvement>

Be specific and practical."""

    # Check cache
    config = get_config()
    key = cache_key(prompt, model, focus=focus)
    cached = get_cached_response(key)
    if cached is not None:
        return {"optimization_suggestions": cached}

    # Make API call
    client = anthropic.Anthropic(api_key=api_key)

    try:
        response_text = _call_claude_api(client, model, prompt, max_tokens=3072)

        # Cache the result
        cache_response(key, response_text, {"model": model, "focus": focus})

        return {"optimization_suggestions": response_text}

    except Exception as e:
        console.print(f"[red]Error during optimization analysis: {e}[/red]")
        raise


def ai_optimize_command(
    snakefile: Path | None = None,
    focus: str | None = None,
    output: Path | None = None,
) -> None:
    """CLI command for AI-powered optimization.

    Args:
        snakefile: Path to Snakefile
        focus: Optimization focus (speed, memory, cost, readability)
        output: Save suggestions to file

    Examples:
        >>> ai_optimize_command(focus="speed")
        Analyzing workflow...

        Optimization Suggestions:

        Rule: filter_variants
        Issue: Sequential processing of variants
        Suggestion: Add threads directive and use parallel processing
        Impact: 4x faster with 4 cores
        ...
    """
    console.print(
        Panel(
            f"[cyan]Analyzing workflow for optimizations...[/cyan]\\n\\n"
            f"Focus: {focus or 'all aspects'}",
            title="Vigil AI Optimize",
        )
    )

    try:
        suggestions = ai_optimize(snakefile, focus)

        console.print("\\n[bold green]Optimization Suggestions:[/bold green]\\n")
        console.print(suggestions["optimization_suggestions"])

        if output:
            output.write_text(suggestions["optimization_suggestions"])
            console.print(f"\\n[green]✓[/green] Saved suggestions to: {output}")

    except Exception as e:
        console.print(f"\\n[red]✗ Optimization failed: {e}[/red]")
        raise

