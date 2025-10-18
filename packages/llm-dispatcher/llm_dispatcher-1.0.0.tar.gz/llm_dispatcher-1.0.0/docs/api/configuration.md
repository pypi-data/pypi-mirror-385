# Configuration API Reference

This page provides comprehensive documentation for the LLM-Dispatcher configuration system.

## Overview

LLM-Dispatcher provides a flexible configuration system that supports multiple configuration sources and formats. Configuration can be provided through environment variables, YAML files, or programmatically.

## Configuration Sources

### Environment Variables

Configuration can be set using environment variables with the `LLM_DISPATCHER_` prefix.

```bash
# Provider API keys
export LLM_DISPATCHER_OPENAI_API_KEY="sk-..."
export LLM_DISPATCHER_ANTHROPIC_API_KEY="sk-ant-..."
export LLM_DISPATCHER_GOOGLE_API_KEY="..."

# Global settings
export LLM_DISPATCHER_OPTIMIZATION_STRATEGY="balanced"
export LLM_DISPATCHER_FALLBACK_ENABLED="true"
export LLM_DISPATCHER_MAX_RETRIES="3"
export LLM_DISPATCHER_TIMEOUT="30000"
```

### YAML Configuration Files

Configuration can be defined in YAML files.

```yaml
# config.yaml
providers:
  openai:
    api_key: "sk-..."
    models: ["gpt-4", "gpt-3.5-turbo"]
    max_tokens: 4096
    temperature: 0.7
    timeout: 30
    max_retries: 3
    cost_per_token: 0.00003

  anthropic:
    api_key: "sk-ant-..."
    models: ["claude-3-sonnet", "claude-3-haiku"]
    max_tokens: 4096
    temperature: 0.7
    timeout: 30
    max_retries: 3
    cost_per_token: 0.000015

  google:
    api_key: "..."
    models: ["gemini-2.5-pro", "gemini-2.5-flash"]
    max_tokens: 4096
    temperature: 0.7
    timeout: 30
    max_retries: 3
    cost_per_token: 0.00001

global:
  optimization_strategy: "balanced"
  fallback_enabled: true
  max_retries: 3
  retry_delay: 1000
  timeout: 30000
  cache_enabled: true
  monitoring_enabled: true
  logging_level: "INFO"

cache:
  type: "semantic"
  similarity_threshold: 0.95
  max_cache_size: 1000
  ttl: 3600

monitoring:
  enabled: true
  metrics_interval: 60
  alert_thresholds:
    latency: 5000
    error_rate: 0.05
    cost_per_hour: 10.0
```

### Programmatic Configuration

Configuration can be set programmatically when initializing the dispatcher.

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.config.settings import OptimizationStrategy

# Programmatic configuration
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"]
        },
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-sonnet", "claude-3-haiku"]
        }
    },
    config={
        "optimization_strategy": OptimizationStrategy.BALANCED,
        "fallback_enabled": True,
        "max_retries": 3,
        "timeout": 30000
    }
)
```

## Configuration Classes

### SwitchConfig

Main configuration class for the LLM switch.

```python
from llm_dispatcher.config.settings import SwitchConfig

config = SwitchConfig(
    optimization_strategy=OptimizationStrategy.BALANCED,
    fallback_enabled=True,
    max_retries=3,
    retry_delay=1000,
    timeout=30000,
    cache_enabled=True,
    monitoring_enabled=True,
    logging_level="INFO"
)
```

#### Attributes

| Attribute               | Type                   | Default    | Description                              |
| ----------------------- | ---------------------- | ---------- | ---------------------------------------- |
| `optimization_strategy` | `OptimizationStrategy` | `BALANCED` | Optimization strategy                    |
| `fallback_enabled`      | `bool`                 | `True`     | Enable fallback to alternative providers |
| `max_retries`           | `int`                  | `3`        | Maximum number of retry attempts         |
| `retry_delay`           | `int`                  | `1000`     | Delay between retries in milliseconds    |
| `timeout`               | `int`                  | `30000`    | Request timeout in milliseconds          |
| `cache_enabled`         | `bool`                 | `True`     | Enable caching                           |
| `monitoring_enabled`    | `bool`                 | `True`     | Enable monitoring                        |
| `logging_level`         | `str`                  | `"INFO"`   | Logging level                            |

### ProviderConfig

Configuration class for individual providers.

```python
from llm_dispatcher.config.settings import ProviderConfig

