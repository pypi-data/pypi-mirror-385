# Exceptions API Reference

This page provides comprehensive documentation for the LLM-Dispatcher exception handling system.

## Exception Hierarchy

LLM-Dispatcher uses a hierarchical exception system to provide specific error handling for different types of failures.

```python
LLMDispatcherError (Base Exception)
├── ProviderError
│   ├── ProviderConnectionError
│   ├── ProviderAuthenticationError
│   ├── ProviderRateLimitError
│   ├── ProviderQuotaExceededError
│   └── ProviderTimeoutError
├── ModelError
│   ├── ModelNotFoundError
│   ├── ModelContextLengthExceededError
│   └── ModelUnavailableError
├── ConfigurationError
│   ├── InvalidConfigurationError
│   ├── MissingConfigurationError
│   └── ConfigurationValidationError
├── RequestError
│   ├── InvalidRequestError
│   ├── RequestTimeoutError
│   └── RequestValidationError
├── CacheError
│   ├── CacheConnectionError
│   ├── CacheKeyError
│   └── CacheTimeoutError
└── MonitoringError
    ├── MetricsError
    └── AlertingError
```

## Base Exceptions

### LLMDispatcherError

The base exception class for all LLM-Dispatcher errors.

```python
from llm_dispatcher.exceptions import LLMDispatcherError

class LLMDispatcherError(Exception):
    """Base exception for all LLM-Dispatcher errors."""

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message
```

#### Usage

```python
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    print(f"Dispatcher error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
```

## Provider Exceptions

### ProviderError

Base exception for provider-related errors.

```python
from llm_dispatcher.exceptions import ProviderError

class ProviderError(LLMDispatcherError):
    """Base exception for provider-related errors."""

    def __init__(self, message: str, provider: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.provider = provider
```

### ProviderConnectionError

Raised when there's a connection issue with a provider.

```python
from llm_dispatcher.exceptions import ProviderConnectionError

try:
    result = await generate_text("Your prompt")
except ProviderConnectionError as e:
    print(f"Connection failed to {e.provider}: {e}")
    # Handle connection issues
    # - Check network connectivity
    # - Verify provider endpoints
    # - Implement retry logic
```

#### Attributes

- `provider: str` - The provider that failed
- `endpoint: str` - The endpoint that failed
- `status_code: int` - HTTP status code (if applicable)

### ProviderAuthenticationError

Raised when authentication fails with a provider.

```python
from llm_dispatcher.exceptions import ProviderAuthenticationError

try:
    result = await generate_text("Your prompt")
except ProviderAuthenticationError as e:
    print(f"Authentication failed for {e.provider}: {e}")
    # Handle authentication issues
    # - Check API keys
    # - Verify credentials
    # - Update authentication
```

#### Attributes

- `provider: str` - The provider that failed authentication
- `api_key: str` - The API key that failed (masked)

### ProviderRateLimitError

Raised when rate limits are exceeded.

```python
from llm_dispatcher.exceptions import ProviderRateLimitError

try:
    result = await generate_text("Your prompt")
except ProviderRateLimitError as e:
    print(f"Rate limit exceeded for {e.provider}: {e}")
    print(f"Retry after: {e.retry_after} seconds")
    # Handle rate limiting
    # - Implement backoff strategy
    # - Wait for retry_after period
    # - Switch to alternative provider
```

#### Attributes

- `provider: str` - The provider that hit rate limits
- `retry_after: int` - Seconds to wait before retrying
- `limit_type: str` - Type of rate limit (requests, tokens, etc.)
- `current_usage: int` - Current usage count
- `limit: int` - The rate limit threshold

### ProviderQuotaExceededError

Raised when quota limits are exceeded.

```python
from llm_dispatcher.exceptions import ProviderQuotaExceededError

try:
    result = await generate_text("Your prompt")
except ProviderQuotaExceededError as e:
    print(f"Quota exceeded for {e.provider}: {e}")
    print(f"Quota type: {e.quota_type}")
    print(f"Reset time: {e.reset_time}")
    # Handle quota issues
    # - Switch to alternative provider
    # - Wait for quota reset
    # - Upgrade quota limits
```

#### Attributes

- `provider: str` - The provider that exceeded quota
- `quota_type: str` - Type of quota (daily, monthly, etc.)
- `current_usage: float` - Current usage amount
- `limit: float` - The quota limit
- `reset_time: datetime` - When the quota resets

### ProviderTimeoutError

Raised when requests timeout.

