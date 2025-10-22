"""Anthropic (Claude) model implementation."""

from __future__ import annotations

import os
from typing import Any

from vigil_ai.models.base import (
    FoundationModel,
    ModelCapability,
    ModelDomain,
    ModelMetadata,
)


class AnthropicModel(FoundationModel):
    """Anthropic Claude model.

    Supports Claude 3 family models (Opus, Sonnet, Haiku).
    """

    def __init__(self, name: str = "claude-3-5-sonnet-20241022", **kwargs: Any) -> None:
        """Initialize Anthropic model.

        Args:
            name: Model name (e.g., "claude-3-5-sonnet-20241022")
            **kwargs: Additional configuration

        Raises:
            ImportError: If anthropic package not installed
            ValueError: If ANTHROPIC_API_KEY not set
        """
        super().__init__(name=name, **kwargs)

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            )

        api_key = kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your API key from: https://console.anthropic.com/"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = name

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate text using Claude.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens (default: 4096)
            temperature: Sampling temperature (default: 0.7)
            **kwargs: Additional parameters (system, etc.)

        Returns:
            Generated text
        """
        max_tokens = max_tokens or 4096

        system = kwargs.pop("system", None)

        message_kwargs: dict[str, Any] = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        if system:
            message_kwargs["system"] = system

        message_kwargs.update(kwargs)

        response = self.client.messages.create(**message_kwargs)

        return response.content[0].text

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings (not supported by Claude).

        Args:
            text: Text to embed
            **kwargs: Additional parameters

        Raises:
            NotImplementedError: Claude doesn't support embeddings

        Note:
            Use a different model for embeddings (e.g., text-embedding-ada-002)
        """
        raise NotImplementedError(
            "Claude models do not support embeddings. "
            "Use OpenAI's text-embedding models or sentence-transformers."
        )

    def classify(
        self,
        text: str,
        labels: list[str],
        **kwargs: Any,
    ) -> dict[str, float]:
        """Classify text using Claude.

        Args:
            text: Text to classify
            labels: Possible labels
            **kwargs: Additional parameters

        Returns:
            Dict mapping labels to probabilities
        """
        # Use Claude to classify by asking it to choose
        prompt = f"""Classify the following text into one of these categories: {', '.join(labels)}

Text: {text}

Respond with ONLY the category name, nothing else."""

        response = self.generate(prompt, temperature=0.0, **kwargs)
        chosen_label = response.strip()

        # Return uniform probabilities with chosen label highest
        probs = {label: 0.1 for label in labels}
        if chosen_label in labels:
            probs[chosen_label] = 0.9

        return probs

    def get_metadata(self) -> ModelMetadata:
        """Get model metadata.

        Returns:
            Model metadata
        """
        # Map model names to metadata
        metadata_map = {
            "claude-3-5-sonnet-20241022": ModelMetadata(
                name="claude-3-5-sonnet-20241022",
                display_name="Claude 3.5 Sonnet",
                domain=ModelDomain.GENERAL,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.CLASSIFICATION,
                ],
                description="Most intelligent Claude model, excellent for complex reasoning",
                max_tokens=8192,
                context_window=200000,
                requires_gpu=False,
                requires_api_key=True,
                license="Proprietary",
                url="https://www.anthropic.com/claude",
            ),
            "claude-3-opus-20240229": ModelMetadata(
                name="claude-3-opus-20240229",
                display_name="Claude 3 Opus",
                domain=ModelDomain.GENERAL,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.CLASSIFICATION,
                ],
                description="Most capable Claude 3 model for highly complex tasks",
                max_tokens=4096,
                context_window=200000,
                requires_gpu=False,
                requires_api_key=True,
                license="Proprietary",
                url="https://www.anthropic.com/claude",
            ),
            "claude-3-haiku-20240307": ModelMetadata(
                name="claude-3-haiku-20240307",
                display_name="Claude 3 Haiku",
                domain=ModelDomain.GENERAL,
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT,
                    ModelCapability.CLASSIFICATION,
                ],
                description="Fastest Claude model for simple tasks",
                max_tokens=4096,
                context_window=200000,
                requires_gpu=False,
                requires_api_key=True,
                license="Proprietary",
                url="https://www.anthropic.com/claude",
            ),
        }

        # Return metadata for this model, or default
        return metadata_map.get(
            self.model_name,
            ModelMetadata(
                name=self.model_name,
                display_name=self.model_name,
                domain=ModelDomain.GENERAL,
                capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
                description="Anthropic Claude model",
                requires_api_key=True,
            ),
        )
