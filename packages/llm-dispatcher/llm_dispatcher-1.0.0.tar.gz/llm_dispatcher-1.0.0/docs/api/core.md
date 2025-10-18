# Core API Reference

This page provides comprehensive documentation for the core LLM-Dispatcher API components.

## Core Classes

### LLMSwitch

The main orchestrator class that manages providers and routing.

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.config.settings import OptimizationStrategy

# Initialize with providers (dictionary format)
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
        "max_retries": 3
    }
)
```

#### Methods

##### `process_request(request: TaskRequest) -> TaskResponse`

Process a single request through the dispatcher.

```python
from llm_dispatcher.core.base import TaskRequest, TaskType

request = TaskRequest(
    prompt="Your prompt here",
    task_type=TaskType.TEXT_GENERATION,
    max_tokens=1000
)

response = await switch.process_request(request)
print(response.content)
```

##### `process_batch(requests: List[TaskRequest]) -> List[TaskResponse]`

Process multiple requests efficiently.

```python
requests = [
    TaskRequest(prompt="Question 1", task_type=TaskType.TEXT_GENERATION),
    TaskRequest(prompt="Question 2", task_type=TaskType.TEXT_GENERATION)
]

responses = await switch.process_batch(requests)
for response in responses:
    print(response.content)
```

##### `get_provider_status() -> Dict[str, ProviderStatus]`

Get the current status of all providers.

```python
status = switch.get_provider_status()
for provider_name, provider_status in status.items():
    print(f"{provider_name}: {provider_status.status}")
    print(f"  Latency: {provider_status.avg_latency}ms")
    print(f"  Success Rate: {provider_status.success_rate:.2%}")
```

##### `update_config(config: Dict[str, Any]) -> None`

Update the switch configuration at runtime.

```python
switch.update_config({
    "optimization_strategy": OptimizationStrategy.COST,
    "max_retries": 5
})
```

### TaskRequest

Represents a request to be processed by the dispatcher.

```python
from llm_dispatcher.core.base import TaskRequest, TaskType

request = TaskRequest(
    prompt="Your prompt here",
    task_type=TaskType.TEXT_GENERATION,
    max_tokens=1000,
    temperature=0.7,
    metadata={"user_id": "123", "session_id": "abc"}
)
```

#### Attributes

- `prompt: str` - The input prompt
- `task_type: TaskType` - The type of task to perform
- `max_tokens: int` - Maximum tokens to generate
- `temperature: float` - Sampling temperature
- `metadata: Dict[str, Any]` - Additional metadata

### TaskResponse

Represents the response from a processed request.

```python
from llm_dispatcher.core.base import TaskResponse

response = TaskResponse(
    content="Generated response",
    provider="openai",
    model="gpt-4",
    tokens_used=150,
    cost=0.002,
    latency=1200,
    metadata={"request_id": "req_123"}
)
```

#### Attributes

- `content: str` - The generated content
- `provider: str` - The provider that generated the response
- `model: str` - The model used
- `tokens_used: int` - Number of tokens used
- `cost: float` - Cost of the request
- `latency: int` - Response latency in milliseconds
- `metadata: Dict[str, Any]` - Additional metadata

### TaskType

Enumeration of supported task types.

```python
from llm_dispatcher.core.base import TaskType

# Available task types
TaskType.TEXT_GENERATION
TaskType.CODE_GENERATION
TaskType.REASONING
TaskType.CREATIVE_WRITING
TaskType.ANALYSIS
TaskType.SUMMARIZATION
TaskType.TRANSLATION
TaskType.QUESTION_ANSWERING
TaskType.VISION_ANALYSIS
TaskType.AUDIO_TRANSCRIPTION
TaskType.MULTIMODAL_ANALYSIS
```

## Decorators

### @llm_dispatcher

The main decorator for automatic LLM dispatching.

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType

@llm_dispatcher(
    task_type=TaskType.TEXT_GENERATION,
    optimization_strategy=OptimizationStrategy.BALANCED,
    fallback_enabled=True,
    max_retries=3
)
def generate_text(prompt: str) -> str:
    """Generate text using the best available provider."""
    return prompt

# Usage
result = generate_text("Write a story about space exploration")
```

#### Parameters

- `task_type: TaskType` - The type of task to perform
- `optimization_strategy: OptimizationStrategy` - Optimization strategy
- `fallback_enabled: bool` - Enable fallback to alternative providers
- `max_retries: int` - Maximum number of retry attempts
- `timeout: int` - Request timeout in milliseconds
- `cache: Cache` - Caching strategy to use
- `monitor: Monitor` - Performance monitoring

### @llm_stream

Decorator for streaming responses.

```python
from llm_dispatcher import llm_stream

@llm_stream(
    task_type=TaskType.TEXT_GENERATION,
    chunk_size=100
)
async def stream_text(prompt: str):
    """Stream text generation in real-time."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    for chunk in chunks:
        yield chunk

# Usage
async for chunk in stream_text("Write a long story"):
    print(chunk, end="", flush=True)
```

### @llm_stream_with_metadata

Decorator for streaming with metadata.