```python
from llm_dispatcher.exceptions import ProviderTimeoutError

try:
    result = await generate_text("Your prompt")
except ProviderTimeoutError as e:
    print(f"Timeout for {e.provider}: {e}")
    print(f"Timeout duration: {e.timeout_duration} seconds")
    # Handle timeout issues
    # - Increase timeout duration
    # - Implement retry logic
    # - Switch to faster provider
```

#### Attributes

- `provider: str` - The provider that timed out
- `timeout_duration: int` - The timeout duration in seconds
- `request_type: str` - Type of request that timed out

## Model Exceptions

### ModelError

Base exception for model-related errors.

```python
from llm_dispatcher.exceptions import ModelError

class ModelError(LLMDispatcherError):
    """Base exception for model-related errors."""

    def __init__(self, message: str, model: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model = model
```

### ModelNotFoundError

Raised when a requested model is not found.

```python
from llm_dispatcher.exceptions import ModelNotFoundError

try:
    result = await generate_text("Your prompt")
except ModelNotFoundError as e:
    print(f"Model not found: {e.model}")
    # Handle model not found
    # - Use fallback model
    # - Check model availability
    # - Update model list
```

#### Attributes

- `model: str` - The model that was not found
- `available_models: List[str]` - List of available models

### ModelContextLengthExceededError

Raised when the context length is exceeded.

```python
from llm_dispatcher.exceptions import ModelContextLengthExceededError

try:
    result = await generate_text("Your very long prompt...")
except ModelContextLengthExceededError as e:
    print(f"Context too long for {e.model}: {e}")
    print(f"Max context length: {e.max_context_length}")
    print(f"Request context length: {e.request_context_length}")
    # Handle context length issues
    # - Truncate input
    # - Split into chunks
    # - Use model with larger context
```

#### Attributes

- `model: str` - The model that exceeded context length
- `max_context_length: int` - Maximum context length for the model
- `request_context_length: int` - Context length of the request

### ModelUnavailableError

Raised when a model is temporarily unavailable.

```python
from llm_dispatcher.exceptions import ModelUnavailableError

try:
    result = await generate_text("Your prompt")
except ModelUnavailableError as e:
    print(f"Model unavailable: {e.model}")
    print(f"Estimated availability: {e.estimated_availability}")
    # Handle model unavailability
    # - Use alternative model
    # - Wait for model to become available
    # - Implement retry logic
```

#### Attributes

- `model: str` - The unavailable model
- `estimated_availability: datetime` - When the model might be available
- `reason: str` - Reason for unavailability

## Configuration Exceptions

### ConfigurationError

Base exception for configuration-related errors.

```python
from llm_dispatcher.exceptions import ConfigurationError

class ConfigurationError(LLMDispatcherError):
    """Base exception for configuration-related errors."""

    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key
```

### InvalidConfigurationError

Raised when configuration is invalid.

```python
from llm_dispatcher.exceptions import InvalidConfigurationError

try:
    switch = LLMSwitch(config={"invalid": "config"})
except InvalidConfigurationError as e:
    print(f"Invalid configuration: {e}")
    print(f"Config key: {e.config_key}")
    print(f"Expected type: {e.expected_type}")
    print(f"Actual type: {e.actual_type}")
    # Handle invalid configuration
    # - Fix configuration values
    # - Validate configuration
    # - Use default values
```

#### Attributes

- `config_key: str` - The configuration key that is invalid
- `expected_type: str` - The expected type
- `actual_type: str` - The actual type
- `value: Any` - The invalid value

### MissingConfigurationError

Raised when required configuration is missing.

```python
from llm_dispatcher.exceptions import MissingConfigurationError

try:
    switch = LLMSwitch()  # No providers configured
except MissingConfigurationError as e:
    print(f"Missing configuration: {e}")
    print(f"Missing keys: {e.missing_keys}")
    # Handle missing configuration
    # - Add required configuration
    # - Use environment variables
    # - Provide default values
```

#### Attributes

- `missing_keys: List[str]` - List of missing configuration keys
- `required_keys: List[str]` - List of required configuration keys

### ConfigurationValidationError

Raised when configuration validation fails.

```python
from llm_dispatcher.exceptions import ConfigurationValidationError

try:
    switch = LLMSwitch(config={"max_retries": -1})
except ConfigurationValidationError as e:
    print(f"Configuration validation failed: {e}")
    print(f"Validation errors: {e.validation_errors}")
    # Handle validation errors
    # - Fix validation issues
    # - Update configuration
    # - Use valid defaults
```

#### Attributes

- `validation_errors: List[str]` - List of validation error messages
- `config_section: str` - The configuration section that failed validation

## Request Exceptions

### RequestError

Base exception for request-related errors.

