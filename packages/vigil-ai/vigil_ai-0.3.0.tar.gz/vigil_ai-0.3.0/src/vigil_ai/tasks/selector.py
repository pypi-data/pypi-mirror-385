"""High-level model selection helper."""

from __future__ import annotations

from typing import Any

from vigil_ai.models import ModelDomain, get_model, list_models


class ModelSelector:
    """High-level interface for discovering and selecting models.

    This class helps users find the right model for their scientific domain
    and task without needing to know all available models.

    Examples:
        >>> selector = ModelSelector()
        >>>
        >>> # Get recommended model for a domain
        >>> model = selector.for_domain("biology")
        >>>
        >>> # List available models
        >>> models = selector.list_all()
        >>>
        >>> # Get model info
        >>> info = selector.get_info("esm-2-650m")
        >>> print(info)
    """

    def for_domain(
        self,
        domain: str | ModelDomain,
        **kwargs: Any,
    ) -> Any:
        """Get the recommended model for a scientific domain.

        Args:
            domain: Scientific domain (biology, chemistry, materials, general)
            **kwargs: Additional parameters for model initialization

        Returns:
            Initialized model instance

        Examples:
            >>> selector = ModelSelector()
            >>> model = selector.for_domain("biology")  # Returns ESM-2
            >>> embedding = model.embed("MKFLKF...")
        """
        domain_obj = ModelDomain(domain) if isinstance(domain, str) else domain
        return get_model(domain=domain_obj, **kwargs)

    def for_task(self, task: str, domain: str | None = None, **kwargs: Any) -> Any:
        """Get a model suited for a specific task.

        Args:
            task: Task name (embedding, generation, classification, etc.)
            domain: Optional domain filter
            **kwargs: Additional parameters

        Returns:
            Initialized model instance

        Examples:
            >>> selector = ModelSelector()
            >>> model = selector.for_task("embedding", domain="biology")
        """
        # Map tasks to capabilities and select appropriate model
        task_to_domain = {
            "protein-embedding": ModelDomain.BIOLOGY,
            "protein-generation": ModelDomain.BIOLOGY,
            "molecular-property": ModelDomain.CHEMISTRY,
            "materials-prediction": ModelDomain.MATERIALS,
            "scientific-writing": ModelDomain.GENERAL,
        }

        # If task maps to a domain, use that
        if task in task_to_domain:
            return self.for_domain(task_to_domain[task], **kwargs)

        # Otherwise use specified domain or default
        if domain:
            return self.for_domain(domain, **kwargs)

        return get_model(**kwargs)

    def by_name(self, name: str, **kwargs: Any) -> Any:
        """Get a specific model by name.

        Args:
            name: Model name
            **kwargs: Additional parameters

        Returns:
            Initialized model instance

        Examples:
            >>> selector = ModelSelector()
            >>> model = selector.by_name("galactica-6.7b")
        """
        return get_model(name=name, **kwargs)

    def list_all(self) -> list[str]:
        """List all available models.

        Returns:
            List of model names

        Examples:
            >>> selector = ModelSelector()
            >>> models = selector.list_all()
            >>> print(models)
            ['claude-3-5-sonnet-20241022', 'esm-2-650m', ...]
        """
        return list_models()

    def list_by_domain(self, domain: str | ModelDomain) -> list[str]:
        """List models for a specific domain.

        Args:
            domain: Scientific domain

        Returns:
            List of model names for that domain

        Examples:
            >>> selector = ModelSelector()
            >>> bio_models = selector.list_by_domain("biology")
            >>> print(bio_models)
            ['esm-2-650m', 'esm-2-3b', 'biogpt', 'protgpt2']
        """
        domain_obj = ModelDomain(domain) if isinstance(domain, str) else domain

        # Filter models by domain
        # This is a simple implementation - could be enhanced
        domain_keywords = {
            ModelDomain.BIOLOGY: ["esm", "bio", "prot"],
            ModelDomain.CHEMISTRY: ["chem", "mol"],
            ModelDomain.MATERIALS: ["mat"],
            ModelDomain.GENERAL: ["claude", "galactica"],
        }

        keywords = domain_keywords.get(domain_obj, [])
        all_models = self.list_all()

        return [
            model
            for model in all_models
            if any(keyword in model.lower() for keyword in keywords)
        ]

    def get_info(self, name: str) -> dict[str, Any]:
        """Get detailed information about a model.

        Args:
            name: Model name

        Returns:
            Dict with model metadata

        Examples:
            >>> selector = ModelSelector()
            >>> info = selector.get_info("esm-2-650m")
            >>> print(info["description"])
            'Protein language model from Meta AI'
        """
        model = self.by_name(name)
        metadata = model.get_metadata()

        return {
            "name": metadata.name,
            "display_name": metadata.display_name,
            "domain": str(metadata.domain),
            "capabilities": [str(c) for c in metadata.capabilities],
            "description": metadata.description,
            "parameters": metadata.parameters,
            "requires_gpu": metadata.requires_gpu,
            "requires_api_key": metadata.requires_api_key,
            "license": metadata.license,
            "citation": metadata.citation,
            "url": metadata.url,
        }

    def recommend(
        self,
        description: str,
        **kwargs: Any,
    ) -> tuple[Any, str]:
        """Recommend a model based on a task description.

        Args:
            description: Natural language description of the task
            **kwargs: Additional parameters

        Returns:
            Tuple of (model, reasoning)

        Examples:
            >>> selector = ModelSelector()
            >>> model, reason = selector.recommend(
            ...     "I need to analyze protein sequences"
            ... )
            >>> print(reason)
            'Recommended esm-2-650m for protein analysis'
        """
        desc_lower = description.lower()

        # Simple keyword-based recommendation
        # Could be enhanced with an LLM for better matching
        if any(word in desc_lower for word in ["protein", "genome", "dna", "gene"]):
            model = self.for_domain(ModelDomain.BIOLOGY, **kwargs)
            return model, "Recommended biology model (ESM-2) for protein/genomic analysis"

        if any(word in desc_lower for word in ["chemical", "molecule", "drug", "compound"]):
            model = self.for_domain(ModelDomain.CHEMISTRY, **kwargs)
            return model, "Recommended chemistry model (ChemBERTa) for molecular analysis"

        if any(word in desc_lower for word in ["material", "crystal", "alloy"]):
            model = self.for_domain(ModelDomain.MATERIALS, **kwargs)
            return model, "Recommended materials model (MatBERT) for materials science"

        # Default to general-purpose
        model = get_model(**kwargs)
        return model, "Recommended general-purpose model (Claude) for diverse tasks"

    def __repr__(self) -> str:
        """String representation."""
        return f"ModelSelector(available_models={len(self.list_all())})"
