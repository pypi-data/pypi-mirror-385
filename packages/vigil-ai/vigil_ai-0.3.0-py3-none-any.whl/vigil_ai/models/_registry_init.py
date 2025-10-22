"""Auto-registration of all foundation models.

This module is imported automatically and registers all available models
into the ModelRegistry.
"""

from vigil_ai.models.anthropic import AnthropicModel
from vigil_ai.models.base import ModelDomain
from vigil_ai.models.huggingface import HuggingFaceModel
from vigil_ai.models.registry import ModelRegistry


def _register_all_models() -> None:
    """Register all available foundation models."""

    # ═══════════════════════════════════════════════════════════
    # GENERAL PURPOSE MODELS
    # ═══════════════════════════════════════════════════════════

    # Claude models (Anthropic)
    ModelRegistry.register(
        "claude-3-5-sonnet-20241022",
        AnthropicModel,
        domain=ModelDomain.GENERAL,
        is_default=True,  # Global default
        is_domain_default=True,  # Default for general domain
    )

    ModelRegistry.register(
        "claude-3-opus-20240229",
        AnthropicModel,
        domain=ModelDomain.GENERAL,
    )

    ModelRegistry.register(
        "claude-3-haiku-20240307",
        AnthropicModel,
        domain=ModelDomain.GENERAL,
    )

    # ═══════════════════════════════════════════════════════════
    # BIOLOGY MODELS
    # ═══════════════════════════════════════════════════════════

    # ESM-2 (Protein language models from Meta AI)
    ModelRegistry.register(
        "esm-2-650m",
        HuggingFaceModel,
        domain=ModelDomain.BIOLOGY,
        is_domain_default=True,  # Default for biology
    )

    ModelRegistry.register(
        "esm-2-3b",
        HuggingFaceModel,
        domain=ModelDomain.BIOLOGY,
    )

    # BioGPT (Biomedical text generation)
    ModelRegistry.register(
        "biogpt",
        HuggingFaceModel,
        domain=ModelDomain.BIOLOGY,
    )

    # ProtGPT2 (Protein sequence generation)
    ModelRegistry.register(
        "protgpt2",
        HuggingFaceModel,
        domain=ModelDomain.BIOLOGY,
    )

    # ═══════════════════════════════════════════════════════════
    # CHEMISTRY MODELS
    # ═══════════════════════════════════════════════════════════

    # ChemBERTa (Chemical language model)
    ModelRegistry.register(
        "chemberta-v2",
        HuggingFaceModel,
        domain=ModelDomain.CHEMISTRY,
        is_domain_default=True,  # Default for chemistry
    )

    # MolFormer (Molecular property prediction)
    ModelRegistry.register(
        "molformer",
        HuggingFaceModel,
        domain=ModelDomain.CHEMISTRY,
    )

    # ═══════════════════════════════════════════════════════════
    # MATERIALS SCIENCE MODELS
    # ═══════════════════════════════════════════════════════════

    # MatBERT (Materials science language model)
    ModelRegistry.register(
        "matbert",
        HuggingFaceModel,
        domain=ModelDomain.MATERIALS,
        is_domain_default=True,  # Default for materials
    )

    # ═══════════════════════════════════════════════════════════
    # GENERAL SCIENCE MODELS
    # ═══════════════════════════════════════════════════════════

    # Galactica (Scientific corpus LLM)
    ModelRegistry.register(
        "galactica-1.3b",
        HuggingFaceModel,
        domain=ModelDomain.GENERAL,
    )

    ModelRegistry.register(
        "galactica-6.7b",
        HuggingFaceModel,
        domain=ModelDomain.GENERAL,
    )


# Auto-register on import
_register_all_models()