```python
from llm_dispatcher.exceptions import RequestError

class RequestError(LLMDispatcherError):
    """Base exception for request-related errors."""

    def __init__(self, message: str, request_id: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.request_id = request_id
```

### InvalidRequestError

Raised when a request is invalid.

```python
from llm_dispatcher.exceptions import InvalidRequestError

try:
    result = await generate_text("")  # Empty prompt
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
    print(f"Request ID: {e.request_id}")
    print(f"Validation errors: {e.validation_errors}")
    # Handle invalid request
    # - Validate request parameters
    # - Fix request format
    # - Provide error feedback
```

#### Attributes

- `request_id: str` - The request ID
- `validation_errors: List[str]` - List of validation error messages
- `request_data: Dict[str, Any]` - The invalid request data

### RequestTimeoutError

Raised when a request times out.

```python
from llm_dispatcher.exceptions import RequestTimeoutError

try:
    result = await generate_text("Your prompt")
except RequestTimeoutError as e:
    print(f"Request timeout: {e}")
    print(f"Request ID: {e.request_id}")
    print(f"Timeout duration: {e.timeout_duration}")
    # Handle request timeout
    # - Increase timeout duration
    # - Implement retry logic
    # - Use faster provider
```

#### Attributes

- `request_id: str` - The request ID
- `timeout_duration: int` - The timeout duration in milliseconds
- `provider: str` - The provider that timed out

### RequestValidationError

Raised when request validation fails.

```python
from llm_dispatcher.exceptions import RequestValidationError

try:
    result = await generate_text("Your prompt", max_tokens=-1)
except RequestValidationError as e:
    print(f"Request validation failed: {e}")
    print(f"Validation errors: {e.validation_errors}")
    # Handle validation errors
    # - Fix request parameters
    # - Validate input data
    # - Provide error feedback
```

#### Attributes

- `validation_errors: List[str]` - List of validation error messages
- `request_data: Dict[str, Any]` - The request data that failed validation

## Cache Exceptions

### CacheError

Base exception for cache-related errors.

```python
from llm_dispatcher.exceptions import CacheError

class CacheError(LLMDispatcherError):
    """Base exception for cache-related errors."""

    def __init__(self, message: str, cache_type: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.cache_type = cache_type
```

### CacheConnectionError

Raised when there's a connection issue with the cache.

```python
from llm_dispatcher.exceptions import CacheConnectionError

try:
    result = await generate_text("Your prompt")
except CacheConnectionError as e:
    print(f"Cache connection failed: {e}")
    print(f"Cache type: {e.cache_type}")
    # Handle cache connection issues
    # - Check cache server status
    # - Implement fallback
    # - Retry connection
```

### CacheKeyError

Raised when a cache key is not found.

```python
from llm_dispatcher.exceptions import CacheKeyError

try:
    result = await generate_text("Your prompt")
except CacheKeyError as e:
    print(f"Cache key not found: {e}")
    print(f"Cache key: {e.cache_key}")
    # Handle cache key issues
    # - Check key format
    # - Implement fallback
    # - Generate new key
```

### CacheTimeoutError

Raised when cache operations timeout.

```python
from llm_dispatcher.exceptions import CacheTimeoutError

try:
    result = await generate_text("Your prompt")
except CacheTimeoutError as e:
    print(f"Cache timeout: {e}")
    print(f"Cache operation: {e.operation}")
    # Handle cache timeout
    # - Increase timeout duration
    # - Implement retry logic
    # - Use fallback cache
```

## Monitoring Exceptions

### MonitoringError

Base exception for monitoring-related errors.

```python
from llm_dispatcher.exceptions import MonitoringError

class MonitoringError(LLMDispatcherError):
    """Base exception for monitoring-related errors."""

    def __init__(self, message: str, metric_name: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.metric_name = metric_name
```

### MetricsError

Raised when metrics collection fails.

```python
from llm_dispatcher.exceptions import MetricsError

try:
    result = await generate_text("Your prompt")
except MetricsError as e:
    print(f"Metrics error: {e}")
    print(f"Metric name: {e.metric_name}")
    # Handle metrics errors
    # - Check metrics configuration
    # - Implement fallback
    # - Retry metrics collection
```

### AlertingError

Raised when alerting fails.

```python
from llm_dispatcher.exceptions import AlertingError

try:
    result = await generate_text("Your prompt")
except AlertingError as e:
    print(f"Alerting error: {e}")
    print(f"Alert type: {e.alert_type}")
    # Handle alerting errors
    # - Check alert configuration
    # - Implement fallback
    # - Retry alerting
```

## Error Handling Patterns

### Basic Error Handling

```python
from llm_dispatcher.exceptions import LLMDispatcherError

try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    print(f"Error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
```

