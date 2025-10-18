# Error Handling

LLM-Dispatcher provides comprehensive error handling and recovery mechanisms to ensure robust operation in production environments.

## Overview

Error handling in LLM-Dispatcher is designed to be:

- **Automatic** - Handles common errors without user intervention
- **Configurable** - Allows customization of error handling behavior
- **Informative** - Provides detailed error information for debugging
- **Resilient** - Implements fallback mechanisms for reliability

## Error Types

### Provider Errors

#### Connection Errors

```python
from llm_dispatcher.exceptions import ProviderConnectionError

try:
    result = await generate_text("Your prompt")
except ProviderConnectionError as e:
    print(f"Connection failed: {e}")
    # Handle connection issues
```

#### Authentication Errors

```python
from llm_dispatcher.exceptions import ProviderAuthenticationError

try:
    result = await generate_text("Your prompt")
except ProviderAuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Check API keys
```

#### Rate Limit Errors

```python
from llm_dispatcher.exceptions import ProviderRateLimitError

try:
    result = await generate_text("Your prompt")
except ProviderRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement backoff strategy
```

#### Quota Exceeded Errors

```python
from llm_dispatcher.exceptions import ProviderQuotaExceededError

try:
    result = await generate_text("Your prompt")
except ProviderQuotaExceededError as e:
    print(f"Quota exceeded: {e}")
    # Switch to alternative provider
```

### Model Errors

#### Model Not Found

```python
from llm_dispatcher.exceptions import ModelNotFoundError

try:
    result = await generate_text("Your prompt")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
    # Use fallback model
```

#### Context Length Exceeded

```python
from llm_dispatcher.exceptions import ModelContextLengthExceededError

try:
    result = await generate_text("Your very long prompt...")
except ModelContextLengthExceededError as e:
    print(f"Context too long: {e}")
    # Truncate or split content
```

### Configuration Errors

#### Invalid Configuration

```python
from llm_dispatcher.exceptions import InvalidConfigurationError

try:
    switch = LLMSwitch(config={"invalid": "config"})
except InvalidConfigurationError as e:
    print(f"Invalid configuration: {e}")
    # Fix configuration
```

#### Missing Configuration

```python
from llm_dispatcher.exceptions import MissingConfigurationError

try:
    switch = LLMSwitch()  # No providers configured
except MissingConfigurationError as e:
    print(f"Missing configuration: {e}")
    # Add required configuration
```

### Request Errors

#### Invalid Request

```python
from llm_dispatcher.exceptions import InvalidRequestError

try:
    result = await generate_text("")  # Empty prompt
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
    # Validate request parameters
```

#### Request Timeout

```python
from llm_dispatcher.exceptions import RequestTimeoutError

try:
    result = await generate_text("Your prompt")
except RequestTimeoutError as e:
    print(f"Request timed out: {e}")
    # Implement retry logic
```

## Automatic Error Handling

### Fallback Mechanisms

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(
    fallback_enabled=True,
    max_retries=3,
    retry_delay=1000
)
def robust_generation(prompt: str) -> str:
    """Generation with automatic fallback."""
    return prompt

# Automatic fallback to alternative providers
result = robust_generation("Your prompt")
```

### Retry Logic

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.retry import ExponentialBackoff

@llm_dispatcher(
    retry_strategy=ExponentialBackoff(
        base_delay=1,
        max_delay=60,
        multiplier=2
    ),
    max_retries=5
)
def retry_generation(prompt: str) -> str:
    """Generation with exponential backoff retry."""
    return prompt
```

### Circuit Breaker Pattern

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.circuit_breaker import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

@llm_dispatcher(
    circuit_breaker=circuit_breaker
)
def circuit_breaker_generation(prompt: str) -> str:
    """Generation with circuit breaker protection."""
    return prompt
```

## Custom Error Handling

### Custom Error Handler

```python
from llm_dispatcher.exceptions import LLMDispatcherError
from llm_dispatcher.error_handling import ErrorHandler

