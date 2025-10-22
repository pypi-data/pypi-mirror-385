"""Model registry for managing foundation models."""

from __future__ import annotations

from typing import Any, Type

from vigil_ai.models.base import FoundationModel, ModelDomain


class ModelRegistry:
    """Registry for foundation models.

    Manages available models and provides lookup by name or domain.
    """

    _models: dict[str, Type[FoundationModel]] = {}
    _domain_defaults: dict[ModelDomain, str] = {}
    _global_default: str | None = None

    @classmethod
    def register(
        cls,
        name: str,
        model_class: Type[FoundationModel],
        domain: ModelDomain | None = None,
        is_default: bool = False,
        is_domain_default: bool = False,
    ) -> None:
        """Register a model.

        Args:
            name: Model name (e.g., "claude-3-5-sonnet", "esm-2-650m")
            model_class: Model class to register
            domain: Scientific domain (optional)
            is_default: Set as global default model
            is_domain_default: Set as default for this domain

        Examples:
            >>> ModelRegistry.register(
            ...     "claude-3-5-sonnet",
            ...     AnthropicModel,
            ...     domain=ModelDomain.GENERAL,
            ...     is_default=True
            ... )
        """
        cls._models[name] = model_class

        if is_default:
            cls._global_default = name

        if is_domain_default and domain:
            cls._domain_defaults[domain] = name

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> FoundationModel:
        """Get a model by name.

        Args:
            name: Model name
            **kwargs: Model initialization parameters

        Returns:
            Initialized model instance

        Raises:
            KeyError: If model not found

        Examples:
            >>> model = ModelRegistry.get("esm-2-650m")
        """
        if name not in cls._models:
            available = ", ".join(cls._models.keys())
            raise KeyError(
                f"Model '{name}' not found. Available models: {available}"
            )

        model_class = cls._models[name]
        return model_class(name=name, **kwargs)

    @classmethod
    def get_by_domain(cls, domain: ModelDomain, **kwargs: Any) -> FoundationModel:
        """Get the default model for a domain.

        Args:
            domain: Scientific domain
            **kwargs: Model initialization parameters

        Returns:
            Initialized model instance

        Examples:
            >>> model = ModelRegistry.get_by_domain(ModelDomain.BIOLOGY)
        """
        if domain not in cls._domain_defaults:
            raise KeyError(
                f"No default model for domain '{domain}'. "
                f"Available domains: {list(cls._domain_defaults.keys())}"
            )

        model_name = cls._domain_defaults[domain]
        return cls.get(model_name, **kwargs)

    @classmethod
    def get_default(cls, **kwargs: Any) -> FoundationModel:
        """Get the global default model.

        Returns:
            Initialized default model

        Raises:
            RuntimeError: If no default model set
        """
        if not cls._global_default:
            raise RuntimeError("No default model configured")

        return cls.get(cls._global_default, **kwargs)

    @classmethod
    def list_models(cls) -> list[str]:
        """List all registered model names.

        Returns:
            List of model names
        """
        return list(cls._models.keys())

    @classmethod
    def list_domains(cls) -> list[ModelDomain]:
        """List all domains with default models.

        Returns:
            List of domains
        """
        return list(cls._domain_defaults.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered models (for testing)."""
        cls._models.clear()
        cls._domain_defaults.clear()
        cls._global_default = None


# Convenience functions


def register_model(
    name: str,
    model_class: Type[FoundationModel],
    domain: ModelDomain | None = None,
    is_default: bool = False,
    is_domain_default: bool = False,
) -> None:
    """Register a model (convenience function).

    Args:
        name: Model name
        model_class: Model class
        domain: Scientific domain
        is_default: Set as global default
        is_domain_default: Set as domain default
    """
    ModelRegistry.register(name, model_class, domain, is_default, is_domain_default)


def get_model(
    name: str | None = None,
    domain: ModelDomain | None = None,
    **kwargs: Any,
) -> FoundationModel:
    """Get a model by name or domain.

    Args:
        name: Model name (if None, uses domain or default)
        domain: Scientific domain (if name is None)
        **kwargs: Model initialization parameters

    Returns:
        Initialized model

    Examples:
        >>> # Get default model
        >>> model = get_model()
        >>>
        >>> # Get specific model
        >>> claude = get_model(name="claude-3-5-sonnet")
        >>>
        >>> # Get domain-specific model
        >>> bio_model = get_model(domain=ModelDomain.BIOLOGY)
    """
    if name:
        return ModelRegistry.get(name, **kwargs)
    elif domain:
        return ModelRegistry.get_by_domain(domain, **kwargs)
    else:
        return ModelRegistry.get_default(**kwargs)


def list_models() -> list[str]:
    """List all available models.

    Returns:
        List of model names
    """
    return ModelRegistry.list_models()
