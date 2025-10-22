"""High-level debugging task interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vigil_ai.debugger import ai_debug


class ErrorDebugger:
    """High-level interface for debugging workflow errors.

    This class provides a simple API for getting AI-powered debugging
    suggestions for Vigil workflow errors.

    Args:
        model: Specific model to use for debugging (default: Claude)

    Examples:
        >>> debugger = ErrorDebugger()
        >>> fix = debugger.analyze("FileNotFoundError: variants.csv")
        >>> print(fix)
        >>>
        >>> # With context
        >>> fix = debugger.analyze(
        ...     error="Rule failed",
        ...     context={"snakefile": "rule filter: ..."}
        ... )
        >>>
        >>> # From log file
        >>> fix = debugger.analyze_log("error.log")
    """

    def __init__(self, model: str | None = None) -> None:
        """Initialize error debugger.

        Args:
            model: Specific model to use (default: Claude)
        """
        self.model = model

    def analyze(
        self,
        error: str,
        context: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Analyze an error and get debugging suggestions.

        Args:
            error: Error message to analyze
            context: Additional context (files, logs, etc.)
            **kwargs: Additional parameters

        Returns:
            Debugging suggestions

        Examples:
            >>> debugger = ErrorDebugger()
            >>> fix = debugger.analyze(
            ...     "FileNotFoundError: data/variants.csv",
            ...     context={"snakefile": "rule filter: input: 'data/variants.csv'"}
            ... )
        """
        return ai_debug(
            error_message=error,
            context=context,
            model=kwargs.get("model", self.model),
        )

    def analyze_log(
        self,
        log_path: str | Path,
        context: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> str:
        """Analyze error from a log file.

        Args:
            log_path: Path to error log
            context: Additional context
            **kwargs: Additional parameters

        Returns:
            Debugging suggestions

        Examples:
            >>> debugger = ErrorDebugger()
            >>> fix = debugger.analyze_log(".snakemake/log/error.log")
        """
        log_path = Path(log_path)

        if not log_path.exists():
            return f"Error: Log file not found: {log_path}"

        error_content = log_path.read_text()

        return self.analyze(error_content, context=context, **kwargs)

    def analyze_snakemake_error(
        self,
        error: str,
        snakefile: str | Path | None = None,
        **kwargs: Any,
    ) -> str:
        """Analyze a Snakemake-specific error.

        Args:
            error: Error message
            snakefile: Path to Snakefile (for context)
            **kwargs: Additional parameters

        Returns:
            Debugging suggestions

        Examples:
            >>> debugger = ErrorDebugger()
            >>> fix = debugger.analyze_snakemake_error(
            ...     "Rule 'filter' failed",
            ...     snakefile="workflow.smk"
            ... )
        """
        context = {}

        if snakefile:
            snakefile_path = Path(snakefile)
            if snakefile_path.exists():
                # Read first 1000 chars for context
                context["snakefile"] = snakefile_path.read_text()[:1000]

        return self.analyze(error, context=context, **kwargs)

    def quick_fix(self, error: str) -> str:
        """Get a quick fix suggestion (concise).

        Args:
            error: Error message

        Returns:
            Concise fix suggestion

        Examples:
            >>> debugger = ErrorDebugger()
            >>> fix = debugger.quick_fix("FileNotFoundError: data.csv")
        """
        # Use same analysis but could be enhanced to request concise output
        return self.analyze(error)

    def __repr__(self) -> str:
        """String representation."""
        model_info = self.model or "default"
        return f"ErrorDebugger(model={model_info})"
