# LLM-Dispatcher API Reference

This document provides comprehensive API reference for LLM-Dispatcher.

## Core Classes

### LLMSwitch

The main switching engine that intelligently selects LLMs based on various factors.

```python
class LLMSwitch:
    def __init__(
        self,
        providers: List[LLMProvider],
        config: Optional[SwitchConfig] = None
    )
```

#### Methods

##### `execute_with_fallback(request: TaskRequest, constraints: Optional[Dict] = None) -> TaskResponse`

Execute a request with automatic fallback if the primary LLM fails.

**Parameters:**

- `request` (TaskRequest): The task request to execute
- `constraints` (Optional[Dict]): Additional constraints for LLM selection

**Returns:**

- `TaskResponse`: The response from the selected LLM

**Example:**

```python
request = TaskRequest(
    prompt="Explain machine learning",
    task_type=TaskType.TEXT_GENERATION
)
response = await switch.execute_with_fallback(request)
```

##### `execute_stream(request: TaskRequest, chunk_callback: Optional[callable] = None, metadata_callback: Optional[callable] = None) -> AsyncGenerator[str, None]`

Execute a request with streaming response.

**Parameters:**

- `request` (TaskRequest): The task request to execute
- `chunk_callback` (Optional[callable]): Callback for processing chunks
- `metadata_callback` (Optional[callable]): Callback for receiving metadata

**Returns:**

- `AsyncGenerator[str, None]`: Streaming response chunks

**Example:**

```python
async for chunk in switch.execute_stream(request):
    print(chunk, end="", flush=True)
```

##### `execute_stream_with_metadata(request: TaskRequest, include_timing: bool = True, include_tokens: bool = True) -> AsyncGenerator[Dict[str, Any], None]`

Execute streaming request with detailed metadata.

**Parameters:**

- `request` (TaskRequest): The task request to execute
- `include_timing` (bool): Whether to include timing information
- `include_tokens` (bool): Whether to include token estimation

**Returns:**

- `AsyncGenerator[Dict[str, Any], None]`: Streaming response with metadata

**Example:**

```python
async for metadata in switch.execute_stream_with_metadata(request):
    if metadata["chunk"] is None:  # End of stream
        break
    print(f"Chunk {metadata['chunk_index']}: {metadata['chunk']}")
```

##### `select_llm(request: TaskRequest, constraints: Optional[Dict] = None) -> SwitchDecision`

Select the best LLM for a request without executing it.

**Parameters:**

- `request` (TaskRequest): The task request
- `constraints` (Optional[Dict]): Additional constraints

**Returns:**

- `SwitchDecision`: Decision about which LLM to use

**Example:**

```python
decision = switch.select_llm(request)
print(f"Selected: {decision.provider}:{decision.model}")
print(f"Confidence: {decision.confidence:.2f}")
```

##### `get_system_status() -> Dict[str, Any]`

Get overall system status and health.

**Returns:**

- `Dict[str, Any]`: System status information

**Example:**

```python
status = switch.get_system_status()
print(f"Total providers: {status['total_providers']}")
print(f"Enabled providers: {status['enabled_providers']}")
```

##### `update_config(new_config: SwitchConfig) -> None`

Update the configuration.

**Parameters:**

- `new_config` (SwitchConfig): New configuration

##### `get_decision_weights() -> Dict[str, float]`

Get current decision weights.

**Returns:**

- `Dict[str, float]`: Current decision weights

##### `set_decision_weights(weights: Dict[str, float]) -> None`

Set custom decision weights.

**Parameters:**

- `weights` (Dict[str, float]): Custom decision weights

## Data Structures

### TaskRequest

Request structure for LLM tasks.

```python
@dataclass
class TaskRequest:
    prompt: str
    task_type: TaskType
    images: Optional[List[bytes]] = None
    audio: Optional[bytes] = None
    structured_output: Optional[Dict[str, Any]] = None
    functions: Optional[List[Dict[str, Any]]] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[List[str]] = None
```

**Fields:**

