"""Base classes for foundation models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModelDomain(str, Enum):
    """Scientific domains for model specialization."""

    GENERAL = "general"  # General purpose (Claude, GPT-4, etc.)
    BIOLOGY = "biology"  # Protein, DNA, genomics (ESM, BioGPT)
    CHEMISTRY = "chemistry"  # Molecules, reactions (ChemBERTa, MolFormer)
    MATERIALS = "materials"  # Materials science (MatBERT, CrystaLLM)
    PHYSICS = "physics"  # Physics simulations
    ASTRONOMY = "astronomy"  # Astronomy, astrophysics
    CLIMATE = "climate"  # Climate modeling
    MEDICAL = "medical"  # Medical/clinical (BioMedBERT, PubMedGPT)


class ModelCapability(str, Enum):
    """Capabilities that models can provide."""

    TEXT_GENERATION = "text_generation"  # Generate text from prompts
    EMBEDDING = "embedding"  # Generate embeddings for sequences
    CLASSIFICATION = "classification"  # Classify sequences/structures
    PREDICTION = "prediction"  # Predict properties
    TRANSLATION = "translation"  # Translate between representations
    SEARCH = "search"  # Semantic search
    CHAT = "chat"  # Multi-turn conversation


@dataclass
class ModelMetadata:
    """Metadata about a foundation model."""

    name: str
    display_name: str
    domain: ModelDomain
    capabilities: list[ModelCapability]
    description: str
    max_tokens: int | None = None
    context_window: int | None = None
    requires_gpu: bool = False
    requires_api_key: bool = False
    parameters: int | None = None  # Number of parameters (e.g., 650M, 7B)
    license: str | None = None
    citation: str | None = None
    url: str | None = None


class FoundationModel(ABC):
    """Abstract base class for all foundation models.

    All models (Claude, ESM, BioGPT, etc.) must implement this interface.
    This enables the Application Layer to work with any model uniformly.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the model with configuration."""
        self.config = kwargs

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt/query
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Model-specific parameters

        Returns:
            Generated text

        Examples:
            >>> model = get_model()
            >>> result = model.generate("Explain protein folding")
            >>> print(result)
        """
        pass

    @abstractmethod
    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings for text/sequence.

        Args:
            text: Text or sequence to embed
            **kwargs: Model-specific parameters

        Returns:
            Embedding vector

        Examples:
            >>> model = get_model(name="esm-2-650m")
            >>> embedding = model.embed("MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLL")
            >>> len(embedding)
            1280
        """
        pass

    @abstractmethod
    def classify(
        self,
        text: str,
        labels: list[str],
        **kwargs: Any,
    ) -> dict[str, float]:
        """Classify text into categories.

        Args:
            text: Text to classify
            labels: Possible labels
            **kwargs: Model-specific parameters

        Returns:
            Dict mapping labels to probabilities

        Examples:
            >>> model = get_model(domain="biology")
            >>> probs = model.classify(
            ...     "MKFLKF...",
            ...     ["membrane_protein", "cytoplasmic_protein"]
            ... )
        """
        pass

    @abstractmethod
    def get_metadata(self) -> ModelMetadata:
        """Get model metadata.

        Returns:
            Model metadata
        """
        pass

    def supports(self, capability: ModelCapability) -> bool:
        """Check if model supports a capability.

        Args:
            capability: Capability to check

        Returns:
            True if supported
        """
        metadata = self.get_metadata()
        return capability in metadata.capabilities

    def __repr__(self) -> str:
        """String representation."""
        metadata = self.get_metadata()
        return f"{self.__class__.__name__}(name={metadata.name}, domain={metadata.domain})"
