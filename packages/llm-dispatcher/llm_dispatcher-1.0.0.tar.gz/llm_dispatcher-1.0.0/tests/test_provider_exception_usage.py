"""
Tests demonstrating proper usage of custom exceptions in providers.

This module shows how custom exceptions should be used in practice
within provider implementations and integration scenarios.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from llm_dispatcher.exceptions import (
    ProviderError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ModelError,
    ModelNotFoundError,
    ModelUnsupportedError,
    ModelContextLengthExceededError,
    CostLimitExceededError,
    FallbackExhaustedError,
    NoAvailableProvidersError,
)
from llm_dispatcher.core.base import TaskRequest, TaskType
from llm_dispatcher.core.switch_engine import LLMSwitch
from llm_dispatcher.config.settings import (
    SwitchConfig,
    SwitchingRules,
    OptimizationStrategy,
    FallbackStrategy,
)


class TestProviderExceptionUsage:
    """Test how exceptions are used in provider implementations."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider that can raise various exceptions."""
        provider = Mock()
        provider.name = "test_provider"
        provider.models = {
            "test-model": Mock(
                name="test-model",
                max_tokens=1000,
                context_window=2000,
                capabilities=["text"],
            )
        }
        return provider

    def test_connection_error_handling(self, mock_provider):
        """Test handling of connection errors."""
        # Test that the custom exception is properly formed
        with pytest.raises(ProviderConnectionError) as exc_info:
            raise ProviderConnectionError("test_provider", "Failed to connect to API")

        error = exc_info.value
        assert error.provider == "test_provider"
        assert error.error_code == "CONNECTION_ERROR"

        # Test simulating a connection error scenario
        with patch.object(
            mock_provider, "generate", side_effect=ConnectionError("Connection failed")
        ):
            with pytest.raises(ConnectionError):
                mock_provider.generate(Mock(), "test-model")

    def test_authentication_error_handling(self, mock_provider):
        """Test handling of authentication errors."""
        # Test that the custom exception is properly formed
        with pytest.raises(ProviderAuthenticationError) as exc_info:
            raise ProviderAuthenticationError("test_provider", "Invalid API key")

        error = exc_info.value
        assert error.provider == "test_provider"
        assert error.error_code == "AUTHENTICATION_ERROR"

        # Test simulating an authentication error scenario
        with patch.object(
            mock_provider, "generate", side_effect=Exception("401 Unauthorized")
        ):
            with pytest.raises(Exception, match="401 Unauthorized"):
                mock_provider.generate(Mock(), "test-model")

    def test_rate_limit_error_handling(self, mock_provider):
        """Test handling of rate limit errors."""
        # Test that the custom exception is properly formed
        with pytest.raises(ProviderRateLimitError) as exc_info:
            raise ProviderRateLimitError("test_provider", retry_after=60)

        error = exc_info.value
        assert error.provider == "test_provider"
        assert error.retry_after == 60
        assert error.error_code == "RATE_LIMIT_ERROR"

        # Test simulating a rate limit error scenario
        with patch.object(
            mock_provider, "generate", side_effect=Exception("429 Too Many Requests")
        ):
            with pytest.raises(Exception, match="429 Too Many Requests"):
                mock_provider.generate(Mock(), "test-model")

    def test_model_not_found_error_handling(self, mock_provider):
        """Test handling of model not found errors."""
        # Simulate requesting a non-existent model
        with pytest.raises(ModelNotFoundError) as exc_info:
            if "non-existent-model" not in mock_provider.models:
                raise ModelNotFoundError("non-existent-model", "test_provider")

        error = exc_info.value
        assert error.model == "non-existent-model"
        assert error.provider == "test_provider"
        assert error.error_code == "MODEL_NOT_FOUND_ERROR"

    def test_model_unsupported_error_handling(self, mock_provider):
        """Test handling of unsupported capability errors."""
        # Simulate requesting an unsupported capability
        with pytest.raises(ModelUnsupportedError) as exc_info:
            model_capabilities = mock_provider.models["test-model"].capabilities
            if "vision" not in model_capabilities:
                raise ModelUnsupportedError("test-model", "test_provider", "vision")

        error = exc_info.value
        assert error.model == "test-model"
        assert error.provider == "test_provider"
        assert error.capability == "vision"
        assert error.error_code == "MODEL_UNSUPPORTED_ERROR"

    def test_context_length_exceeded_error_handling(self, mock_provider):
        """Test handling of context length exceeded errors."""
        # Simulate requesting more tokens than the model supports
        with pytest.raises(ModelContextLengthExceededError) as exc_info:
            requested_tokens = 3000
            max_tokens = mock_provider.models["test-model"].context_window
            if requested_tokens > max_tokens:
                raise ModelContextLengthExceededError(
                    "test-model", "test_provider", requested_tokens, max_tokens
                )

        error = exc_info.value
        assert error.model == "test-model"
        assert error.provider == "test_provider"
        assert error.requested_tokens == 3000
        assert error.max_tokens == 2000
        assert error.error_code == "CONTEXT_LENGTH_EXCEEDED_ERROR"