- `prompt` (str): The input prompt for the LLM
- `task_type` (TaskType): Type of task being performed
- `images` (Optional[List[bytes]]): List of image data for vision tasks
- `audio` (Optional[bytes]): Audio data for audio processing tasks
- `structured_output` (Optional[Dict[str, Any]]): Schema for structured output
- `functions` (Optional[List[Dict[str, Any]]]): Available functions for function calling
- `max_tokens` (Optional[int]): Maximum tokens to generate
- `temperature` (Optional[float]): Sampling temperature (0.0 to 2.0)
- `top_p` (Optional[float]): Nucleus sampling parameter
- `frequency_penalty` (Optional[float]): Frequency penalty (-2.0 to 2.0)
- `presence_penalty` (Optional[float]): Presence penalty (-2.0 to 2.0)
- `stop` (Optional[List[str]]): Stop sequences

### TaskResponse

Response structure from LLM providers.

```python
@dataclass
class TaskResponse:
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    latency_ms: float
    finish_reason: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
```

**Fields:**

- `content` (str): The generated text content
- `model_used` (str): Name of the model that generated the response
- `provider` (str): Name of the provider used
- `tokens_used` (int): Number of tokens used in the request
- `cost` (float): Cost of the request in USD
- `latency_ms` (float): Request latency in milliseconds
- `finish_reason` (str): Reason for completion (stop, length, etc.)
- `usage` (Optional[Dict[str, Any]]): Detailed usage information
- `metadata` (Optional[Dict[str, Any]]): Additional metadata

### SwitchDecision

Decision about which LLM to use.

```python
@dataclass
class SwitchDecision:
    provider: str
    model: str
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency: float
    fallback_options: List[Tuple[str, str]]
    decision_factors: Dict[str, float]
```

**Fields:**

- `provider` (str): Selected provider name
- `model` (str): Selected model name
- `confidence` (float): Confidence score (0.0 to 1.0)
- `reasoning` (str): Human-readable reasoning for the decision
- `estimated_cost` (float): Estimated cost of the request
- `estimated_latency` (float): Estimated latency in milliseconds
- `fallback_options` (List[Tuple[str, str]]): List of fallback (provider, model) pairs
- `decision_factors` (Dict[str, float]): Individual factor scores

## Enums

### TaskType

Enumeration of supported task types.

```python
class TaskType(Enum):
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    VISION_ANALYSIS = "vision_analysis"
    MATH = "math"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    MULTIMODAL = "multimodal"
```

### OptimizationStrategy

Enumeration of optimization strategies.

```python
class OptimizationStrategy(Enum):
    COST = "cost"
    SPEED = "speed"
    PERFORMANCE = "performance"
    BALANCED = "balanced"
```

### FallbackStrategy

Enumeration of fallback strategies.

```python
class FallbackStrategy(Enum):
    PERFORMANCE_BASED = "performance_based"
    COST_BASED = "cost_based"
    SPEED_BASED = "speed_based"
    RELIABILITY_BASED = "reliability_based"
    ROUND_ROBIN = "round_robin"
```

### Capability

Enumeration of LLM capabilities.

```python
class Capability(Enum):
    TEXT = "text"
    VISION = "vision"
    AUDIO = "audio"
    FUNCTION_CALLING = "function_calling"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"
    EMBEDDINGS = "embeddings"
```

## Decorators

### @llm_dispatcher

Main decorator for LLM dispatching.

```python
def llm_dispatcher(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    fallback_enabled: bool = True,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    **kwargs
) -> LLMSwitchDecorator
```

**Parameters:**

- `task_type` (Optional[TaskType]): Specific task type for the function
- `optimization_strategy` (OptimizationStrategy): Strategy for LLM selection
- `max_cost` (Optional[float]): Maximum cost per request
- `max_latency` (Optional[int]): Maximum latency in milliseconds
- `fallback_enabled` (bool): Whether to enable automatic fallback
- `providers` (Optional[List[str]]): List of allowed providers
- `model` (Optional[str]): Preferred model
- `**kwargs`: Additional configuration options

**Example:**

```python
@llm_dispatcher(
    task_type=TaskType.CODE_GENERATION,
    optimization_strategy=OptimizationStrategy.SPEED,
    max_cost=0.01
)
def generate_code(description: str) -> str:
    return description
```

### @llm_stream

Decorator for streaming LLM responses.

```python
def llm_stream(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    chunk_callback: Optional[callable] = None,
    metadata_callback: Optional[callable] = None,
    **kwargs
) -> Callable[[F], F]
```

**Parameters:**