provider_config = ProviderConfig(
    name="openai",
    api_key="sk-...",
    models=["gpt-4", "gpt-3.5-turbo"],
    max_tokens=4096,
    temperature=0.7,
    timeout=30,
    max_retries=3,
    cost_per_token=0.00003
)
```

#### Attributes

| Attribute        | Type        | Default  | Description                |
| ---------------- | ----------- | -------- | -------------------------- |
| `name`           | `str`       | Required | Provider name              |
| `api_key`        | `str`       | Required | API key for the provider   |
| `models`         | `List[str]` | `[]`     | Available models           |
| `max_tokens`     | `int`       | `4096`   | Maximum tokens per request |
| `temperature`    | `float`     | `0.7`    | Sampling temperature       |
| `timeout`        | `int`       | `30`     | Request timeout in seconds |
| `max_retries`    | `int`       | `3`      | Maximum retry attempts     |
| `cost_per_token` | `float`     | `0.0`    | Cost per token             |

### CacheConfig

Configuration class for caching.

```python
from llm_dispatcher.config.settings import CacheConfig

cache_config = CacheConfig(
    type="semantic",
    similarity_threshold=0.95,
    max_cache_size=1000,
    ttl=3600,
    compression_enabled=True
)
```

#### Attributes

| Attribute              | Type    | Default    | Description                             |
| ---------------------- | ------- | ---------- | --------------------------------------- |
| `type`                 | `str`   | `"memory"` | Cache type (memory, redis, semantic)    |
| `similarity_threshold` | `float` | `0.95`     | Similarity threshold for semantic cache |
| `max_cache_size`       | `int`   | `1000`     | Maximum cache size                      |
| `ttl`                  | `int`   | `3600`     | Time-to-live in seconds                 |
| `compression_enabled`  | `bool`  | `False`    | Enable cache compression                |

### MonitoringConfig

Configuration class for monitoring.

```python
from llm_dispatcher.config.settings import MonitoringConfig

monitoring_config = MonitoringConfig(
    enabled=True,
    metrics_interval=60,
    alert_thresholds={
        "latency": 5000,
        "error_rate": 0.05,
        "cost_per_hour": 10.0
    }
)
```

#### Attributes

| Attribute          | Type             | Default | Description                            |
| ------------------ | ---------------- | ------- | -------------------------------------- |
| `enabled`          | `bool`           | `True`  | Enable monitoring                      |
| `metrics_interval` | `int`            | `60`    | Metrics collection interval in seconds |
| `alert_thresholds` | `Dict[str, Any]` | `{}`    | Alert thresholds                       |

## Configuration Loading

### ConfigLoader

Utility class for loading configuration from various sources.

```python
from llm_dispatcher.config.config_loader import ConfigLoader

# Load from YAML file
config_loader = ConfigLoader()
config = config_loader.load_from_file("config.yaml")

# Load from environment variables
config = config_loader.load_from_env()

# Load from multiple sources
config = config_loader.load_from_sources([
    "config.yaml",
    "config.prod.yaml",
    "env"
])
```

#### Methods

##### `load_from_file(file_path: str) -> Dict[str, Any]`

```python
config = config_loader.load_from_file("config.yaml")
```

##### `load_from_env() -> Dict[str, Any]`

```python
config = config_loader.load_from_env()
```

##### `load_from_sources(sources: List[str]) -> Dict[str, Any]`

```python
config = config_loader.load_from_sources([
    "config.yaml",
    "config.prod.yaml",
    "env"
])
```

##### `validate_config(config: Dict[str, Any]) -> bool`

```python
is_valid = config_loader.validate_config(config)
```

## Configuration Validation

### Validation Rules

Configuration is validated against predefined rules to ensure correctness.

```python
from llm_dispatcher.config.validation import ConfigValidator

