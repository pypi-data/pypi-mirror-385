"""AI-powered debugging assistant for Vigil workflows."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from vigil_ai.cache import cached
from vigil_ai.retry import with_retry

console = Console()


@with_retry
def _call_claude_api(client: Any, model: str, prompt: str, max_tokens: int = 2048) -> str:
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


@cached
def ai_debug(
    error_message: str,
    context: dict[str, str] | None = None,
    model: str = "claude-3-5-sonnet-20241022",
) -> str:
    """Analyze error and suggest fixes using AI.

    Args:
        error_message: The error message from the failed pipeline
        context: Additional context (files, logs, etc.)
        model: Claude model to use

    Returns:
        Suggested fix explanation

    Examples:
        >>> fix = ai_debug("FileNotFoundError: variants.csv not found")
        >>> print(fix)
        The error indicates that the input file 'variants.csv' is missing.

        Suggested fixes:
        1. Check that your data file exists in app/data/samples/
        2. Verify the file name matches exactly (case-sensitive)
        3. Run: ls app/data/samples/ to see available files
        ...
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package required. Install with: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    # Build context
    context_str = ""
    if context:
        context_str = "\\n\\nAdditional context:\\n"
        for key, value in context.items():
            context_str += f"{key}:\\n{value}\\n\\n"

    prompt = f"""You are a Vigil workflow debugging expert. Analyze this error and suggest fixes.

Error message:
{error_message}
{context_str}

Provide:
1. Root cause analysis
2. Step-by-step fix instructions
3. Commands to run (if applicable)
4. How to prevent this in the future

Be concise and actionable."""

    try:
        return _call_claude_api(client, model, prompt, max_tokens=2048)

    except Exception as e:
        console.print(f"[red]Error during debugging: {e}[/red]")
        raise


def ai_debug_command(
    error_log: Path | None = None,
    interactive: bool = False,
) -> None:
    """CLI command for AI-powered debugging.

    Args:
        error_log: Path to error log file
        interactive: If True, enter interactive debugging mode

    Examples:
        >>> ai_debug_command(error_log=Path(".snakemake/log/error.log"))
        Analyzing error...

        Root Cause:
        The rule 'filter_variants' failed because...

        Suggested Fix:
        1. ...
    """
    if error_log and error_log.exists():
        error_content = error_log.read_text()
    elif interactive:
        console.print("[bold]Enter error message (Ctrl+D when done):[/bold]")
        import sys

        error_content = sys.stdin.read()
    else:
        # Try to find latest error
        snakemake_logs = Path(".snakemake/log")
        if snakemake_logs.exists():
            log_files = sorted(snakemake_logs.glob("*.log"), key=lambda p: p.stat().st_mtime)
            if log_files:
                error_content = log_files[-1].read_text()
            else:
                console.print("[red]No error logs found[/red]")
                return
        else:
            console.print("[red]No .snakemake/log directory found[/red]")
            return

    console.print(Panel("[cyan]Analyzing error with Claude...[/cyan]", title="Vigil AI Debug"))

    try:
        # Extract relevant context
        context = {}
        if Path("app/code/pipelines/Snakefile").exists():
            context["Snakefile"] = Path("app/code/pipelines/Snakefile").read_text()[:1000]

        fix_suggestion = ai_debug(error_content, context)

        console.print("\\n[bold green]Suggested Fix:[/bold green]\\n")
        console.print(fix_suggestion)

    except Exception as e:
        console.print(f"\\n[red]✗ Debugging failed: {e}[/red]")
        raise