- `task_type` (Optional[TaskType]): Type of task (auto-detected if not provided)
- `optimization_strategy` (OptimizationStrategy): Strategy for optimization
- `max_cost` (Optional[float]): Maximum cost per request
- `max_latency` (Optional[int]): Maximum latency in milliseconds
- `providers` (Optional[List[str]]): List of preferred providers
- `model` (Optional[str]): Specific model to use
- `chunk_callback` (Optional[callable]): Optional callback for processing chunks
- `metadata_callback` (Optional[callable]): Optional callback for receiving metadata
- `**kwargs`: Additional configuration options

**Example:**

```python
@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def stream_text(prompt: str):
    async for chunk in _stream_generator():
        yield chunk
```

### @llm_stream_with_metadata

Decorator for streaming LLM responses with detailed metadata.

```python
def llm_stream_with_metadata(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    include_timing: bool = True,
    include_tokens: bool = True,
    **kwargs
) -> Callable[[F], F]
```

**Parameters:**

- `task_type` (Optional[TaskType]): Type of task (auto-detected if not provided)
- `optimization_strategy` (OptimizationStrategy): Strategy for optimization
- `max_cost` (Optional[float]): Maximum cost per request
- `max_latency` (Optional[int]): Maximum latency in milliseconds
- `providers` (Optional[List[str]]): List of preferred providers
- `model` (Optional[str]): Specific model to use
- `include_timing` (bool): Whether to include timing information
- `include_tokens` (bool): Whether to include token estimation
- `**kwargs`: Additional configuration options

**Example:**

```python
@llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
async def stream_text_with_metadata(prompt: str):
    async for metadata in _stream_generator():
        yield metadata
```

## Convenience Decorators

### Task-Specific Decorators

```python
def for_text_generation(**kwargs) -> LLMSwitchDecorator
def for_code_generation(**kwargs) -> LLMSwitchDecorator
def for_reasoning(**kwargs) -> LLMSwitchDecorator
def for_vision(**kwargs) -> LLMSwitchDecorator
def for_math(**kwargs) -> LLMSwitchDecorator
```

### Optimization Decorators

```python
def cost_optimized(**kwargs) -> LLMSwitchDecorator
def speed_optimized(**kwargs) -> LLMSwitchDecorator
def performance_optimized(**kwargs) -> LLMSwitchDecorator
```

## Configuration

### SwitchConfig

Main configuration class for the dispatcher.

```python
@dataclass
class SwitchConfig:
    providers: Dict[str, ProviderConfig]
    switching_rules: SwitchingRules
    global_settings: GlobalSettings
```

### ProviderConfig

Configuration for individual LLM providers.

```python
@dataclass
class ProviderConfig:
    api_key: Optional[str] = None
    enabled: bool = True
    models: List[str] = field(default_factory=list)
    custom_endpoint: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    rate_limit: Optional[int] = None
```

### SwitchingRules

Rules for intelligent LLM switching.

```python
@dataclass
class SwitchingRules:
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    fallback_strategy: FallbackStrategy = FallbackStrategy.PERFORMANCE_BASED
    max_cost_per_request: Optional[float] = None
    max_latency_ms: Optional[int] = None
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    enable_analytics: bool = True
```

## Utilities

### BenchmarkManager

Manages credible benchmark data for LLM performance evaluation.

```python
class BenchmarkManager:
    def get_benchmark_scores(self, model: str) -> Dict[str, float]
    def get_performance_metrics(self, model: str) -> PerformanceMetrics
    def get_task_performance_ranking(self, task_type: TaskType) -> List[Tuple[str, float]]
    def get_cost_efficiency_ranking(self) -> List[Tuple[str, float]]
    def get_speed_ranking(self) -> List[Tuple[str, float]]
    def get_reliability_ranking(self) -> List[Tuple[str, float]]
```

### CostCalculator

Provides utilities for calculating and tracking LLM costs.

```python
class CostCalculator:
    def calculate_cost(self, provider: str, model: str, tokens: int) -> float
    def track_cost(self, provider: str, model: str, tokens: int, cost: float) -> None
    def get_cost_efficiency_ranking(self) -> List[Tuple[str, float]]
    def get_total_cost(self, start_date: datetime, end_date: datetime) -> float
```

### PerformanceMonitor

Implements real-time performance monitoring.

```python
class PerformanceMonitor:
    def record_request(self, provider: str, model: str, latency_ms: float, success: bool) -> None
    def get_performance_stats(self, provider: str, model: str) -> PerformanceStats
    def get_system_overview(self) -> Dict[str, Any]
    def get_latency_percentiles(self, provider: str, model: str) -> Dict[str, float]
```