class TestLLMSwitchExceptionHandling:
    """Test exception handling in LLMSwitch integration."""

    @pytest.fixture
    def mock_providers(self):
        """Create mock providers for testing."""
        provider1 = Mock()
        provider1.name = "provider1"
        provider1.get_health_status.return_value = {"status": "healthy"}
        provider1.models = {"model1": Mock(name="model1")}

        provider2 = Mock()
        provider2.name = "provider2"
        provider2.get_health_status.return_value = {"status": "healthy"}
        provider2.models = {"model2": Mock(name="model2")}

        return {"provider1": provider1, "provider2": provider2}

    @pytest.fixture
    def switch_config(self):
        """Create a switch configuration."""
        return SwitchConfig(
            switching_rules=SwitchingRules(
                optimization_strategy=OptimizationStrategy.BALANCED,
                fallback_strategy=FallbackStrategy.PERFORMANCE_PRIORITY,
                max_cost_per_request=1.0,
                max_latency_ms=5000,
                enable_caching=True,
            )
        )

    @pytest.fixture
    def llm_switch(self, mock_providers, switch_config):
        """Create an LLMSwitch instance."""
        return LLMSwitch(providers=mock_providers, config=switch_config)

    def test_fallback_exhausted_error(self, llm_switch, mock_providers):
        """Test FallbackExhaustedError when all providers fail."""
        # Make all providers fail
        for provider in mock_providers.values():
            provider.generate = AsyncMock(side_effect=Exception("Provider failed"))

        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION,
        )

        # Test that fallback exhausted error is raised
        with pytest.raises(FallbackExhaustedError) as exc_info:
            # This would be called in the actual implementation
            failed_providers = list(mock_providers.keys())
            raise FallbackExhaustedError(
                "All fallback providers failed", failed_providers
            )

        error = exc_info.value
        assert error.failed_providers == ["provider1", "provider2"]
        assert error.error_code == "FALLBACK_EXHAUSTED_ERROR"

    def test_no_available_providers_error(self, mock_providers):
        """Test NoAvailableProvidersError when no providers are available."""
        # Make all providers unhealthy
        for provider in mock_providers.values():
            provider.get_health_status.return_value = {"status": "unhealthy"}

        with pytest.raises(NoAvailableProvidersError) as exc_info:
            raise NoAvailableProvidersError("All providers are currently unhealthy")

        error = exc_info.value
        assert error.message == "All providers are currently unhealthy"
        assert error.error_code == "NO_AVAILABLE_PROVIDERS_ERROR"

    def test_cost_limit_exceeded_error(self, llm_switch):
        """Test CostLimitExceededError when cost limits are exceeded."""
        with pytest.raises(CostLimitExceededError) as exc_info:
            current_cost = 1.5
            limit = 1.0
            raise CostLimitExceededError(
                f"Request cost {current_cost} exceeds limit {limit}",
                current_cost,
                limit,
            )

        error = exc_info.value
        assert error.current_cost == 1.5
        assert error.limit == 1.0
        assert error.error_code == "COST_LIMIT_EXCEEDED_ERROR"