class CustomErrorHandler(ErrorHandler):
    def handle_provider_error(self, error: ProviderError) -> str:
        """Custom provider error handling."""
        if isinstance(error, ProviderRateLimitError):
            # Implement custom rate limit handling
            return self.handle_rate_limit(error)
        elif isinstance(error, ProviderQuotaExceededError):
            # Implement custom quota handling
            return self.handle_quota_exceeded(error)
        else:
            return self.default_handler(error)

    def handle_rate_limit(self, error: ProviderRateLimitError) -> str:
        """Handle rate limit errors."""
        # Wait and retry
        import time
        time.sleep(error.retry_after)
        return "Retrying after rate limit..."

    def handle_quota_exceeded(self, error: ProviderQuotaExceededError) -> str:
        """Handle quota exceeded errors."""
        # Switch to alternative provider
        return "Switching to alternative provider..."

# Use custom error handler
switch = LLMSwitch(
    providers={...},
    config={
        "error_handler": CustomErrorHandler()
    }
)
```

### Error Recovery Strategies

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.recovery import RecoveryStrategy

class CustomRecoveryStrategy(RecoveryStrategy):
    def recover_from_error(self, error: Exception, context: dict) -> str:
        """Custom error recovery."""
        if isinstance(error, ProviderError):
            # Try alternative provider
            return self.try_alternative_provider(context)
        elif isinstance(error, ModelError):
            # Try alternative model
            return self.try_alternative_model(context)
        else:
            return self.default_recovery(error, context)

    def try_alternative_provider(self, context: dict) -> str:
        """Try alternative provider."""
        # Implementation for provider switching
        pass

    def try_alternative_model(self, context: dict) -> str:
        """Try alternative model."""
        # Implementation for model switching
        pass

@llm_dispatcher(
    recovery_strategy=CustomRecoveryStrategy()
)
def recovery_generation(prompt: str) -> str:
    """Generation with custom recovery strategy."""
    return prompt
```

## Error Monitoring and Logging

### Structured Logging

```python
import logging
from llm_dispatcher.logging import StructuredLogger

# Configure structured logging
logger = StructuredLogger(
    level=logging.INFO,
    format="json",
    include_context=True
)

@llm_dispatcher(
    logger=logger
)
def logged_generation(prompt: str) -> str:
    """Generation with structured logging."""
    return prompt

# Logs will include:
# - Request context
# - Provider information
# - Error details
# - Performance metrics
```

### Error Metrics

```python
from llm_dispatcher.monitoring import ErrorMetrics

# Track error metrics
error_metrics = ErrorMetrics()

@llm_dispatcher(
    error_metrics=error_metrics
)
def monitored_generation(prompt: str) -> str:
    """Generation with error monitoring."""
    return prompt

# Get error statistics
stats = error_metrics.get_statistics()
print(f"Error rate: {stats.error_rate:.2%}")
print(f"Most common error: {stats.most_common_error}")
print(f"Provider error distribution: {stats.provider_errors}")
```

### Alerting

```python
from llm_dispatcher.alerting import AlertManager

# Configure alerts
alert_manager = AlertManager()
alert_manager.add_alert(
    name="high_error_rate",
    condition=lambda metrics: metrics.error_rate > 0.1,
    severity="critical",
    message="Error rate is above 10%"
)

alert_manager.add_alert(
    name="provider_down",
    condition=lambda metrics: metrics.provider_availability < 0.8,
    severity="warning",
    message="Provider availability is below 80%"
)

@llm_dispatcher(
    alert_manager=alert_manager
)
def alerted_generation(prompt: str) -> str:
    """Generation with alerting."""
    return prompt
```

## Best Practices

### 1. **Always Enable Fallbacks**