```python
from llm_dispatcher import llm_stream_with_metadata

@llm_stream_with_metadata(
    task_type=TaskType.TEXT_GENERATION
)
async def stream_with_metadata(prompt: str):
    """Stream with additional metadata."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        {"chunk": "Chunk 1", "chunk_index": 0, "provider": "openai"},
        {"chunk": "Chunk 2", "chunk_index": 1, "provider": "openai"}
    ]
    for chunk_data in chunks:
        yield chunk_data

# Usage
async for metadata in stream_with_metadata("Write a story"):
    print(f"[{metadata['provider']}] {metadata['chunk']}")
```

## Configuration

### OptimizationStrategy

Enumeration of optimization strategies.

```python
from llm_dispatcher.config.settings import OptimizationStrategy

# Available strategies
OptimizationStrategy.COST        # Minimize cost
OptimizationStrategy.SPEED       # Minimize latency
OptimizationStrategy.PERFORMANCE # Maximize quality
OptimizationStrategy.BALANCED    # Balance cost, speed, and quality
```

### Provider Configuration

```python

# Provider configuration is a dictionary with provider names as keys
provider_config = {
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
}
```

### Global Configuration

```python
global_config = {
    "optimization_strategy": OptimizationStrategy.BALANCED,
    "fallback_enabled": True,
    "max_retries": 3,
    "retry_delay": 1000,
    "timeout": 30000,
    "cache_enabled": True,
    "monitoring_enabled": True,
    "logging_level": "INFO"
}
```

## Error Handling

### Exception Hierarchy

```python
from llm_dispatcher.exceptions import (
    LLMDispatcherError,
    ProviderError,
    ModelError,
    ConfigurationError,
    RequestError
)

# Base exception
class LLMDispatcherError(Exception):
    """Base exception for all LLM-Dispatcher errors."""
    pass

# Provider-specific errors
class ProviderError(LLMDispatcherError):
    """Base exception for provider-related errors."""
    pass

class ProviderConnectionError(ProviderError):
    """Connection error with provider."""
    pass

class ProviderAuthenticationError(ProviderError):
    """Authentication error with provider."""
    pass

class ProviderRateLimitError(ProviderError):
    """Rate limit exceeded error."""
    pass

# Model-specific errors
class ModelError(LLMDispatcherError):
    """Base exception for model-related errors."""
    pass

class ModelNotFoundError(ModelError):
    """Model not found error."""
    pass

class ModelContextLengthExceededError(ModelError):
    """Context length exceeded error."""
    pass

# Configuration errors
class ConfigurationError(LLMDispatcherError):
    """Configuration-related error."""
    pass

class InvalidConfigurationError(ConfigurationError):
    """Invalid configuration error."""
    pass

class MissingConfigurationError(ConfigurationError):
    """Missing configuration error."""
    pass

# Request errors
class RequestError(LLMDispatcherError):
    """Base exception for request-related errors."""
    pass

class InvalidRequestError(RequestError):
    """Invalid request error."""
    pass

class RequestTimeoutError(RequestError):
    """Request timeout error."""
    pass
```

### Error Handling Example

```python
from llm_dispatcher.exceptions import (
    LLMDispatcherError,
    ProviderError,
    ModelError
)

try:
    result = generate_text("Your prompt")
except ProviderError as e:
    print(f"Provider error: {e}")
    # Handle provider-specific errors
except ModelError as e:
    print(f"Model error: {e}")
    # Handle model-specific errors
except LLMDispatcherError as e:
    print(f"Dispatcher error: {e}")
    # Handle other dispatcher errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

## Monitoring and Analytics

### Performance Metrics

```python
from llm_dispatcher.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

# Get performance statistics
stats = monitor.get_statistics()
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Total requests: {stats.total_requests}")
print(f"Total cost: ${stats.total_cost:.4f}")
```

### Provider Analytics

```python
# Get provider-specific analytics
provider_stats = monitor.get_provider_statistics()
for provider, stats in provider_stats.items():
    print(f"{provider}:")
    print(f"  Requests: {stats.requests}")
    print(f"  Success rate: {stats.success_rate:.2%}")
    print(f"  Average latency: {stats.avg_latency}ms")
    print(f"  Total cost: ${stats.total_cost:.4f}")
```

## Caching

### Cache Interface

```python
from llm_dispatcher.cache import Cache

class Cache:
    """Base cache interface."""

    def get(self, key: str) -> Optional[str]:
        """Get cached value."""
        pass

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set cached value."""
        pass

    def delete(self, key: str) -> None:
        """Delete cached value."""
        pass

    def clear(self) -> None:
        """Clear all cached values."""
        pass
```

### Cache Implementations

```python
from llm_dispatcher.cache import (
    MemoryCache,
    RedisCache,
    SemanticCache,
    TTLCache,
    LRUCache
)

# Memory cache
memory_cache = MemoryCache(max_size=1000)

# Redis cache
redis_cache = RedisCache(
    host="localhost",
    port=6379,
    db=0
)

# Semantic cache
semantic_cache = SemanticCache(
    similarity_threshold=0.95,
    embedding_model="text-embedding-ada-002"
)

# TTL cache
ttl_cache = TTLCache(ttl=3600)  # 1 hour

# LRU cache
lru_cache = LRUCache(max_size=1000)
```

## Next Steps

- [:octicons-puzzle-24: Decorators](decorators.md) - Decorator API reference
- [:octicons-plug-24: Providers](providers.md) - Provider implementations
- [:octicons-exclamation-triangle-24: Exceptions](exceptions.md) - Exception handling
- [:octicons-gear-24: Configuration](configuration.md) - Configuration options