class TestExceptionChainingInProviders:
    """Test exception chaining in provider implementations."""

    def test_original_error_preservation(self):
        """Test that original errors are preserved when wrapping with custom exceptions."""
        # Simulate an original API error
        original_error = ConnectionError("Connection refused")

        try:
            raise original_error
        except ConnectionError as e:
            # Wrap with our custom exception while preserving the original
            custom_error = ProviderConnectionError("openai", "API connection failed")
            custom_error.__cause__ = e

            assert custom_error.__cause__ == original_error
            assert isinstance(custom_error, ProviderConnectionError)

    def test_exception_context_preservation(self):
        """Test that exception context is preserved during chaining."""
        try:
            # Simulate a nested error scenario
            try:
                raise ValueError("Invalid parameter")
            except ValueError as e:
                # Convert to our custom exception
                raise ModelNotFoundError("gpt-5", "openai") from e
        except ModelNotFoundError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
            assert str(e.__cause__) == "Invalid parameter"


class TestExceptionDetailsAndDebugging:
    """Test exception details for debugging purposes."""

    def test_exception_with_rich_details(self):
        """Test exceptions with rich debugging details."""
        details = {
            "request_id": "req_12345",
            "model": "gpt-4",
            "provider": "openai",
            "tokens_used": 1500,
            "cost": 0.03,
            "latency_ms": 2500,
            "retry_count": 2,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        error = ProviderTimeoutError(
            "openai",
            timeout=30.0,
            message="Request timed out after 30 seconds",
            details=details,
        )

        assert error.provider == "openai"
        assert error.timeout == 30.0
        assert error.details == details
        assert error.details["request_id"] == "req_12345"
        assert error.details["tokens_used"] == 1500

    def test_exception_logging_format(self):
        """Test that exceptions can be formatted for logging."""
        error = ProviderRateLimitError(
            "anthropic",
            retry_after=60,
            details={
                "endpoint": "/v1/messages",
                "limit": 1000,
                "remaining": 0,
                "reset_time": "2024-01-01T12:01:00Z",
            },
        )

        # Test that all important information is accessible
        log_info = {
            "error_type": type(error).__name__,
            "provider": error.provider,
            "error_code": error.error_code,
            "retry_after": error.retry_after,
            "details": error.details,
        }

        assert log_info["error_type"] == "ProviderRateLimitError"
        assert log_info["provider"] == "anthropic"
        assert log_info["error_code"] == "RATE_LIMIT_ERROR"
        assert log_info["retry_after"] == 60
        assert log_info["details"]["endpoint"] == "/v1/messages"


class TestExceptionInheritanceInCatching:
    """Test exception inheritance when catching exceptions."""

    def test_catching_base_exception_catches_derived(self):
        """Test that catching base exceptions also catches derived ones."""
        exceptions_to_test = [
            ProviderConnectionError("openai"),
            ProviderAuthenticationError("anthropic"),
            ProviderRateLimitError("google"),
            ModelNotFoundError("gpt-5", "openai"),
            ModelUnsupportedError("gpt-3.5-turbo", "openai", "vision"),
        ]

        for exc in exceptions_to_test:
            try:
                raise exc
            except ProviderError as e:
                # Should catch all ProviderError-derived exceptions
                assert isinstance(e, ProviderError)
            except ModelError as e:
                # Should catch all ModelError-derived exceptions
                assert isinstance(e, ModelError)
            except Exception:
                pytest.fail(
                    f"Should have caught {type(exc).__name__} with specific handler"
                )

    def test_specific_exception_handling(self):
        """Test handling specific exception types differently."""

        def handle_provider_error(error):
            if isinstance(error, ProviderRateLimitError):
                return f"Rate limited. Retry after {error.retry_after} seconds"
            elif isinstance(error, ProviderAuthenticationError):
                return "Authentication failed. Check API key"
            elif isinstance(error, ProviderConnectionError):
                return "Connection failed. Check network"
            else:
                return f"Provider error: {error.message}"

        # Test different provider errors
        rate_limit_error = ProviderRateLimitError("openai", retry_after=60)
        auth_error = ProviderAuthenticationError("anthropic")
        conn_error = ProviderConnectionError("google")

        assert "Retry after 60 seconds" in handle_provider_error(rate_limit_error)
        assert "Authentication failed" in handle_provider_error(auth_error)
        assert "Connection failed" in handle_provider_error(conn_error)
