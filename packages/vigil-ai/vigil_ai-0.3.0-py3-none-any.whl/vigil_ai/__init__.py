"""Vigil AI - AI-powered workflow generation and optimization.

This package provides AI assistance for Vigil workflows using foundation models.

Architecture (Three-Layer):
    Foundation Layer:  Vigil Core (pipelines, artifacts, receipts)
    Application Layer: MCP + Tools + Datasets + Foundation Models ← THIS PACKAGE
    Agents Layer:      AI Assistants (Claude Desktop, etc.)

Features:
- Natural language → Snakemake pipelines
- AI-powered debugging and optimization
- Foundation model abstraction (Claude, ESM, BioGPT, ChemBERTa, etc.)
- Domain-specific model selection (biology, chemistry, materials)
- Response caching
- Configurable settings
- Retry logic for reliability

Models Supported:
    General:   Claude 3.5 Sonnet, Opus, Haiku, Galactica
    Biology:   ESM-2, BioGPT, ProtGPT2
    Chemistry: ChemBERTa, MolFormer
    Materials: MatBERT
"""

from vigil_ai.cache import clear_cache, get_cache_dir
from vigil_ai.config import Config, get_config
from vigil_ai.debugger import ai_debug
from vigil_ai.generator import ai_create, generate_pipeline
from vigil_ai.models import (
    FoundationModel,
    ModelCapability,
    ModelDomain,
    ModelRegistry,
    get_model,
    list_models,
)
from vigil_ai.optimizer import ai_optimize
from vigil_ai.tasks import (
    ErrorDebugger,
    ModelSelector,
    PipelineGenerator,
    WorkflowOptimizer,
)

__version__ = "0.3.0"  # Updated for foundation models support
__all__ = [
    # Generator
    "generate_pipeline",
    "ai_create",
    # Debugger
    "ai_debug",
    # Optimizer
    "ai_optimize",
    # Config
    "Config",
    "get_config",
    # Cache
    "clear_cache",
    "get_cache_dir",
    # Models (Application Layer)
    "FoundationModel",
    "ModelDomain",
    "ModelCapability",
    "ModelRegistry",
    "get_model",
    "list_models",
    # Tasks (High-level interface)
    "PipelineGenerator",
    "ErrorDebugger",
    "WorkflowOptimizer",
    "ModelSelector",
]
