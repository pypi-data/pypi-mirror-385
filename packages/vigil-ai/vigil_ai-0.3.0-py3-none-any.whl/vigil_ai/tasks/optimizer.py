"""High-level workflow optimization task interface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vigil_ai.optimizer import ai_optimize


class WorkflowOptimizer:
    """High-level interface for optimizing scientific workflows.

    This class provides a simple API for getting AI-powered optimization
    suggestions for Vigil workflows.

    Args:
        model: Specific model to use (default: Claude)

    Examples:
        >>> optimizer = WorkflowOptimizer()
        >>> suggestions = optimizer.analyze("workflow.smk")
        >>> print(suggestions)
        >>>
        >>> # Focus on specific aspect
        >>> suggestions = optimizer.analyze("workflow.smk", focus="speed")
        >>>
        >>> # Optimize current workflow
        >>> optimizer.optimize_current(focus="memory")
    """

    def __init__(self, model: str | None = None) -> None:
        """Initialize workflow optimizer.

        Args:
            model: Specific model to use
        """
        self.model = model

    def analyze(
        self,
        snakefile: str | Path = "app/code/pipelines/Snakefile",
        focus: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Analyze a workflow and get optimization suggestions.

        Args:
            snakefile: Path to Snakefile
            focus: Optimization focus (speed, memory, cost, readability)
            **kwargs: Additional parameters

        Returns:
            Optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.analyze(
            ...     "workflow.smk",
            ...     focus="speed"
            ... )
        """
        result = ai_optimize(
            snakefile=Path(snakefile),
            focus=focus,
        )

        return result.get("optimization_suggestions", "No suggestions available")

    def optimize_current(self, focus: str | None = None, **kwargs: Any) -> str:
        """Optimize the current project's workflow.

        Args:
            focus: Optimization focus
            **kwargs: Additional parameters

        Returns:
            Optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.optimize_current(focus="memory")
        """
        return self.analyze(
            snakefile="app/code/pipelines/Snakefile",
            focus=focus,
            **kwargs,
        )

    def optimize_for_speed(
        self,
        snakefile: str | Path = "app/code/pipelines/Snakefile",
        **kwargs: Any,
    ) -> str:
        """Get speed optimization suggestions.

        Args:
            snakefile: Path to Snakefile
            **kwargs: Additional parameters

        Returns:
            Speed optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.optimize_for_speed("workflow.smk")
        """
        return self.analyze(snakefile, focus="speed", **kwargs)

    def optimize_for_memory(
        self,
        snakefile: str | Path = "app/code/pipelines/Snakefile",
        **kwargs: Any,
    ) -> str:
        """Get memory optimization suggestions.

        Args:
            snakefile: Path to Snakefile
            **kwargs: Additional parameters

        Returns:
            Memory optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.optimize_for_memory("workflow.smk")
        """
        return self.analyze(snakefile, focus="memory", **kwargs)

    def optimize_for_cost(
        self,
        snakefile: str | Path = "app/code/pipelines/Snakefile",
        **kwargs: Any,
    ) -> str:
        """Get cost optimization suggestions.

        Args:
            snakefile: Path to Snakefile
            **kwargs: Additional parameters

        Returns:
            Cost optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.optimize_for_cost("workflow.smk")
        """
        return self.analyze(snakefile, focus="cost", **kwargs)

    def optimize_for_readability(
        self,
        snakefile: str | Path = "app/code/pipelines/Snakefile",
        **kwargs: Any,
    ) -> str:
        """Get readability optimization suggestions.

        Args:
            snakefile: Path to Snakefile
            **kwargs: Additional parameters

        Returns:
            Readability optimization suggestions

        Examples:
            >>> optimizer = WorkflowOptimizer()
            >>> suggestions = optimizer.optimize_for_readability("workflow.smk")
        """
        return self.analyze(snakefile, focus="readability", **kwargs)

    def __repr__(self) -> str:
        """String representation."""
        model_info = self.model or "default"
        return f"WorkflowOptimizer(model={model_info})"