validator = ConfigValidator()

# Validate configuration
is_valid, errors = validator.validate(config)
if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

#### Validation Rules

| Rule                 | Description                                |
| -------------------- | ------------------------------------------ |
| `required_providers` | At least one provider must be configured   |
| `valid_api_keys`     | API keys must be non-empty strings         |
| `valid_models`       | Models must be non-empty lists             |
| `valid_timeouts`     | Timeouts must be positive integers         |
| `valid_retries`      | Retry counts must be non-negative integers |
| `valid_temperatures` | Temperatures must be between 0 and 2       |
| `valid_max_tokens`   | Max tokens must be positive integers       |

### Custom Validation

```python
from llm_dispatcher.config.validation import ConfigValidator

class CustomConfigValidator(ConfigValidator):
    """Custom configuration validator."""

    def validate_custom_rule(self, config: Dict[str, Any]) -> List[str]:
        """Validate custom rule."""
        errors = []
        if config.get("custom_setting") == "invalid":
            errors.append("Custom setting is invalid")
        return errors

validator = CustomConfigValidator()
is_valid, errors = validator.validate(config)
```

## Configuration Examples

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

# Basic configuration with minimal settings
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"]
        }
    }
)
```

### Production Configuration

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.config.settings import OptimizationStrategy

# Production configuration with comprehensive settings
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.00003
        },
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-sonnet", "claude-3-haiku"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.000015
        }
    },
    config={
        "optimization_strategy": OptimizationStrategy.BALANCED,
        "fallback_enabled": True,
        "max_retries": 3,
        "retry_delay": 1000,
        "timeout": 30000,
        "cache_enabled": True,
        "monitoring_enabled": True,
        "logging_level": "INFO"
    }
)
```

### Development Configuration

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.config.settings import OptimizationStrategy

# Development configuration with relaxed settings
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-3.5-turbo"],  # Cheaper model for development
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 60,  # Longer timeout for development
            "max_retries": 1,  # Fewer retries for faster feedback
            "cost_per_token": 0.00003
        }
    },
    config={
        "optimization_strategy": OptimizationStrategy.COST,  # Cost optimization for development
        "fallback_enabled": False,  # Disable fallback for development
        "max_retries": 1,
        "retry_delay": 500,
        "timeout": 60000,
        "cache_enabled": False,  # Disable cache for development
        "monitoring_enabled": False,  # Disable monitoring for development
        "logging_level": "DEBUG"
    }
)
```

### Testing Configuration

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.config.settings import OptimizationStrategy

# Testing configuration with mock providers
switch = LLMSwitch(
    providers={
        "mock": {
            "api_key": "mock-key",
            "models": ["mock-model"],
            "max_tokens": 100,
            "temperature": 0.7,
            "timeout": 5,
            "max_retries": 1,
            "cost_per_token": 0.0
        }
    },
    config={
        "optimization_strategy": OptimizationStrategy.SPEED,
        "fallback_enabled": False,
        "max_retries": 1,
        "retry_delay": 100,
        "timeout": 5000,
        "cache_enabled": False,
        "monitoring_enabled": False,
        "logging_level": "WARNING"
    }
)
```

## Environment-Specific Configuration

### Development Environment

```yaml
# config.dev.yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    models: ["gpt-3.5-turbo"]
    max_tokens: 1000
    temperature: 0.7
    timeout: 60
    max_retries: 1

global:
  optimization_strategy: "cost"
  fallback_enabled: false
  max_retries: 1
  timeout: 60000
  cache_enabled: false
  monitoring_enabled: false
  logging_level: "DEBUG"
```

### Production Environment