## Multimodal

### MultimodalAnalyzer

Advanced multimodal analysis for LLM task optimization.

```python
class MultimodalAnalyzer:
    def analyze_multimodal_content(
        self,
        media_data: Dict[str, Union[str, bytes]],
        analysis_type: AnalysisType = AnalysisType.COMPREHENSIVE,
        task_description: Optional[str] = None
    ) -> MultimodalAnalysis
```

### MediaValidator

Media validation and security for multi-modal LLM tasks.

```python
class MediaValidator:
    def validate_media(
        self,
        media_data: Union[str, bytes],
        media_type: Optional[MediaType] = None
    ) -> ValidationResult
```

## Monitoring

### AnalyticsEngine

Advanced analytics engine for LLM-Dispatcher.

```python
class AnalyticsEngine:
    async def record_request(
        self,
        provider: str,
        model: str,
        task_type: str,
        success: bool,
        latency_ms: float,
        cost: float,
        tokens_used: int = 0,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    )

    def generate_performance_report(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        providers: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        task_types: Optional[List[str]] = None
    ) -> PerformanceReport

    def analyze_usage_patterns(self, days: int = 30) -> UsagePattern

    def assess_system_health(self) -> SystemHealth
```

### MonitoringDashboard

Comprehensive monitoring dashboard for LLM-Dispatcher.

```python
class MonitoringDashboard:
    def __init__(
        self,
        analytics_engine: AnalyticsEngine,
        metrics_collector: MetricsCollector,
        update_interval: int = 30
    )

    async def start(self)
    async def stop(self)
    def get_dashboard_data(self) -> Dict[str, Any]
    async def generate_summary_report(self) -> Dict[str, Any]
```

## Caching

### CacheManager

Advanced cache manager for LLM responses.

```python
class CacheManager:
    def __init__(
        self,
        cache_dir: str = "./cache",
        max_size_mb: int = 100,
        cleanup_interval: int = 3600,
        cache_policies: List[CachePolicy] = None
    )

    def start(self) -> None
    def stop(self) -> None
    def get(self, key: str) -> Optional[Any]
    def put(self, key: str, value: Any, tags: List[str] = None, metadata: Dict[str, Any] = None) -> None
    def invalidate_pattern(self, pattern: str) -> int
    def get_cache_stats(self) -> Dict[str, Any]
```

### SemanticCache

Semantic similarity-based caching.

```python
class SemanticCache:
    def __init__(
        self,
        cache_dir: str = "./semantic_cache",
        similarity_threshold: float = 0.8,
        max_cache_size: int = 10000
    )

    def get_similar_response(self, query: str, threshold: Optional[float] = None) -> Optional[Dict[str, Any]]
    def add_to_semantic_cache(self, query: str, response: str, metadata: Dict[str, Any] = None) -> None
    def find_best_similar_response(self, query: str) -> Optional[Dict[str, Any]]
```

## Error Handling

### Common Exceptions

```python
class LLMDispatcherError(Exception):
    """Base exception for LLM-Dispatcher errors."""
    pass

class ProviderError(LLMDispatcherError):
    """Error related to LLM providers."""
    pass

class ConfigurationError(LLMDispatcherError):
    """Error related to configuration."""
    pass

class ValidationError(LLMDispatcherError):
    """Error related to input validation."""
    pass
```

## Type Hints

### Common Type Aliases

```python
from typing import Dict, List, Optional, Union, Any, AsyncGenerator, Callable

# Request/Response types
RequestData = Union[str, bytes, Dict[str, Any]]
ResponseData = Union[str, Dict[str, Any]]

# Provider types
ProviderName = str
ModelName = str

# Metric types
MetricValue = Union[int, float, bool]
MetricTags = Dict[str, str]
MetricMetadata = Dict[str, Any]

# Cache types
CacheKey = str
CacheValue = Any
CacheTags = List[str]
```

## Constants

### Default Values

```python
DEFAULT_MAX_TOKENS = 4096
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 1.0
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 3
DEFAULT_CACHE_TTL = 3600
DEFAULT_MAX_COST = 1.0
DEFAULT_MAX_LATENCY = 5000
```

### Supported Providers

```python
SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic",
    "google"
]
```

### Supported Models

```python
OPENAI_MODELS = [
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-3.5-turbo"
]

ANTHROPIC_MODELS = [
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku"
]

GOOGLE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-1.5-pro"
]
```
