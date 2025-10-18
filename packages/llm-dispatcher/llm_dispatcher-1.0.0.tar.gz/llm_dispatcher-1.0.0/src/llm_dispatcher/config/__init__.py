"""
Configuration management for LLM-Dispatcher.

This module provides configuration management functionality including
settings, provider configurations, and switching rules.
"""

from .settings import (
    SwitchConfig,
    ProviderConfig,
    SwitchingRules,
    OptimizationStrategy,
    FallbackStrategy,
)
from .config_loader import ConfigLoader

__all__ = [
    "SwitchConfig",
    "ProviderConfig",
    "SwitchingRules",
    "OptimizationStrategy",
    "FallbackStrategy",
    "ConfigLoader",
]
