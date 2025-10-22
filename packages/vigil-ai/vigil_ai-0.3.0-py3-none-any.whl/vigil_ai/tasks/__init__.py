"""Task-based interface for common AI workflows.

This module provides high-level task abstractions that make it easy to use
vigil-ai for common scientific workflow tasks without needing to understand
the underlying model details.

Examples:
    >>> from vigil_ai.tasks import PipelineGenerator, ErrorDebugger
    >>>
    >>> # Generate a pipeline
    >>> generator = PipelineGenerator(domain="biology")
    >>> pipeline = generator.create("Filter variants by quality >30")
    >>>
    >>> # Debug an error
    >>> debugger = ErrorDebugger()
    >>> fix = debugger.analyze(error_message="FileNotFoundError: variants.csv")
"""

from vigil_ai.tasks.debugger import ErrorDebugger
from vigil_ai.tasks.generator import PipelineGenerator
from vigil_ai.tasks.optimizer import WorkflowOptimizer
from vigil_ai.tasks.selector import ModelSelector

__all__ = [
    "PipelineGenerator",
    "ErrorDebugger",
    "WorkflowOptimizer",
    "ModelSelector",
]
