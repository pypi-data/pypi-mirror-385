"""
Configuration settings for LLM-Dispatcher.

This module defines the configuration data structures and default settings
for the LLM-Dispatcher package.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import os
from pathlib import Path


class OptimizationStrategy(str, Enum):
    """Optimization strategies for LLM selection."""

    PERFORMANCE = "performance"  # Prioritize best performance
    COST = "cost"  # Prioritize cost efficiency
    SPEED = "speed"  # Prioritize fastest response
    BALANCED = "balanced"  # Balance all factors
    RELIABILITY = "reliability"  # Prioritize reliability


class FallbackStrategy(str, Enum):
    """Fallback strategies when primary LLM fails."""

    PERFORMANCE_PRIORITY = "performance_priority"
    COST_PRIORITY = "cost_priority"
    SPEED_PRIORITY = "speed_priority"
    RELIABILITY_PRIORITY = "reliability_priority"


class ProviderConfig(BaseModel):
    """Configuration for a specific LLM provider."""

    name: str
    api_key: str
    enabled: bool = True
    models: List[str] = Field(default_factory=list)
    max_requests_per_minute: Optional[int] = None
    max_requests_per_day: Optional[int] = None
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    custom_headers: Dict[str, str] = Field(default_factory=dict)
    base_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SwitchingRules(BaseModel):
    """Rules for intelligent LLM switching."""

    # Task-specific routing
    task_routing: Dict[str, List[str]] = Field(default_factory=dict)

    # Optimization preferences
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED

    # Performance thresholds
    min_performance_score: float = 0.5
    max_latency_ms: Optional[int] = None
    max_cost_per_request: Optional[float] = None

    # Fallback configuration
    fallback_strategy: FallbackStrategy = FallbackStrategy.PERFORMANCE_PRIORITY
    max_fallback_attempts: int = 3
    fallback_enabled: bool = True

    # Caching configuration
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    max_cache_size: int = 1000

    # Monitoring configuration
    enable_monitoring: bool = True
    performance_window_hours: int = 24
    alert_thresholds: Dict[str, float] = Field(default_factory=dict)

    # Budget limits
    daily_budget: Optional[float] = None
    monthly_budget: Optional[float] = None
    budget_alert_threshold: float = 0.8  # Alert at 80% of budget

    @field_validator("task_routing")
    @classmethod
    def validate_task_routing(cls, v):
        """Validate task routing configuration."""
        valid_tasks = [
            "text_generation",
            "code_generation",
            "translation",
            "summarization",
            "question_answering",
            "classification",
            "sentiment_analysis",
            "vision_analysis",
            "audio_transcription",
            "structured_output",
            "function_calling",
            "reasoning",
            "math",
        ]

        for task, providers in v.items():
            if task not in valid_tasks:
                raise ValueError(f"Invalid task type: {task}")
            if not isinstance(providers, list):
                raise ValueError(f"Task routing providers must be a list: {task}")

        return v


class SwitchConfig(BaseModel):
    """Main configuration for LLM-Dispatcher."""

    # Provider configurations
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict)

    # Switching rules
    switching_rules: SwitchingRules = Field(default_factory=SwitchingRules)

    # Global settings
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # Performance settings
    enable_async: bool = True
    max_concurrent_requests: int = 10
    request_timeout: int = 30

    # Data persistence
    data_dir: str = "~/.llm-dispatcher"
    enable_persistence: bool = True
    backup_interval_hours: int = 24

    # Advanced settings
    custom_metrics: Dict[str, Any] = Field(default_factory=dict)
    experimental_features: Dict[str, bool] = Field(default_factory=dict)

    @field_validator("providers")
    @classmethod
    def validate_providers(cls, v):
        """Validate provider configurations."""
        for name, config in v.items():
            if not config.api_key:
                raise ValueError(f"API key required for provider: {name}")
            if not config.models:
                raise ValueError(f"At least one model required for provider: {name}")

        return v

    @field_validator("data_dir")
    @classmethod
    def expand_data_dir(cls, v):
        """Expand user home directory in data_dir path."""
        return os.path.expanduser(v)

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)

    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a provider is enabled."""
        config = self.get_provider_config(provider_name)
        return config is not None and config.enabled

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled providers."""
        return [name for name, config in self.providers.items() if config.enabled]

    def get_models_for_provider(self, provider_name: str) -> List[str]:
        """Get models for a specific provider."""
        config = self.get_provider_config(provider_name)
        return config.models if config else []

    def get_task_providers(self, task_type: str) -> List[str]:
        """Get providers configured for a specific task type."""
        return self.switching_rules.task_routing.get(task_type, [])

    def set_task_providers(self, task_type: str, providers: List[str]) -> None:
        """Set providers for a specific task type."""
        self.switching_rules.task_routing[task_type] = providers

    def add_provider(self, name: str, config: ProviderConfig) -> None:
        """Add a new provider configuration."""
        self.providers[name] = config

    def remove_provider(self, name: str) -> bool:
        """Remove a provider configuration."""
        if name in self.providers:
            del self.providers[name]
            return True
        return False

    def update_provider(self, name: str, **kwargs) -> bool:
        """Update provider configuration."""
        if name not in self.providers:
            return False

        config = self.providers[name]
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return True

    def validate_config(self) -> List[str]:
        """Validate the entire configuration and return any errors."""
        errors = []

        # Check if default provider exists and is enabled
        if self.default_provider:
            if self.default_provider not in self.providers:
                errors.append(f"Default provider '{self.default_provider}' not found")
            elif not self.is_provider_enabled(self.default_provider):
                errors.append(f"Default provider '{self.default_provider}' is disabled")

        # Check if default model exists
        if self.default_model and self.default_provider:
            models = self.get_models_for_provider(self.default_provider)
            if self.default_model not in models:
                errors.append(
                    f"Default model '{self.default_model}' not found in provider '{self.default_provider}'"
                )

        # Validate task routing
        for task_type, providers in self.switching_rules.task_routing.items():
            for provider in providers:
                if provider not in self.providers:
                    errors.append(
                        f"Task routing references unknown provider '{provider}' for task '{task_type}'"
                    )
                elif not self.is_provider_enabled(provider):
                    errors.append(
                        f"Task routing references disabled provider '{provider}' for task '{task_type}'"
                    )

        # Validate budget settings
        if (
            self.switching_rules.daily_budget is not None
            and self.switching_rules.daily_budget <= 0
        ):
            errors.append("Daily budget must be positive")

        if (
            self.switching_rules.monthly_budget is not None
            and self.switching_rules.monthly_budget <= 0
        ):
            errors.append("Monthly budget must be positive")

        return errors

    def get_data_path(self, filename: str) -> Path:
        """Get full path for a data file."""
        data_dir = Path(self.data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / filename

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SwitchConfig":
        """Create configuration from dictionary."""
        return cls(**data)


# Default configuration
DEFAULT_CONFIG = SwitchConfig(
    switching_rules=SwitchingRules(
        task_routing={
            "text_generation": ["openai", "anthropic", "google"],
            "code_generation": ["anthropic", "openai", "google"],
            "reasoning": ["openai", "anthropic", "google"],
            "math": ["openai", "anthropic", "google"],
            "vision_analysis": ["openai", "anthropic", "google"],
            "audio_transcription": ["openai", "google"],
            "structured_output": ["openai", "anthropic"],
            "function_calling": ["openai", "anthropic"],
        },
        optimization_strategy=OptimizationStrategy.BALANCED,
        fallback_strategy=FallbackStrategy.PERFORMANCE_PRIORITY,
        enable_caching=True,
        enable_monitoring=True,
        alert_thresholds={
            "latency_ms": 5000,
            "success_rate": 0.95,
            "cost_per_request": 0.10,
        },
    ),
    log_level="INFO",
    enable_async=True,
    max_concurrent_requests=10,
    enable_persistence=True,
)
