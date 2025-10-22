"""HuggingFace model implementation for science foundation models."""

from __future__ import annotations

from typing import Any

from vigil_ai.models.base import (
    FoundationModel,
    ModelCapability,
    ModelDomain,
    ModelMetadata,
)


class HuggingFaceModel(FoundationModel):
    """HuggingFace model for science foundation models.

    Supports:
    - Biology: ESM-2, BioGPT, ProtGPT
    - Chemistry: ChemBERTa, MolFormer
    - Materials: MatBERT
    - General Science: Galactica
    """

    # Model metadata registry
    MODELS = {
        # Biology - Protein models
        "esm-2-650m": ModelMetadata(
            name="esm-2-650m",
            display_name="ESM-2 650M",
            domain=ModelDomain.BIOLOGY,
            capabilities=[ModelCapability.EMBEDDING, ModelCapability.PREDICTION],
            description="Protein language model from Meta AI, 650M parameters",
            parameters=650_000_000,
            requires_gpu=True,
            license="MIT",
            citation="Lin et al. 2022, https://doi.org/10.1101/2022.07.20.500902",
            url="https://huggingface.co/facebook/esm2_t33_650M_UR50D",
        ),
        "esm-2-3b": ModelMetadata(
            name="esm-2-3b",
            display_name="ESM-2 3B",
            domain=ModelDomain.BIOLOGY,
            capabilities=[ModelCapability.EMBEDDING, ModelCapability.PREDICTION],
            description="Protein language model from Meta AI, 3B parameters",
            parameters=3_000_000_000,
            requires_gpu=True,
            license="MIT",
            url="https://huggingface.co/facebook/esm2_t36_3B_UR50D",
        ),
        "biogpt": ModelMetadata(
            name="biogpt",
            display_name="BioGPT",
            domain=ModelDomain.BIOLOGY,
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CHAT],
            description="Biomedical text generation model from Microsoft",
            parameters=347_000_000,
            requires_gpu=True,
            license="MIT",
            citation="Luo et al. 2022",
            url="https://huggingface.co/microsoft/biogpt",
        ),
        "protgpt2": ModelMetadata(
            name="protgpt2",
            display_name="ProtGPT2",
            domain=ModelDomain.BIOLOGY,
            capabilities=[ModelCapability.TEXT_GENERATION],
            description="Protein sequence generation model",
            parameters=738_000_000,
            requires_gpu=True,
            license="BSD-3-Clause",
            url="https://huggingface.co/nferruz/ProtGPT2",
        ),
        # Chemistry models
        "chemberta-v2": ModelMetadata(
            name="chemberta-v2",
            display_name="ChemBERTa v2",
            domain=ModelDomain.CHEMISTRY,
            capabilities=[
                ModelCapability.EMBEDDING,
                ModelCapability.CLASSIFICATION,
                ModelCapability.PREDICTION,
            ],
            description="Chemical language model for molecules (SMILES)",
            parameters=110_000_000,
            requires_gpu=False,
            license="MIT",
            url="https://huggingface.co/seyonec/ChemBERTa-zinc-base-v1",
        ),
        "molformer": ModelMetadata(
            name="molformer",
            display_name="MolFormer",
            domain=ModelDomain.CHEMISTRY,
            capabilities=[ModelCapability.EMBEDDING, ModelCapability.PREDICTION],
            description="Transformer for molecular property prediction",
            parameters=47_000_000,
            requires_gpu=True,
            license="MIT",
            citation="Ross et al. 2022",
            url="https://huggingface.co/ibm/MoLFormer-XL-both-10pct",
        ),
        # Materials science
        "matbert": ModelMetadata(
            name="matbert",
            display_name="MatBERT",
            domain=ModelDomain.MATERIALS,
            capabilities=[
                ModelCapability.EMBEDDING,
                ModelCapability.CLASSIFICATION,
            ],
            description="Materials science language model",
            parameters=110_000_000,
            requires_gpu=False,
            license="Apache-2.0",
            url="https://huggingface.co/m3rg-iitd/MatBERT",
        ),
        # General science
        "galactica-1.3b": ModelMetadata(
            name="galactica-1.3b",
            display_name="Galactica 1.3B",
            domain=ModelDomain.GENERAL,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
            ],
            description="Large language model trained on scientific corpus",
            parameters=1_300_000_000,
            requires_gpu=True,
            license="CC-BY-NC-4.0",
            citation="Taylor et al. 2022, Meta AI",
            url="https://huggingface.co/facebook/galactica-1.3b",
        ),
        "galactica-6.7b": ModelMetadata(
            name="galactica-6.7b",
            display_name="Galactica 6.7B",
            domain=ModelDomain.GENERAL,
            capabilities=[
                ModelCapability.TEXT_GENERATION,
                ModelCapability.CHAT,
            ],
            description="Large language model trained on scientific corpus",
            parameters=6_700_000_000,
            requires_gpu=True,
            license="CC-BY-NC-4.0",
            url="https://huggingface.co/facebook/galactica-6.7b",
        ),
    }

    def __init__(self, name: str, **kwargs: Any) -> None:
        """Initialize HuggingFace model.

        Args:
            name: Model name (e.g., "esm-2-650m", "biogpt")
            **kwargs: Additional configuration (device, etc.)

        Raises:
            ImportError: If transformers not installed
            KeyError: If model not supported
        """
        super().__init__(name=name, **kwargs)

        if name not in self.MODELS:
            available = ", ".join(self.MODELS.keys())
            raise KeyError(
                f"Model '{name}' not supported. Available models: {available}"
            )

        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError:
            raise ImportError(
                "transformers and torch required. "
                "Install with: pip install 'vigil-ai[science]'"
            )

        self.model_name = name
        self.device = kwargs.get("device", "cuda" if torch.cuda.is_available() else "cpu")

        # Load model and tokenizer lazily
        self._model = None
        self._tokenizer = None
        self._torch = torch
        self._AutoModel = AutoModel
        self._AutoTokenizer = AutoTokenizer

    def _load_model(self) -> None:
        """Lazy load model and tokenizer."""
        if self._model is not None:
            return

        # Map model names to HuggingFace model IDs
        model_id_map = {
            "esm-2-650m": "facebook/esm2_t33_650M_UR50D",
            "esm-2-3b": "facebook/esm2_t36_3B_UR50D",
            "biogpt": "microsoft/biogpt",
            "protgpt2": "nferruz/ProtGPT2",
            "chemberta-v2": "seyonec/ChemBERTa-zinc-base-v1",
            "molformer": "ibm/MoLFormer-XL-both-10pct",
            "matbert": "m3rg-iitd/MatBERT",
            "galactica-1.3b": "facebook/galactica-1.3b",
            "galactica-6.7b": "facebook/galactica-6.7b",
        }

        model_id = model_id_map[self.model_name]

        self._tokenizer = self._AutoTokenizer.from_pretrained(model_id)
        self._model = self._AutoModel.from_pretrained(model_id).to(self.device)

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate text using the model.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Generated text

        Note:
            Only works for generative models (BioGPT, ProtGPT2, Galactica)
        """
        metadata = self.get_metadata()
        if ModelCapability.TEXT_GENERATION not in metadata.capabilities:
            raise NotImplementedError(
                f"{self.model_name} does not support text generation. "
                f"Use generate() with: biogpt, protgpt2, galactica-*"
            )

        self._load_model()

        # Tokenize
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate
        max_length = (max_tokens or 100) + inputs["input_ids"].shape[1]
        outputs = self._model.generate(
            **inputs,
            max_length=max_length,
            temperature=temperature,
            do_sample=temperature > 0,
            **kwargs,
        )

        # Decode
        generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Remove prompt from output
        if generated_text.startswith(prompt):
            generated_text = generated_text[len(prompt) :].strip()

        return generated_text

    def embed(self, text: str, **kwargs: Any) -> list[float]:
        """Generate embeddings for text/sequence.

        Args:
            text: Text or sequence to embed
            **kwargs: Additional parameters

        Returns:
            Embedding vector

        Examples:
            >>> model = get_model(name="esm-2-650m")
            >>> embedding = model.embed("MKFLKFSLLTAVLLSVVFAFSSCGDDDDTGYLPPSQAIQDLL")
        """
        metadata = self.get_metadata()
        if ModelCapability.EMBEDDING not in metadata.capabilities:
            raise NotImplementedError(
                f"{self.model_name} does not support embeddings"
            )

        self._load_model()

        # Tokenize
        inputs = self._tokenizer(text, return_tensors="pt").to(self.device)

        # Get embeddings
        with self._torch.no_grad():
            outputs = self._model(**inputs)

        # Use mean pooling over sequence length
        embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings[0].cpu().tolist()

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
            **kwargs: Additional parameters

        Returns:
            Dict mapping labels to probabilities

        Note:
            Uses zero-shot classification via embeddings
        """
        metadata = self.get_metadata()
        if ModelCapability.CLASSIFICATION not in metadata.capabilities:
            raise NotImplementedError(
                f"{self.model_name} does not support classification"
            )

        # For now, use simple embedding similarity
        # TODO: Implement proper zero-shot classification
        text_embedding = self.embed(text)

        # Uniform probabilities as placeholder
        probs = {label: 1.0 / len(labels) for label in labels}

        return probs

    def get_metadata(self) -> ModelMetadata:
        """Get model metadata.

        Returns:
            Model metadata
        """
        return self.MODELS[self.model_name]