```yaml
# config.prod.yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    models: ["gpt-4", "gpt-3.5-turbo"]
    max_tokens: 4096
    temperature: 0.7
    timeout: 30
    max_retries: 3

  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    models: ["claude-3-sonnet", "claude-3-haiku"]
    max_tokens: 4096
    temperature: 0.7
    timeout: 30
    max_retries: 3

global:
  optimization_strategy: "balanced"
  fallback_enabled: true
  max_retries: 3
  timeout: 30000
  cache_enabled: true
  monitoring_enabled: true
  logging_level: "INFO"

cache:
  type: "redis"
  host: "${REDIS_HOST}"
  port: "${REDIS_PORT}"
  db: 0
  ttl: 3600

monitoring:
  enabled: true
  metrics_interval: 60
  alert_thresholds:
    latency: 5000
    error_rate: 0.05
    cost_per_hour: 10.0
```

### Testing Environment

```yaml
# config.test.yaml
providers:
  mock:
    api_key: "mock-key"
    models: ["mock-model"]
    max_tokens: 100
    temperature: 0.7
    timeout: 5
    max_retries: 1

global:
  optimization_strategy: "speed"
  fallback_enabled: false
  max_retries: 1
  timeout: 5000
  cache_enabled: false
  monitoring_enabled: false
  logging_level: "WARNING"
```

## Configuration Management

### Runtime Configuration Updates

```python
# Update configuration at runtime
switch.update_config({
    "optimization_strategy": OptimizationStrategy.COST,
    "max_retries": 5,
    "timeout": 60000
})
```

### Configuration Validation

```python
from llm_dispatcher.config.validation import ConfigValidator

# Validate configuration before applying
validator = ConfigValidator()
is_valid, errors = validator.validate(new_config)
if is_valid:
    switch.update_config(new_config)
else:
    print(f"Configuration validation failed: {errors}")
```

### Configuration Backup and Restore

```python
# Backup current configuration
backup_config = switch.get_config()

# Apply new configuration
switch.update_config(new_config)

# Restore backup if needed
switch.update_config(backup_config)
```

## Best Practices

### 1. **Use Environment Variables for Secrets**

```python
# Good: Use environment variables for API keys
providers = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "models": ["gpt-4", "gpt-3.5-turbo"]
    }
}

# Avoid: Hardcoding API keys
providers = {
    "openai": {
        "api_key": "sk-...",  # Never hardcode secrets
        "models": ["gpt-4", "gpt-3.5-turbo"]
    }
}
```

### 2. **Use Configuration Files for Complex Settings**

```python
# Good: Use YAML files for complex configuration
config_loader = ConfigLoader()
config = config_loader.load_from_file("config.yaml")

# Avoid: Complex configuration in code
config = {
    "providers": {
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.00003
        }
    }
}
```

### 3. **Validate Configuration**

```python
# Good: Validate configuration
validator = ConfigValidator()
is_valid, errors = validator.validate(config)
if not is_valid:
    raise ConfigurationError(f"Invalid configuration: {errors}")

# Avoid: No validation
switch = LLMSwitch(config=config)  # May fail at runtime
```

### 4. **Use Environment-Specific Configuration**

```python
# Good: Environment-specific configuration
config_files = {
    "development": "config.dev.yaml",
    "production": "config.prod.yaml",
    "testing": "config.test.yaml"
}

config_file = config_files[os.getenv("ENVIRONMENT", "development")]
config = config_loader.load_from_file(config_file)

# Avoid: Single configuration for all environments
config = config_loader.load_from_file("config.yaml")
```

### 5. **Monitor Configuration Changes**

```python
# Good: Monitor configuration changes
def on_config_change(old_config, new_config):
    logger.info("Configuration updated")
    # Validate new configuration
    # Update monitoring settings
    # Notify relevant components

switch.add_config_change_listener(on_config_change)

# Avoid: No monitoring of configuration changes
switch.update_config(new_config)  # No monitoring
```

## Next Steps

- [:octicons-puzzle-24: Core API](core.md) - Core API reference
- [:octicons-puzzle-24: Decorators](decorators.md) - Decorator API reference
- [:octicons-plug-24: Providers](providers.md) - Provider implementations
- [:octicons-exclamation-triangle-24: Exceptions](exceptions.md) - Exception handling