### Specific Error Handling

```python
from llm_dispatcher.exceptions import (
    ProviderError,
    ModelError,
    ConfigurationError,
    RequestError
)

try:
    result = generate_text("Your prompt")
except ProviderError as e:
    print(f"Provider error: {e}")
    # Handle provider-specific errors
except ModelError as e:
    print(f"Model error: {e}")
    # Handle model-specific errors
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration errors
except RequestError as e:
    print(f"Request error: {e}")
    # Handle request errors
```

### Comprehensive Error Handling

```python
from llm_dispatcher.exceptions import (
    LLMDispatcherError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ModelNotFoundError,
    RequestTimeoutError
)

try:
    result = generate_text("Your prompt")
except ProviderConnectionError as e:
    print(f"Connection failed: {e}")
    # Implement retry logic
except ProviderAuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Check API keys
except ProviderRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement backoff strategy
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    # Use fallback model
except RequestTimeoutError as e:
    print(f"Request timeout: {e}")
    # Increase timeout or retry
except LLMDispatcherError as e:
    print(f"Dispatcher error: {e}")
    # Handle other dispatcher errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Error Recovery Strategies

### Automatic Retry

```python
from llm_dispatcher.retry import ExponentialBackoff

@llm_dispatcher(
    max_retries=3,
    retry_strategy=ExponentialBackoff()
)
def retry_generation(prompt: str) -> str:
    """Generation with automatic retry."""
    return prompt
```

### Fallback Providers

```python
@llm_dispatcher(
    fallback_enabled=True,
    fallback_providers=["anthropic", "google"]
)
def fallback_generation(prompt: str) -> str:
    """Generation with fallback providers."""
    return prompt
```

### Circuit Breaker

```python
from llm_dispatcher.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

@llm_dispatcher(circuit_breaker=circuit_breaker)
def circuit_breaker_generation(prompt: str) -> str:
    """Generation with circuit breaker protection."""
    return prompt
```

## Best Practices

### 1. **Handle Errors Gracefully**

```python
# Good: Comprehensive error handling
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    logger.error(f"Generation failed: {e}")
    # Implement fallback logic
    result = "Fallback response"
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    result = "Error occurred"

# Avoid: Ignoring errors
result = generate_text("Your prompt")  # May raise unhandled exceptions
```

### 2. **Use Specific Exception Types**

```python
# Good: Handle specific exceptions
try:
    result = generate_text("Your prompt")
except ProviderRateLimitError as e:
    # Handle rate limiting specifically
    time.sleep(e.retry_after)
    result = generate_text("Your prompt")
except ProviderAuthenticationError as e:
    # Handle authentication issues
    update_api_key()
    result = generate_text("Your prompt")

# Avoid: Catching all exceptions
try:
    result = generate_text("Your prompt")
except Exception as e:
    # Too generic
    pass
```

### 3. **Implement Proper Logging**

```python
# Good: Log errors with context
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    logger.error(
        "Generation failed",
        extra={
            "error": str(e),
            "error_code": e.error_code,
            "details": e.details,
            "prompt": "Your prompt"
        }
    )
    raise

# Avoid: No logging
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    # No logging
    pass
```

### 4. **Provide User-Friendly Error Messages**

```python
# Good: User-friendly error messages
try:
    result = generate_text("Your prompt")
except ProviderRateLimitError as e:
    user_message = f"Service is temporarily busy. Please try again in {e.retry_after} seconds."
    return {"error": user_message, "retry_after": e.retry_after}
except ProviderAuthenticationError as e:
    user_message = "Authentication failed. Please check your API key."
    return {"error": user_message}

# Avoid: Technical error messages
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    return {"error": str(e)}  # Too technical
```

### 5. **Implement Monitoring and Alerting**

```python
# Good: Monitor and alert on errors
def handle_error(error: LLMDispatcherError):
    # Log error
    logger.error(f"Error occurred: {error}")

    # Update metrics
    error_metrics.increment(error.error_code)

    # Send alert for critical errors
    if isinstance(error, ProviderError):
        alert_manager.send_alert(
            "Provider Error",
            f"Provider {error.provider} failed: {error}",
            severity="critical"
        )

# Avoid: No monitoring
def handle_error(error: LLMDispatcherError):
    # No monitoring or alerting
    pass
```

## Next Steps

- [:octicons-puzzle-24: Core API](core.md) - Core API reference
- [:octicons-puzzle-24: Decorators](decorators.md) - Decorator API reference
- [:octicons-plug-24: Providers](providers.md) - Provider implementations
- [:octicons-gear-24: Configuration](configuration.md) - Configuration options
