"""Configuration management for vigil-ai."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


DEFAULT_CONFIG = {
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 4096,
    "temperature": 0.7,
    "cache_responses": True,
    "cache_dir": ".vigil-ai-cache",
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "timeout": 60.0,
}


class Config:
    """Configuration manager for vigil-ai.

    Loads configuration from multiple sources in order of precedence:
    1. Environment variables (VIGIL_AI_*)
    2. .vigil-ai.yaml in current directory
    3. ~/.vigil-ai.yaml in home directory
    4. Default values

    Examples:
        >>> config = Config.load()
        >>> print(config.model)
        claude-3-5-sonnet-20241022

        >>> config.cache_responses = False
        >>> config.save()
    """

    def __init__(self, data: dict[str, Any] | None = None):
        """Initialize configuration.

        Args:
            data: Configuration dictionary (defaults to DEFAULT_CONFIG)
        """
        self._data = {**DEFAULT_CONFIG, **(data or {})}

    def __getattr__(self, name: str) -> Any:
        """Get configuration value."""
        if name.startswith("_"):
            return object.__getattribute__(self, name)
        return self._data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set configuration value."""
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value

    @classmethod
    def load(cls) -> Config:
        """Load configuration from all sources.

        Returns:
            Config instance with merged configuration

        Examples:
            >>> config = Config.load()
            >>> print(config.model)
        """
        # Start with defaults
        config_data = DEFAULT_CONFIG.copy()

        # Load from home directory
        home_config = Path.home() / ".vigil-ai.yaml"
        if home_config.exists():
            config_data.update(cls._load_yaml(home_config))

        # Load from current directory
        local_config = Path(".vigil-ai.yaml")
        if local_config.exists():
            config_data.update(cls._load_yaml(local_config))

        # Load from environment variables
        config_data.update(cls._load_env())

        return cls(config_data)

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        """Load YAML configuration file."""
        if yaml is None:
            return {}

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
                # Handle nested 'ai' key
                return data.get("ai", data)
        except Exception:
            return {}

    @staticmethod
    def _load_env() -> dict[str, Any]:
        """Load configuration from environment variables.

        Environment variables are prefixed with VIGIL_AI_
        e.g., VIGIL_AI_MODEL, VIGIL_AI_MAX_TOKENS
        """
        env_config = {}

        for key in DEFAULT_CONFIG:
            env_key = f"VIGIL_AI_{key.upper()}"
            value = os.environ.get(env_key)

            if value is not None:
                # Convert types
                if key in ("max_tokens", "retry_attempts"):
                    env_config[key] = int(value)
                elif key in ("temperature", "retry_delay", "timeout"):
                    env_config[key] = float(value)
                elif key == "cache_responses":
                    env_config[key] = value.lower() in ("true", "1", "yes")
                else:
                    env_config[key] = value

        return env_config

    def save(self, path: Path | None = None) -> None:
        """Save configuration to YAML file.

        Args:
            path: Path to save config (default: .vigil-ai.yaml)

        Examples:
            >>> config = Config.load()
            >>> config.model = "claude-3-opus-20240229"
            >>> config.save()
        """
        if yaml is None:
            raise ImportError("pyyaml required to save configuration")

        if path is None:
            path = Path(".vigil-ai.yaml")

        with open(path, "w") as f:
            yaml.dump({"ai": self._data}, f, default_flow_style=False)

    def to_dict(self) -> dict[str, Any]:
        """Get configuration as dictionary."""
        return self._data.copy()


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get global configuration instance.

    Returns:
        Config instance

    Examples:
        >>> from vigil_ai.config import get_config
        >>> config = get_config()
        >>> print(config.model)
    """
    global _config
    if _config is None:
        _config = Config.load()
    return _config


def reset_config() -> None:
    """Reset global configuration (useful for testing)."""
    global _config
    _config = None
