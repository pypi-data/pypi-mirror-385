"""Foundation model abstraction layer for vigil-ai.

This module provides a unified interface for working with different foundation models:
- Language models (Claude, GPT-4, Llama)
- Science models (ESM, BioGPT, ChemBERTa, Galactica)
- Domain-specific models (ProtGPT, MolFormer, MatBERT)

Architecture:
    Foundation Layer:  Vigil Core (pipelines, artifacts, receipts)
    Application Layer: MCP + Tools + Datasets + Foundation Models ← THIS
    Agents Layer:      AI Assistants (Claude Desktop, etc.)

Usage:
    >>> from vigil_ai.models import get_model, ModelRegistry
    >>>
    >>> # Get default model
    >>> model = get_model()
    >>> response = model.generate("Explain protein folding")
    >>>
    >>> # Get domain-specific model
    >>> bio_model = get_model(domain="biology")
    >>> protein_analysis = bio_model.generate("Analyze this protein sequence: MKFLKF...")
    >>>
    >>> # Use specific model
    >>> esm = get_model(name="esm-2-650m")
    >>> embeddings = esm.embed("PROTEIN_SEQUENCE")
"""

from vigil_ai.models.base import FoundationModel, ModelCapability, ModelDomain
from vigil_ai.models.registry import ModelRegistry, get_model, list_models, register_model

# Auto-register all models
import vigil_ai.models._registry_init  # noqa: F401

__all__ = [
    # Base classes
    "FoundationModel",
    "ModelCapability",
    "ModelDomain",
    # Registry
    "ModelRegistry",
    "get_model",
    "list_models",
    "register_model",
]
