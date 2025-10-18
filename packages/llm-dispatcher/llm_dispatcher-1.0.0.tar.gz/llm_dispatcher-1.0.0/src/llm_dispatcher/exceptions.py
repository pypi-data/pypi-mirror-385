"""
Custom exceptions for LLM-Dispatcher.

This module defines custom exceptions that provide more specific error handling
and better debugging information for LLM dispatcher operations.
"""

from typing import Optional, Dict, Any


class LLMDispatcherError(Exception):
    """Base exception class for all LLM-Dispatcher errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ProviderError(LLMDispatcherError):
    """Base exception for provider-related errors."""

    def __init__(
        self,
        message: str,
        provider: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.provider = provider


class ProviderConnectionError(ProviderError):
    """Raised when unable to connect to a provider."""

    def __init__(
        self,
        provider: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Unable to connect to provider: {provider}"
        super().__init__(message, provider, "CONNECTION_ERROR", details)


class ProviderAuthenticationError(ProviderError):
    """Raised when provider authentication fails."""

    def __init__(
        self,
        provider: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Authentication failed for provider: {provider}"
        super().__init__(message, provider, "AUTHENTICATION_ERROR", details)


class ProviderRateLimitError(ProviderError):
    """Raised when provider rate limit is exceeded."""

    def __init__(
        self,
        provider: str,
        retry_after: Optional[int] = None,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Rate limit exceeded for provider: {provider}"
        super().__init__(message, provider, "RATE_LIMIT_ERROR", details)
        self.retry_after = retry_after


class ProviderQuotaExceededError(ProviderError):
    """Raised when provider quota is exceeded."""

    def __init__(
        self,
        provider: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Quota exceeded for provider: {provider}"
        super().__init__(message, provider, "QUOTA_EXCEEDED_ERROR", details)


class ProviderTimeoutError(ProviderError):
    """Raised when provider request times out."""

    def __init__(
        self,
        provider: str,
        timeout: Optional[float] = None,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Request timeout for provider: {provider}"
        super().__init__(message, provider, "TIMEOUT_ERROR", details)
        self.timeout = timeout


class ProviderServiceUnavailableError(ProviderError):
    """Raised when provider service is unavailable."""

    def __init__(
        self,
        provider: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Service unavailable for provider: {provider}"
        super().__init__(message, provider, "SERVICE_UNAVAILABLE_ERROR", details)


class ModelError(LLMDispatcherError):
    """Base exception for model-related errors."""

    def __init__(
        self,
        message: str,
        model: str,
        provider: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.model = model
        self.provider = provider


class ModelNotFoundError(ModelError):
    """Raised when a requested model is not found."""

    def __init__(
        self,
        model: str,
        provider: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Model '{model}' not found in provider '{provider}'"
        super().__init__(message, model, provider, "MODEL_NOT_FOUND_ERROR", details)


class ModelUnsupportedError(ModelError):
    """Raised when a model doesn't support the requested capability."""

    def __init__(
        self,
        model: str,
        provider: str,
        capability: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Model '{model}' in provider '{provider}' does not support capability: {capability}"
        super().__init__(message, model, provider, "MODEL_UNSUPPORTED_ERROR", details)
        self.capability = capability


class ModelContextLengthExceededError(ModelError):
    """Raised when request exceeds model's context length."""

    def __init__(
        self,
        model: str,
        provider: str,
        requested_tokens: int,
        max_tokens: int,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Context length exceeded for model '{model}' in provider '{provider}'. Requested: {requested_tokens}, Max: {max_tokens}"
        super().__init__(
            message, model, provider, "CONTEXT_LENGTH_EXCEEDED_ERROR", details
        )
        self.requested_tokens = requested_tokens
        self.max_tokens = max_tokens


class ConfigurationError(LLMDispatcherError):
    """Base exception for configuration-related errors."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.config_key = config_key


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        config_key: str,
        value: Any,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Invalid configuration for '{config_key}': {value}"
        super().__init__(message, config_key, "INVALID_CONFIG_ERROR", details)
        self.value = value


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing."""

    def __init__(
        self,
        config_key: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Missing required configuration: {config_key}"
        super().__init__(message, config_key, "MISSING_CONFIG_ERROR", details)


class RequestError(LLMDispatcherError):
    """Base exception for request-related errors."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.request_id = request_id


class InvalidRequestError(RequestError):
    """Raised when request is invalid."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, request_id, "INVALID_REQUEST_ERROR", details)


class RequestTimeoutError(RequestError):
    """Raised when request times out."""

    def __init__(
        self,
        message: str,
        request_id: Optional[str] = None,
        timeout: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, request_id, "REQUEST_TIMEOUT_ERROR", details)
        self.timeout = timeout


class CostLimitExceededError(LLMDispatcherError):
    """Raised when cost limits are exceeded."""

    def __init__(
        self,
        message: str,
        current_cost: float,
        limit: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "COST_LIMIT_EXCEEDED_ERROR", details)
        self.current_cost = current_cost
        self.limit = limit


class BudgetExceededError(LLMDispatcherError):
    """Raised when budget limits are exceeded."""

    def __init__(
        self,
        message: str,
        budget_type: str,
        current_usage: float,
        limit: float,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "BUDGET_EXCEEDED_ERROR", details)
        self.budget_type = budget_type
        self.current_usage = current_usage
        self.limit = limit


class FallbackExhaustedError(LLMDispatcherError):
    """Raised when all fallback options are exhausted."""

    def __init__(
        self,
        message: str,
        failed_providers: list,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, "FALLBACK_EXHAUSTED_ERROR", details)
        self.failed_providers = failed_providers


class NoAvailableProvidersError(LLMDispatcherError):
    """Raised when no providers are available."""

    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = "No providers are currently available"
        super().__init__(message, "NO_AVAILABLE_PROVIDERS_ERROR", details)


class CacheError(LLMDispatcherError):
    """Base exception for cache-related errors."""

    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.cache_key = cache_key


class CacheMissError(CacheError):
    """Raised when cache miss occurs (not necessarily an error, but can be used for monitoring)."""

    def __init__(
        self,
        cache_key: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Cache miss for key: {cache_key}"
        super().__init__(message, cache_key, "CACHE_MISS_ERROR", details)


class CacheStorageError(CacheError):
    """Raised when cache storage fails."""

    def __init__(
        self,
        cache_key: str,
        message: str = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if message is None:
            message = f"Cache storage failed for key: {cache_key}"
        super().__init__(message, cache_key, "CACHE_STORAGE_ERROR", details)


class SecurityError(LLMDispatcherError):
    """Base exception for security-related errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)


class ContentFilterError(SecurityError):
    """Raised when content is filtered due to security policies."""

    def __init__(
        self, message: str, filter_reason: str, details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, "CONTENT_FILTER_ERROR", details)
        self.filter_reason = filter_reason


class UnauthorizedAccessError(SecurityError):
    """Raised when access is unauthorized."""

    def __init__(self, message: str = None, details: Optional[Dict[str, Any]] = None):
        if message is None:
            message = "Unauthorized access"
        super().__init__(message, "UNAUTHORIZED_ACCESS_ERROR", details)


class BenchmarkError(LLMDispatcherError):
    """Base exception for benchmark-related errors."""

    def __init__(
        self,
        message: str,
        benchmark_type: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, error_code, details)
        self.benchmark_type = benchmark_type


class BenchmarkConfigurationError(BenchmarkError):
    """Raised when benchmark configuration is invalid."""

    def __init__(
        self,
        message: str,
        benchmark_type: Optional[str] = None,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, benchmark_type, "BENCHMARK_CONFIG_ERROR", details)
        self.config_key = config_key


class BenchmarkExecutionError(BenchmarkError):
    """Raised when benchmark execution fails."""

    def __init__(
        self,
        message: str,
        benchmark_type: Optional[str] = None,
        execution_step: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, benchmark_type, "BENCHMARK_EXECUTION_ERROR", details)
        self.execution_step = execution_step


class BenchmarkTimeoutError(BenchmarkError):
    """Raised when benchmark execution times out."""

    def __init__(
        self,
        message: str,
        benchmark_type: Optional[str] = None,
        timeout: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message, benchmark_type, "BENCHMARK_TIMEOUT_ERROR", details)
        self.timeout = timeout
