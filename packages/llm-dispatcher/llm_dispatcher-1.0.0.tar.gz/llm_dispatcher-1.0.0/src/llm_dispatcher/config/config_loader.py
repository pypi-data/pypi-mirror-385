"""
Configuration loader for LLM-Dispatcher.

This module provides functionality to load configuration from various sources
including files, environment variables, and programmatic settings.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging

from .settings import SwitchConfig, ProviderConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and manages configuration for LLM-Dispatcher.

    This class provides methods to load configuration from various sources
    and merge them into a unified configuration object.
    """

    def __init__(self):
        self.config: Optional[SwitchConfig] = None
        self.config_sources: List[str] = []

    def load_config(
        self,
        config_file: Optional[str] = None,
        env_prefix: str = "LLM_DISPATCHER_",
        merge_with_defaults: bool = True,
    ) -> SwitchConfig:
        """
        Load configuration from multiple sources.

        Args:
            config_file: Path to configuration file (JSON or YAML)
            env_prefix: Prefix for environment variables
            merge_with_defaults: Whether to merge with default configuration

        Returns:
            Loaded configuration object
        """
        # Start with defaults if requested
        if merge_with_defaults:
            config_data = DEFAULT_CONFIG.to_dict()
        else:
            config_data = {}

        # Load from file if provided
        if config_file:
            file_data = self._load_from_file(config_file)
            config_data = self._merge_configs(config_data, file_data)
            self.config_sources.append(f"file:{config_file}")

        # Load from environment variables
        env_data = self._load_from_env(env_prefix)
        if env_data:
            config_data = self._merge_configs(config_data, env_data)
            self.config_sources.append("environment")

        # Create configuration object
        try:
            self.config = SwitchConfig(**config_data)
        except Exception as e:
            logger.error(f"Failed to create configuration: {e}")
            raise

        # Validate configuration
        errors = self.config.validate_config()
        if errors:
            logger.warning(f"Configuration validation warnings: {errors}")

        logger.info(f"Configuration loaded from sources: {self.config_sources}")
        return self.config

    def _load_from_file(self, filepath: str) -> Dict[str, Any]:
        """Load configuration from a file."""
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        try:
            with open(filepath, "r") as f:
                if filepath.suffix.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(f) or {}
                elif filepath.suffix.lower() == ".json":
                    return json.load(f) or {}
                else:
                    raise ValueError(
                        f"Unsupported configuration file format: {filepath.suffix}"
                    )
        except Exception as e:
            logger.error(f"Failed to load configuration file {filepath}: {e}")
            raise

    def _load_from_env(self, prefix: str) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config_data = {}

        # Map environment variables to configuration keys
        env_mappings = {
            f"{prefix}DEFAULT_PROVIDER": "default_provider",
            f"{prefix}DEFAULT_MODEL": "default_model",
            f"{prefix}LOG_LEVEL": "log_level",
            f"{prefix}LOG_FILE": "log_file",
            f"{prefix}DATA_DIR": "data_dir",
            f"{prefix}ENABLE_ASYNC": "enable_async",
            f"{prefix}MAX_CONCURRENT_REQUESTS": "max_concurrent_requests",
            f"{prefix}REQUEST_TIMEOUT": "request_timeout",
            f"{prefix}ENABLE_PERSISTENCE": "enable_persistence",
            f"{prefix}OPTIMIZATION_STRATEGY": "switching_rules.optimization_strategy",
            f"{prefix}FALLBACK_STRATEGY": "switching_rules.fallback_strategy",
            f"{prefix}ENABLE_CACHING": "switching_rules.enable_caching",
            f"{prefix}ENABLE_MONITORING": "switching_rules.enable_monitoring",
            f"{prefix}DAILY_BUDGET": "switching_rules.daily_budget",
            f"{prefix}MONTHLY_BUDGET": "switching_rules.monthly_budget",
        }

        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(
                    config_data, config_key, self._parse_env_value(value)
                )

        # Load provider configurations from environment
        self._load_providers_from_env(config_data, prefix)

        return config_data

    def _load_providers_from_env(
        self, config_data: Dict[str, Any], prefix: str
    ) -> None:
        """Load provider configurations from environment variables."""
        providers = {}

        # Common provider names
        provider_names = ["openai", "anthropic", "google", "xai"]

        for provider in provider_names:
            api_key = os.getenv(f"{prefix}{provider.upper()}_API_KEY")
            if api_key:
                provider_config = {
                    "name": provider,
                    "api_key": api_key,
                    "enabled": True,
                }

                # Load additional provider settings
                enabled = os.getenv(f"{prefix}{provider.upper()}_ENABLED")
                if enabled is not None:
                    provider_config["enabled"] = enabled.lower() in ["true", "1", "yes"]

                timeout = os.getenv(f"{prefix}{provider.upper()}_TIMEOUT")
                if timeout is not None:
                    try:
                        provider_config["timeout_seconds"] = int(timeout)
                    except ValueError:
                        logger.warning(
                            f"Invalid timeout value for {provider}: {timeout}"
                        )

                retry_attempts = os.getenv(f"{prefix}{provider.upper()}_RETRY_ATTEMPTS")
                if retry_attempts is not None:
                    try:
                        provider_config["retry_attempts"] = int(retry_attempts)
                    except ValueError:
                        logger.warning(
                            f"Invalid retry attempts value for {provider}: {retry_attempts}"
                        )

                base_url = os.getenv(f"{prefix}{provider.upper()}_BASE_URL")
                if base_url:
                    provider_config["base_url"] = base_url

                providers[provider] = provider_config

        if providers:
            config_data["providers"] = providers

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate type."""
        # Boolean values
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"

        # Numeric values
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # String value
        return value

    def _set_nested_value(self, data: Dict[str, Any], key: str, value: Any) -> None:
        """Set a nested value in a dictionary using dot notation."""
        keys = key.split(".")
        current = data

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def save_config(self, config: SwitchConfig, filepath: str) -> None:
        """Save configuration to a file."""
        filepath = Path(filepath)

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, "w") as f:
                if filepath.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(config.to_dict(), f, default_flow_style=False, indent=2)
                elif filepath.suffix.lower() == ".json":
                    json.dump(config.to_dict(), f, indent=2)
                else:
                    raise ValueError(
                        f"Unsupported configuration file format: {filepath.suffix}"
                    )
        except Exception as e:
            logger.error(f"Failed to save configuration to {filepath}: {e}")
            raise

    def create_default_config_file(self, filepath: str) -> None:
        """Create a default configuration file."""
        self.save_config(DEFAULT_CONFIG, filepath)
        logger.info(f"Default configuration created at: {filepath}")

    def get_config(self) -> Optional[SwitchConfig]:
        """Get the currently loaded configuration."""
        return self.config

    def reload_config(self) -> SwitchConfig:
        """Reload configuration from the same sources."""
        if not self.config_sources:
            raise RuntimeError("No configuration sources available for reload")

        # Clear current configuration
        self.config = None
        sources = self.config_sources.copy()
        self.config_sources.clear()

        # Reload from sources
        config_file = None
        for source in sources:
            if source.startswith("file:"):
                config_file = source[5:]  # Remove "file:" prefix
                break

        return self.load_config(config_file=config_file, merge_with_defaults=True)


# Global configuration loader instance
config_loader = ConfigLoader()


def load_config(
    config_file: Optional[str] = None,
    env_prefix: str = "LLM_DISPATCHER_",
    merge_with_defaults: bool = True,
) -> SwitchConfig:
    """Convenience function to load configuration."""
    return config_loader.load_config(config_file, env_prefix, merge_with_defaults)


def init_config(
    config_file: Optional[str] = None,
    env_prefix: str = "LLM_DISPATCHER_",
    merge_with_defaults: bool = True,
) -> SwitchConfig:
    """Initialize configuration and return it."""
    return config_loader.load_config(config_file, env_prefix, merge_with_defaults)


def get_config() -> Optional[SwitchConfig]:
    """Convenience function to get current configuration."""
    return config_loader.get_config()
