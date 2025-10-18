"""
Base provider implementation with common functionality.

This module provides a base implementation of the LLMProvider interface
with common functionality that can be shared across different providers.
"""

import asyncio
import time
from typing import Dict, List, Optional, AsyncGenerator, Any
from datetime import datetime
import logging

from ..core.base import (
    LLMProvider,
    TaskRequest,
    TaskResponse,
    TaskType,
    ModelInfo,
    PerformanceMetrics,
    Capability,
)
from ..utils.benchmark_manager import BenchmarkManager
from ..utils.token_counter import token_counter

logger = logging.getLogger(__name__)


class BaseProvider(LLMProvider):
    """
    Base implementation of LLMProvider with common functionality.

    This class provides shared functionality for all LLM providers including
    performance tracking, error handling, and common utility methods.
    """

    def __init__(self, api_key: str, provider_name: str, **kwargs):
        # Initialize benchmark manager first
        self.benchmark_manager = BenchmarkManager()
        self.provider_name = provider_name
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0

        # Call parent constructor (this will call _initialize_models and _initialize_performance_metrics)
        super().__init__(api_key, **kwargs)

    def _initialize_performance_metrics(self) -> None:
        """Initialize performance metrics from benchmark data."""
        for model_name in self.models.keys():
            metrics = self.benchmark_manager.get_performance_metrics(model_name)
            if metrics:
                self.performance_metrics[model_name] = metrics

    async def generate(self, request: TaskRequest, model: str) -> TaskResponse:
        """Generate a response for the given request."""
        start_time = time.time()

        try:
            # Validate request
            self._validate_request(request, model)

            # Estimate tokens
            input_tokens = token_counter.count_tokens(
                request.prompt, self.provider_name
            )
            estimated_output_tokens = self._estimate_output_tokens(request)

            # Make the actual API call
            response_content = await self._make_api_call(request, model)

            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            output_tokens = token_counter.count_tokens(
                response_content, self.provider_name
            )
            total_tokens = input_tokens + output_tokens
            cost = self.estimate_cost(model, input_tokens, output_tokens)

            # Update statistics
            self._update_statistics(latency_ms, True)

            return TaskResponse(
                content=response_content,
                model_used=model,
                provider=self.provider_name,
                tokens_used=total_tokens,
                cost=cost,
                latency_ms=latency_ms,
                finish_reason="stop",
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "request_id": f"{self.provider_name}_{self.request_count}",
                    "timestamp": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_statistics(latency_ms, False)
            logger.error(f"Error in {self.provider_name} provider: {e}")
            raise

    async def generate_stream(
        self, request: TaskRequest, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        start_time = time.time()

        try:
            # Validate request
            self._validate_request(request, model)

            # Make streaming API call
            async for chunk in self._make_streaming_api_call(request, model):
                yield chunk

            # Update statistics
            latency_ms = (time.time() - start_time) * 1000
            self._update_statistics(latency_ms, True)

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            self._update_statistics(latency_ms, False)
            logger.error(f"Error in {self.provider_name} streaming: {e}")
            raise

    async def get_embeddings(self, text: str, model: str) -> List[float]:
        """Get embeddings for the given text."""
        try:
            return await self._make_embeddings_call(text, model)
        except Exception as e:
            logger.error(f"Error getting embeddings from {self.provider_name}: {e}")
            raise

    def _validate_request(self, request: TaskRequest, model: str) -> None:
        """Validate the request and model."""
        if model not in self.models:
            raise ValueError(
                f"Model {model} not available for provider {self.provider_name}"
            )

        model_info = self.models[model]

        # Check if model supports the task type
        if not self._is_model_suitable_for_task(model_info, request.task_type):
            raise ValueError(
                f"Model {model} does not support task type {request.task_type}"
            )

        # Check context window
        input_tokens = token_counter.count_tokens(request.prompt, self.provider_name)
        if input_tokens > model_info.context_window:
            raise ValueError(
                f"Input tokens ({input_tokens}) exceed context window "
                f"({model_info.context_window}) for model {model}"
            )

        # Check if model supports required capabilities
        if request.images and Capability.VISION not in model_info.capabilities:
            raise ValueError(f"Model {model} does not support vision tasks")

        if request.audio and Capability.AUDIO not in model_info.capabilities:
            raise ValueError(f"Model {model} does not support audio tasks")

        if (
            request.functions
            and Capability.FUNCTION_CALLING not in model_info.capabilities
        ):
            raise ValueError(f"Model {model} does not support function calling")

        if (
            request.structured_output
            and Capability.STRUCTURED_OUTPUT not in model_info.capabilities
        ):
            raise ValueError(f"Model {model} does not support structured output")

    def _estimate_output_tokens(self, request: TaskRequest) -> int:
        """Estimate output token count based on request."""
        # Simple estimation based on task type and max_tokens
        if request.max_tokens:
            return request.max_tokens

        # Default estimates by task type
        task_estimates = {
            TaskType.TEXT_GENERATION: 200,
            TaskType.CODE_GENERATION: 300,
            TaskType.SUMMARIZATION: 100,
            TaskType.TRANSLATION: 150,
            TaskType.QUESTION_ANSWERING: 100,
            TaskType.CLASSIFICATION: 50,
            TaskType.SENTIMENT_ANALYSIS: 50,
            TaskType.VISION_ANALYSIS: 200,
            TaskType.AUDIO_TRANSCRIPTION: 100,
            TaskType.STRUCTURED_OUTPUT: 150,
            TaskType.FUNCTION_CALLING: 200,
            TaskType.REASONING: 300,
            TaskType.MATH: 200,
        }

        return task_estimates.get(request.task_type, 200)

    def _update_statistics(self, latency_ms: float, success: bool) -> None:
        """Update provider statistics."""
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.total_latency += latency_ms

    def get_statistics(self) -> Dict[str, Any]:
        """Get provider statistics."""
        success_rate = (
            (self.request_count - self.error_count) / self.request_count
            if self.request_count > 0
            else 0.0
        )
        avg_latency = (
            self.total_latency / self.request_count if self.request_count > 0 else 0.0
        )

        return {
            "provider": self.provider_name,
            "total_requests": self.request_count,
            "successful_requests": self.request_count - self.error_count,
            "failed_requests": self.error_count,
            "success_rate": success_rate,
            "average_latency_ms": avg_latency,
            "total_latency_ms": self.total_latency,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Get provider health status."""
        stats = self.get_statistics()

        # Determine health status
        if stats["success_rate"] < 0.9:
            status = "critical"
        elif stats["success_rate"] < 0.95:
            status = "warning"
        else:
            status = "healthy"

        return {
            "status": status,
            "statistics": stats,
            "available_models": list(self.models.keys()),
            "capabilities": self._get_all_capabilities(),
        }

    def _get_all_capabilities(self) -> List[Capability]:
        """Get all capabilities supported by this provider."""
        all_capabilities = set()
        for model_info in self.models.values():
            all_capabilities.update(model_info.capabilities)
        return list(all_capabilities)

    # Abstract methods that must be implemented by subclasses
    async def _make_api_call(self, request: TaskRequest, model: str) -> str:
        """Make the actual API call to the provider."""
        raise NotImplementedError("Subclasses must implement _make_api_call")

    async def _make_streaming_api_call(
        self, request: TaskRequest, model: str
    ) -> AsyncGenerator[str, None]:
        """Make a streaming API call to the provider."""
        raise NotImplementedError("Subclasses must implement _make_streaming_api_call")

    async def _make_embeddings_call(self, text: str, model: str) -> List[float]:
        """Make an embeddings API call to the provider."""
        raise NotImplementedError("Subclasses must implement _make_embeddings_call")