```python
# Good: Enable fallbacks for production
@llm_dispatcher(fallback_enabled=True)
def reliable_generation(prompt: str) -> str:
    return prompt

# Avoid: Disabling fallbacks in production
@llm_dispatcher(fallback_enabled=False)
def unreliable_generation(prompt: str) -> str:
    return prompt
```

### 2. **Implement Proper Retry Logic**

```python
# Good: Configure appropriate retry settings
@llm_dispatcher(
    max_retries=3,
    retry_delay=1000,
    retry_strategy=ExponentialBackoff()
)
def retry_generation(prompt: str) -> str:
    return prompt

# Avoid: No retry configuration
@llm_dispatcher()
def no_retry_generation(prompt: str) -> str:
    return prompt
```

### 3. **Handle Errors Gracefully**

```python
# Good: Proper error handling
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

### 4. **Monitor Error Patterns**

```python
# Good: Monitor and analyze errors
def monitor_errors():
    metrics = error_metrics.get_statistics()
    if metrics.error_rate > 0.05:
        logger.warning(f"High error rate: {metrics.error_rate:.2%}")

    # Analyze error patterns
    for error_type, count in metrics.error_distribution.items():
        if count > 10:
            logger.warning(f"Frequent error: {error_type} ({count} occurrences)")

# Call periodically
monitor_errors()
```

### 5. **Use Circuit Breakers for Unreliable Providers**

```python
# Good: Use circuit breakers for protection
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)

@llm_dispatcher(circuit_breaker=circuit_breaker)
def protected_generation(prompt: str) -> str:
    return prompt

# Avoid: No protection against cascading failures
@llm_dispatcher()
def unprotected_generation(prompt: str) -> str:
    return prompt
```

## Error Recovery Patterns

### Graceful Degradation

```python
@llm_dispatcher(
    fallback_enabled=True,
    degradation_strategy="quality"
)
def graceful_generation(prompt: str) -> str:
    """Generation with graceful degradation."""
    return prompt

# If high-quality provider fails, fall back to lower-quality but available provider
```

### Fail-Fast Pattern

```python
@llm_dispatcher(
    fail_fast=True,
    timeout=5000
)
def fail_fast_generation(prompt: str) -> str:
    """Generation with fail-fast behavior."""
    return prompt

# Fail quickly if provider is unresponsive
```

### Bulkhead Pattern

```python
@llm_dispatcher(
    bulkhead_enabled=True,
    max_concurrent_requests=10
)
def bulkhead_generation(prompt: str) -> str:
    """Generation with bulkhead isolation."""
    return prompt

# Isolate different types of requests to prevent cascading failures
```

## Testing Error Handling

### Error Injection Testing

```python
from llm_dispatcher.testing import ErrorInjector

# Inject errors for testing
error_injector = ErrorInjector()
error_injector.inject_provider_error("openai", ProviderRateLimitError())

@llm_dispatcher(
    error_injector=error_injector
)
def test_generation(prompt: str) -> str:
    """Generation with error injection for testing."""
    return prompt

# Test error handling behavior
try:
    result = test_generation("Test prompt")
except ProviderRateLimitError:
    print("Error handling working correctly")
```

### Chaos Engineering

```python
from llm_dispatcher.chaos import ChaosMonkey

# Configure chaos testing
chaos_monkey = ChaosMonkey()
chaos_monkey.add_chaos(
    name="random_provider_failure",
    probability=0.1,
    duration=30
)

@llm_dispatcher(
    chaos_monkey=chaos_monkey
)
def chaos_generation(prompt: str) -> str:
    """Generation with chaos testing."""
    return prompt
```

## Next Steps

- [:octicons-chart-line-24: Performance Tips](performance.md) - Optimization strategies
- [:octicons-gear-24: Advanced Features](advanced-features.md) - Advanced capabilities
- [:octicons-lightning-bolt-24: Streaming](streaming.md) - Real-time response streaming
- [:octicons-eye-24: Multimodal Support](multimodal.md) - Working with images and audio
