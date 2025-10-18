"""
Comprehensive tests for custom LLM-Dispatcher exceptions.

This module tests all custom exceptions to ensure they work correctly
and provide proper error information for debugging and error handling.
"""

import pytest
from llm_dispatcher.exceptions import (
    LLMDispatcherError,
    ProviderError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ProviderServiceUnavailableError,
    ModelError,
    ModelNotFoundError,
    ModelUnsupportedError,
    ModelContextLengthExceededError,
    ConfigurationError,
    InvalidConfigurationError,
    MissingConfigurationError,
    RequestError,
    InvalidRequestError,
    RequestTimeoutError,
    CostLimitExceededError,
    BudgetExceededError,
    FallbackExhaustedError,
    NoAvailableProvidersError,
    CacheError,
    CacheMissError,
    CacheStorageError,
    SecurityError,
    ContentFilterError,
    UnauthorizedAccessError,
)


class TestLLMDispatcherError:
    """Test the base LLM-Dispatcher error class."""

    def test_basic_initialization(self):
        """Test basic error initialization."""
        error = LLMDispatcherError("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.error_code is None
        assert error.details == {}

    def test_initialization_with_error_code(self):
        """Test initialization with error code."""
        error = LLMDispatcherError("Test error", error_code="TEST_ERROR")

        assert error.message == "Test error"
        assert error.error_code == "TEST_ERROR"
        assert error.details == {}

    def test_initialization_with_details(self):
        """Test initialization with details."""
        details = {"key": "value", "number": 123}
        error = LLMDispatcherError("Test error", details=details)

        assert error.message == "Test error"
        assert error.details == details

    def test_inheritance(self):
        """Test that it inherits from Exception."""
        error = LLMDispatcherError("Test error")
        assert isinstance(error, Exception)


class TestProviderErrors:
    """Test provider-related error classes."""

    def test_provider_error_basic(self):
        """Test basic ProviderError initialization."""
        error = ProviderError("Provider failed", "openai")

        assert error.message == "Provider failed"
        assert error.provider == "openai"
        assert error.error_code is None

    def test_provider_connection_error(self):
        """Test ProviderConnectionError."""
        error = ProviderConnectionError("openai")

        assert "openai" in error.message
        assert error.provider == "openai"
        assert error.error_code == "CONNECTION_ERROR"

    def test_provider_connection_error_custom_message(self):
        """Test ProviderConnectionError with custom message."""
        error = ProviderConnectionError("openai", "Custom connection message")

        assert error.message == "Custom connection message"
        assert error.provider == "openai"

    def test_provider_authentication_error(self):
        """Test ProviderAuthenticationError."""
        error = ProviderAuthenticationError("anthropic")

        assert "anthropic" in error.message
        assert error.provider == "anthropic"
        assert error.error_code == "AUTHENTICATION_ERROR"

    def test_provider_rate_limit_error(self):
        """Test ProviderRateLimitError."""
        error = ProviderRateLimitError("google", retry_after=60)

        assert "google" in error.message
        assert error.provider == "google"
        assert error.error_code == "RATE_LIMIT_ERROR"
        assert error.retry_after == 60

    def test_provider_quota_exceeded_error(self):
        """Test ProviderQuotaExceededError."""
        error = ProviderQuotaExceededError("grok")

        assert "grok" in error.message
        assert error.provider == "grok"
        assert error.error_code == "QUOTA_EXCEEDED_ERROR"

    def test_provider_timeout_error(self):
        """Test ProviderTimeoutError."""
        error = ProviderTimeoutError("openai", timeout=30.0)

        assert "openai" in error.message
        assert error.provider == "openai"
        assert error.error_code == "TIMEOUT_ERROR"
        assert error.timeout == 30.0

    def test_provider_service_unavailable_error(self):
        """Test ProviderServiceUnavailableError."""
        error = ProviderServiceUnavailableError("anthropic")

        assert "anthropic" in error.message
        assert error.provider == "anthropic"
        assert error.error_code == "SERVICE_UNAVAILABLE_ERROR"


class TestModelErrors:
    """Test model-related error classes."""

    def test_model_error_basic(self):
        """Test basic ModelError initialization."""
        error = ModelError("Model failed", "gpt-4", "openai")

        assert error.message == "Model failed"
        assert error.model == "gpt-4"
        assert error.provider == "openai"
        assert error.error_code is None

    def test_model_not_found_error(self):
        """Test ModelNotFoundError."""
        error = ModelNotFoundError("gpt-5", "openai")

        assert "gpt-5" in error.message
        assert "openai" in error.message
        assert error.model == "gpt-5"
        assert error.provider == "openai"
        assert error.error_code == "MODEL_NOT_FOUND_ERROR"

    def test_model_unsupported_error(self):
        """Test ModelUnsupportedError."""
        error = ModelUnsupportedError("gpt-3.5-turbo", "openai", "vision")

        assert "gpt-3.5-turbo" in error.message
        assert "openai" in error.message
        assert "vision" in error.message
        assert error.model == "gpt-3.5-turbo"
        assert error.provider == "openai"
        assert error.capability == "vision"
        assert error.error_code == "MODEL_UNSUPPORTED_ERROR"

    def test_model_context_length_exceeded_error(self):
        """Test ModelContextLengthExceededError."""
        error = ModelContextLengthExceededError("gpt-4", "openai", 10000, 8000)

        assert "gpt-4" in error.message
        assert "openai" in error.message
        assert "10000" in error.message
        assert "8000" in error.message
        assert error.model == "gpt-4"
        assert error.provider == "openai"
        assert error.requested_tokens == 10000
        assert error.max_tokens == 8000
        assert error.error_code == "CONTEXT_LENGTH_EXCEEDED_ERROR"


class TestConfigurationErrors:
    """Test configuration-related error classes."""

    def test_configuration_error_basic(self):
        """Test basic ConfigurationError initialization."""
        error = ConfigurationError("Config failed", config_key="api_key")

        assert error.message == "Config failed"
        assert error.config_key == "api_key"
        assert error.error_code is None

    def test_invalid_configuration_error(self):
        """Test InvalidConfigurationError."""
        error = InvalidConfigurationError("temperature", 2.5)

        assert "temperature" in error.message
        assert "2.5" in error.message
        assert error.config_key == "temperature"
        assert error.value == 2.5
        assert error.error_code == "INVALID_CONFIG_ERROR"

    def test_missing_configuration_error(self):
        """Test MissingConfigurationError."""
        error = MissingConfigurationError("api_key")

        assert "api_key" in error.message
        assert error.config_key == "api_key"
        assert error.error_code == "MISSING_CONFIG_ERROR"


class TestRequestErrors:
    """Test request-related error classes."""

    def test_request_error_basic(self):
        """Test basic RequestError initialization."""
        error = RequestError("Request failed", request_id="req_123")

        assert error.message == "Request failed"
        assert error.request_id == "req_123"
        assert error.error_code is None

    def test_invalid_request_error(self):
        """Test InvalidRequestError."""
        error = InvalidRequestError("Invalid prompt", request_id="req_456")

        assert error.message == "Invalid prompt"
        assert error.request_id == "req_456"
        assert error.error_code == "INVALID_REQUEST_ERROR"

    def test_request_timeout_error(self):
        """Test RequestTimeoutError."""
        error = RequestTimeoutError(
            "Request timed out", request_id="req_789", timeout=30.0
        )

        assert error.message == "Request timed out"
        assert error.request_id == "req_789"
        assert error.timeout == 30.0
        assert error.error_code == "REQUEST_TIMEOUT_ERROR"


class TestCostAndBudgetErrors:
    """Test cost and budget-related error classes."""

    def test_cost_limit_exceeded_error(self):
        """Test CostLimitExceededError."""
        error = CostLimitExceededError("Cost limit exceeded", 1.5, 1.0)

        assert error.message == "Cost limit exceeded"
        assert error.current_cost == 1.5
        assert error.limit == 1.0
        assert error.error_code == "COST_LIMIT_EXCEEDED_ERROR"

    def test_budget_exceeded_error(self):
        """Test BudgetExceededError."""
        error = BudgetExceededError("Daily budget exceeded", "daily", 100.0, 50.0)

        assert error.message == "Daily budget exceeded"
        assert error.budget_type == "daily"
        assert error.current_usage == 100.0
        assert error.limit == 50.0
        assert error.error_code == "BUDGET_EXCEEDED_ERROR"


class TestFallbackErrors:
    """Test fallback-related error classes."""

    def test_fallback_exhausted_error(self):
        """Test FallbackExhaustedError."""
        failed_providers = ["openai", "anthropic", "google"]
        error = FallbackExhaustedError("All fallbacks failed", failed_providers)

        assert error.message == "All fallbacks failed"
        assert error.failed_providers == failed_providers
        assert error.error_code == "FALLBACK_EXHAUSTED_ERROR"

    def test_no_available_providers_error(self):
        """Test NoAvailableProvidersError."""
        error = NoAvailableProvidersError()

        assert "No providers are currently available" in error.message
        assert error.error_code == "NO_AVAILABLE_PROVIDERS_ERROR"

    def test_no_available_providers_error_custom_message(self):
        """Test NoAvailableProvidersError with custom message."""
        error = NoAvailableProvidersError("All providers are down")

        assert error.message == "All providers are down"
        assert error.error_code == "NO_AVAILABLE_PROVIDERS_ERROR"


class TestCacheErrors:
    """Test cache-related error classes."""

    def test_cache_error_basic(self):
        """Test basic CacheError initialization."""
        error = CacheError("Cache failed", cache_key="key_123")

        assert error.message == "Cache failed"
        assert error.cache_key == "key_123"
        assert error.error_code is None

    def test_cache_miss_error(self):
        """Test CacheMissError."""
        error = CacheMissError("cache_key_456")

        assert "cache_key_456" in error.message
        assert error.cache_key == "cache_key_456"
        assert error.error_code == "CACHE_MISS_ERROR"

    def test_cache_storage_error(self):
        """Test CacheStorageError."""
        error = CacheStorageError("cache_key_789")

        assert "cache_key_789" in error.message
        assert error.cache_key == "cache_key_789"
        assert error.error_code == "CACHE_STORAGE_ERROR"


class TestSecurityErrors:
    """Test security-related error classes."""

    def test_security_error_basic(self):
        """Test basic SecurityError initialization."""
        error = SecurityError("Security violation")

        assert error.message == "Security violation"
        assert error.error_code is None

    def test_content_filter_error(self):
        """Test ContentFilterError."""
        error = ContentFilterError("Content blocked", "inappropriate_content")

        assert error.message == "Content blocked"
        assert error.filter_reason == "inappropriate_content"
        assert error.error_code == "CONTENT_FILTER_ERROR"

    def test_unauthorized_access_error(self):
        """Test UnauthorizedAccessError."""
        error = UnauthorizedAccessError()

        assert error.message == "Unauthorized access"
        assert error.error_code == "UNAUTHORIZED_ACCESS_ERROR"

    def test_unauthorized_access_error_custom_message(self):
        """Test UnauthorizedAccessError with custom message."""
        error = UnauthorizedAccessError("API key invalid")

        assert error.message == "API key invalid"
        assert error.error_code == "UNAUTHORIZED_ACCESS_ERROR"


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_inheritance_hierarchy(self):
        """Test that all exceptions inherit from the correct base classes."""
        # Test base inheritance
        assert issubclass(ProviderError, LLMDispatcherError)
        assert issubclass(ModelError, LLMDispatcherError)
        assert issubclass(ConfigurationError, LLMDispatcherError)
        assert issubclass(RequestError, LLMDispatcherError)
        assert issubclass(CacheError, LLMDispatcherError)
        assert issubclass(SecurityError, LLMDispatcherError)

        # Test specific provider errors
        assert issubclass(ProviderConnectionError, ProviderError)
        assert issubclass(ProviderAuthenticationError, ProviderError)
        assert issubclass(ProviderRateLimitError, ProviderError)
        assert issubclass(ProviderQuotaExceededError, ProviderError)
        assert issubclass(ProviderTimeoutError, ProviderError)
        assert issubclass(ProviderServiceUnavailableError, ProviderError)

        # Test specific model errors
        assert issubclass(ModelNotFoundError, ModelError)
        assert issubclass(ModelUnsupportedError, ModelError)
        assert issubclass(ModelContextLengthExceededError, ModelError)

        # Test specific configuration errors
        assert issubclass(InvalidConfigurationError, ConfigurationError)
        assert issubclass(MissingConfigurationError, ConfigurationError)

        # Test specific request errors
        assert issubclass(InvalidRequestError, RequestError)
        assert issubclass(RequestTimeoutError, RequestError)

        # Test specific cache errors
        assert issubclass(CacheMissError, CacheError)
        assert issubclass(CacheStorageError, CacheError)

        # Test specific security errors
        assert issubclass(ContentFilterError, SecurityError)
        assert issubclass(UnauthorizedAccessError, SecurityError)


class TestExceptionDetails:
    """Test exception details and attributes."""

    def test_exception_details_preservation(self):
        """Test that exception details are properly preserved."""
        details = {"provider": "openai", "model": "gpt-4", "tokens": 1000, "cost": 0.05}

        error = LLMDispatcherError("Test error", details=details)
        assert error.details == details

    def test_exception_details_modification(self):
        """Test that exception details can be modified."""
        error = LLMDispatcherError("Test error")
        error.details["new_key"] = "new_value"

        assert error.details["new_key"] == "new_value"

    def test_exception_string_representation(self):
        """Test string representation of exceptions."""
        error = ProviderError("Provider failed", "openai", "PROVIDER_ERROR")

        # Should be able to convert to string
        str_repr = str(error)
        assert "Provider failed" in str_repr

        # Should be able to use in f-strings
        f_string = f"Error: {error}"
        assert "Provider failed" in f_string


class TestExceptionChaining:
    """Test exception chaining and cause preservation."""

    def test_exception_chaining(self):
        """Test that exceptions can be chained with their causes."""
        original_error = ValueError("Original error")

        try:
            raise original_error
        except ValueError as e:
            dispatcher_error = ProviderError("Provider failed", "openai")
            dispatcher_error.__cause__ = e

            assert dispatcher_error.__cause__ == original_error

    def test_exception_context(self):
        """Test exception context preservation."""
        try:
            raise ValueError("Original error")
        except ValueError:
            dispatcher_error = ModelError("Model failed", "gpt-4", "openai")
            dispatcher_error.__context__ = sys.exception()

            assert dispatcher_error.__context__ is not None


class TestExceptionUsage:
    """Test practical usage patterns of exceptions."""

    def test_exception_in_try_except(self):
        """Test using exceptions in try-except blocks."""
        try:
            raise ProviderConnectionError("openai")
        except ProviderError as e:
            assert e.provider == "openai"
            assert e.error_code == "CONNECTION_ERROR"
        except Exception:
            pytest.fail("Should have caught ProviderError")

    def test_exception_inheritance_in_catching(self):
        """Test that base exceptions can catch derived exceptions."""
        try:
            raise ModelNotFoundError("gpt-5", "openai")
        except ModelError as e:
            assert e.model == "gpt-5"
            assert e.provider == "openai"
        except Exception:
            pytest.fail("Should have caught ModelError")

    def test_multiple_exception_types(self):
        """Test handling multiple exception types."""
        exceptions = [
            ProviderConnectionError("openai"),
            ModelNotFoundError("gpt-5", "openai"),
            ConfigurationError("Invalid config"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except LLMDispatcherError as e:
                assert isinstance(e, LLMDispatcherError)
            except Exception:
                pytest.fail(f"Should have caught {type(exc).__name__}")


# Import sys for exception context testing
import sys
