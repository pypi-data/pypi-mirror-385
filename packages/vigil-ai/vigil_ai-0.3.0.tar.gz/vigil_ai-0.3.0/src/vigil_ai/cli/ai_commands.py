"""AI commands for Vigil - moved from vigil-core."""

from __future__ import annotations

import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def ai_apply(
    skip_promote: bool = typer.Option(False, help="Skip promotion after executing targets."),
) -> None:
    """Execute the targets recorded during propose and optionally promote outputs."""
    cmd = ["uv", "run", "python", "-m", "app.code.ai.auto_target", "apply"]
    if skip_promote:
        cmd.append("--skip-promote")
    console.print(f"[cyan]Running: {' '.join(cmd)}[/cyan]")
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


def ai_create(
    description: str = typer.Argument(..., help="Natural language description of your analysis"),
    output: Path = typer.Option(
        Path("app/code/pipelines/Snakefile"),
        "--output",
        "-o",
        help="Output file path for generated pipeline",
    ),
    template: str = typer.Option(
        "genomics-starter",
        "--template",
        "-t",
        help="Base template to use",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Print pipeline without saving",
    ),
) -> None:
    """Generate a Vigil pipeline from natural language description using AI.

    Examples:
        vigil ai create "Filter variants by quality >30, calculate Ti/Tv ratio"
        vigil ai create "Segment cells, count, measure intensity" -t imaging-starter
    """
    try:
        from vigil_ai import ai_create as ai_create_impl

        ai_create_impl(description, output, template, dry_run=dry_run)

    except ImportError:
        console.print(
            "[red]❌ vigil-ai package not installed. Install with: pip install 'vigil[ai]' or pip install vigil-ai[/red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]❌ Failed to create pipeline: {e}[/red]")
        raise typer.Exit(code=1)


def ai_list_models() -> None:
    """List available AI models for scientific tasks.

    Examples:
        vigil ai list-models
    """
    try:
        from vigil_ai.tasks import ModelSelector

        selector = ModelSelector()
        models = selector.list_models()

        # Create table of models
        table_data = []
        for model in models:
            metadata = model.get_metadata()
            table_data.append([
                metadata.name,
                metadata.domain,
                ', '.join(str(c) for c in metadata.capabilities),
                "Yes" if metadata.requires_gpu else "No",
                "Yes" if metadata.requires_api_key else "No"
            ])

        console.print("\n[bold cyan]Available AI Models:[/bold cyan]")
        console.print("[dim]Use 'vigil ai model-info <name>' for detailed information[/dim]\n")

        for row in table_data:
            console.print(f"[bold]{row[0]}[/bold]")
            console.print(f"  Domain: {row[1]}")
            console.print(f"  Capabilities: {row[2]}")
            console.print(f"  GPU Required: {row[3]}")
            console.print(f"  API Key Required: {row[4]}")
            console.print()

    except ImportError:
        console.print(
            "[red]❌ vigil-ai package not installed. Install with: pip install 'vigil[ai]' or pip install vigil-ai[/red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]❌ Failed to list models: {e}[/red]")
        raise typer.Exit(code=1)


def ai_model_info(
    name: str = typer.Argument(..., help="Model name to get information about"),
) -> None:
    """Get detailed information about a specific model.

    Examples:
        vigil ai model-info esm-2-650m
        vigil ai model-info claude-3-5-sonnet-20241022
    """
    try:
        from vigil_ai.tasks import ModelSelector

        selector = ModelSelector()
        info = selector.get_info(name)

        # Create detailed panel
        panel_content = (
            f"[bold cyan]{info['display_name']}[/bold cyan]\n\n"
            f"[bold]Domain:[/bold] {info['domain']}\n"
            f"[bold]Capabilities:[/bold] {', '.join(info['capabilities'])}\n\n"
            f"[dim]{info['description']}[/dim]\n\n"
        )

        if info['parameters']:
            panel_content += f"[bold]Parameters:[/bold] {info['parameters']:,}\n"
        if info['requires_gpu']:
            panel_content += "[bold]GPU:[/bold] Required\n"
        if info['requires_api_key']:
            panel_content += "[bold]API Key:[/bold] Required (ANTHROPIC_API_KEY)\n"
        if info['license']:
            panel_content += f"[bold]License:[/bold] {info['license']}\n"
        if info['url']:
            panel_content += f"\n[dim]URL: {info['url']}[/dim]"

        panel = Panel(
            panel_content,
            title=f"Model: {name}",
            border_style="cyan",
        )
        console.print(panel)

    except ImportError:
        console.print(
            "[red]❌ vigil-ai package not installed. Install with: pip install 'vigil[ai]' or pip install vigil-ai[/red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]❌ Failed to get model info: {e}[/red]")
        raise typer.Exit(code=1)


def ai_recommend(
    task: str = typer.Argument(..., help="Description of your task"),
) -> None:
    """Get a model recommendation based on your task description.

    Examples:
        vigil ai recommend "analyze protein sequences"
        vigil ai recommend "screen drug compounds"
        vigil ai recommend "predict crystal properties"
    """
    try:
        from vigil_ai.tasks import ModelSelector

        selector = ModelSelector()
        model, reasoning = selector.recommend(task)

        # Get model info
        metadata = model.get_metadata()

        panel = Panel(
            f"[bold green]Recommended Model[/bold green]\n\n"
            f"[bold cyan]{metadata.display_name}[/bold cyan]\n\n"
            f"[bold]Reasoning:[/bold] {reasoning}\n\n"
            f"[bold]Domain:[/bold] {metadata.domain}\n"
            f"[bold]Capabilities:[/bold] {', '.join(str(c) for c in metadata.capabilities)}\n\n"
            f"[dim]{metadata.description}[/dim]",
            title="AI Recommendation",
            border_style="green",
        )
        console.print(panel)

        # Usage example
        console.print("\n[bold]Usage:[/bold]")
        console.print(f"  from vigil_ai import get_model")
        console.print(f"  model = get_model(name='{metadata.name}')")
        console.print(f"  # or")
        console.print(f"  model = get_model(domain=ModelDomain.{metadata.domain.upper()})")

    except ImportError:
        console.print(
            "[red]❌ vigil-ai package not installed. Install with: pip install 'vigil[ai]' or pip install vigil-ai[/red]"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]❌ Failed to get recommendation: {e}[/red]")
        raise typer.Exit(code=1)
