"""
Base classes and interfaces for LLM providers and core functionality.

This module defines the fundamental data structures and interfaces used throughout
the LLM-Dispatcher package, including task types, capabilities, and provider interfaces.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union, AsyncGenerator, Type
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime


class TaskType(str, Enum):
    """Enumeration of supported task types."""

    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CLASSIFICATION = "classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    VISION_ANALYSIS = "vision_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    STRUCTURED_OUTPUT = "structured_output"
    FUNCTION_CALLING = "function_calling"
    REASONING = "reasoning"
    MATH = "math"


class Capability(str, Enum):
    """Enumeration of LLM capabilities."""

    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"
    CODE = "code"
    MATH = "math"
    REASONING = "reasoning"


class ModelInfo(BaseModel):
    """Information about a specific model."""

    name: str
    provider: str
    capabilities: List[Capability]
    max_tokens: int
    cost_per_1k_tokens: Dict[str, float] = Field(default_factory=dict)  # input/output
    context_window: int
    latency_ms: Optional[float] = None
    benchmark_scores: Dict[str, float] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    """Request structure for LLM tasks."""

    prompt: str
    task_type: TaskType
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    images: Optional[List[str]] = None  # Base64 encoded images
    audio: Optional[str] = None  # Base64 encoded audio
    structured_output: Optional[Union[Dict[str, Any], Type[BaseModel]]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response structure from LLM tasks."""

    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: float
    finish_reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class PerformanceMetrics(BaseModel):
    """Performance metrics for LLM evaluation based on credible benchmarks."""

    # General Intelligence Benchmarks
    mmlu_score: Optional[float] = None  # Massive Multitask Language Understanding
    hellaswag_score: Optional[float] = None  # Common sense reasoning
    arc_score: Optional[float] = None  # AI2 Reasoning Challenge

    # Specialized Task Benchmarks
    human_eval_score: Optional[float] = None  # Code generation
    gpqa_score: Optional[float] = None  # Graduate-level reasoning
    aime_score: Optional[float] = None  # Mathematical problem-solving
    truthfulqa_score: Optional[float] = None  # Truthfulness evaluation

    # Multimodal Benchmarks
    vqa_score: Optional[float] = None  # Visual Question Answering
    speech_recognition_score: Optional[float] = None  # Audio processing

    # Performance Metrics
    latency_ms: Optional[float] = None
    cost_efficiency: Optional[float] = None  # Score per dollar
    reliability_score: Optional[float] = None  # Success rate

    def get_task_score(self, task_type: TaskType) -> float:
        """Get weighted score for a specific task type."""
        task_weights = {
            TaskType.REASONING: {
                "gpqa_score": 0.4,
                "mmlu_score": 0.3,
                "hellaswag_score": 0.3,
            },
            TaskType.MATH: {"aime_score": 0.5, "mmlu_score": 0.3, "gpqa_score": 0.2},
            TaskType.CODE_GENERATION: {
                "human_eval_score": 0.6,
                "mmlu_score": 0.2,
                "gpqa_score": 0.2,
            },
            TaskType.VISION_ANALYSIS: {"vqa_score": 0.7, "mmlu_score": 0.3},
            TaskType.TEXT_GENERATION: {
                "mmlu_score": 0.4,
                "hellaswag_score": 0.3,
                "truthfulqa_score": 0.3,
            },
            TaskType.QUESTION_ANSWERING: {
                "mmlu_score": 0.5,
                "arc_score": 0.3,
                "hellaswag_score": 0.2,
            },
            TaskType.CLASSIFICATION: {"mmlu_score": 0.6, "hellaswag_score": 0.4},
            TaskType.SUMMARIZATION: {
                "mmlu_score": 0.5,
                "hellaswag_score": 0.3,
                "truthfulqa_score": 0.2,
            },
        }

        weights = task_weights.get(task_type, {"mmlu_score": 1.0})
        score = 0.0

        for metric, weight in weights.items():
            value = getattr(self, metric, 0.0) or 0.0
            score += value * weight

        return min(score, 1.0)  # Normalize to 0-1 range


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self.models: Dict[str, ModelInfo] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        self._initialize_models()
        self._initialize_performance_metrics()

    @abstractmethod
    def _initialize_models(self) -> None:
        """Initialize available models and their capabilities."""
        pass

    def _initialize_performance_metrics(self) -> None:
        """Initialize performance metrics for each model."""
        # This will be overridden by specific providers with real benchmark data
        # Default implementation - do nothing
        pass

    @abstractmethod
    async def generate(self, request: TaskRequest, model: str) -> TaskResponse:
        """Generate a response for the given request."""
        pass

    @abstractmethod
    async def generate_stream(
        self, request: TaskRequest, model: str
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        pass

    @abstractmethod
    async def get_embeddings(self, text: str, model: str) -> List[float]:
        """Get embeddings for the given text."""
        pass

    def get_models_for_task(self, task_type: TaskType) -> List[str]:
        """Get models suitable for the given task type."""
        suitable_models = []
        for model_name, model_info in self.models.items():
            if self._is_model_suitable_for_task(model_info, task_type):
                suitable_models.append(model_name)
        return suitable_models

    def _is_model_suitable_for_task(
        self, model_info: ModelInfo, task_type: TaskType
    ) -> bool:
        """Check if a model is suitable for a specific task type."""
        capability_mapping = {
            TaskType.TEXT_GENERATION: [Capability.TEXT],
            TaskType.CODE_GENERATION: [Capability.CODE, Capability.TEXT],
            TaskType.VISION_ANALYSIS: [Capability.VISION],
            TaskType.AUDIO_TRANSCRIPTION: [Capability.AUDIO],
            TaskType.STRUCTURED_OUTPUT: [Capability.STRUCTURED_OUTPUT, Capability.TEXT],
            TaskType.FUNCTION_CALLING: [Capability.FUNCTION_CALLING, Capability.TEXT],
            TaskType.REASONING: [Capability.REASONING, Capability.TEXT],
            TaskType.MATH: [Capability.MATH, Capability.TEXT],
            TaskType.QUESTION_ANSWERING: [Capability.TEXT],
            TaskType.CLASSIFICATION: [Capability.TEXT],
            TaskType.SUMMARIZATION: [Capability.TEXT],
            TaskType.TRANSLATION: [Capability.TEXT],
            TaskType.SENTIMENT_ANALYSIS: [Capability.TEXT],
        }

        required_capabilities = capability_mapping.get(task_type, [Capability.TEXT])
        return any(cap in model_info.capabilities for cap in required_capabilities)

    def get_performance_score(self, model: str, task_type: TaskType) -> float:
        """Get performance score for a model on a specific task type."""
        if model not in self.performance_metrics:
            return 0.0

        metrics = self.performance_metrics[model]
        return metrics.get_task_score(task_type)

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request."""
        if model not in self.models:
            return 0.0

        model_info = self.models[model]
        input_cost = model_info.cost_per_1k_tokens.get("input", 0.0)
        output_cost = model_info.cost_per_1k_tokens.get("output", 0.0)

        return (input_tokens / 1000 * input_cost) + (output_tokens / 1000 * output_cost)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (basic implementation)."""
        # This is a simplified estimation - in practice, use tiktoken or similar
        return int(len(text.split()) * 1.3)  # Rough approximation

    def get_model_info(self, model: str) -> Optional[ModelInfo]:
        """Get model information."""
        return self.models.get(model)

    def get_performance_metrics(self, model: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics for a model."""
        return self.performance_metrics.get(model)
