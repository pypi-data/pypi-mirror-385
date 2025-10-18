# Decorators API Reference

This page provides comprehensive documentation for the LLM-Dispatcher decorator API.

## Overview

The decorator API provides a simple and intuitive way to integrate LLM-Dispatcher into your applications. Decorators automatically handle provider selection, routing, fallback, and error handling.

## Main Decorators

### @llm_dispatcher

The primary decorator for automatic LLM dispatching.

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType
from llm_dispatcher.config.settings import OptimizationStrategy

@llm_dispatcher(
    task_type=TaskType.TEXT_GENERATION,
    optimization_strategy=OptimizationStrategy.BALANCED,
    fallback_enabled=True,
    max_retries=3,
    timeout=30000
)
def generate_text(prompt: str) -> str:
    """Generate text using the best available provider."""
    return prompt

# Usage
result = generate_text("Write a story about space exploration")
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_type` | `TaskType` | `TEXT_GENERATION` | The type of task to perform |
| `optimization_strategy` | `OptimizationStrategy` | `BALANCED` | Optimization strategy |
| `fallback_enabled` | `bool` | `True` | Enable fallback to alternative providers |
| `max_retries` | `int` | `3` | Maximum number of retry attempts |
| `timeout` | `int` | `30000` | Request timeout in milliseconds |
| `cache` | `Cache` | `None` | Caching strategy to use |
| `monitor` | `Monitor` | `None` | Performance monitoring |
| `providers` | `List[str]` | `None` | Specific providers to use |
| `models` | `List[str]` | `None` | Specific models to use |
| `max_cost` | `float` | `None` | Maximum cost per request |
| `max_tokens` | `int` | `None` | Maximum tokens to generate |
| `temperature` | `float` | `None` | Sampling temperature |

#### Examples

##### Basic Usage
```python
@llm_dispatcher
def simple_generation(prompt: str) -> str:
    """Simple text generation."""
    return prompt

result = simple_generation("Hello, world!")
```

##### Cost Optimization
```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST,
    max_cost=0.01
)
def cost_optimized_generation(prompt: str) -> str:
    """Generate text with cost optimization."""
    return prompt

result = cost_optimized_generation("Simple question")
```

##### Speed Optimization
```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.SPEED,
    max_latency=2000
)
def speed_optimized_generation(prompt: str) -> str:
    """Generate text with speed optimization."""
    return prompt

result = speed_optimized_generation("Quick question")
```

##### Quality Optimization
```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def quality_optimized_generation(prompt: str) -> str:
    """Generate text with quality optimization."""
    return prompt

result = quality_optimized_generation("Complex analysis")
```

##### Provider-Specific
```python
@llm_dispatcher(
    providers=["openai", "anthropic"],
    models=["gpt-4", "claude-3-sonnet"]
)
def provider_specific_generation(prompt: str) -> str:
    """Generate text using specific providers and models."""
    return prompt

result = provider_specific_generation("Technical question")
```

##### With Caching
```python
from llm_dispatcher.cache import SemanticCache

cache = SemanticCache(similarity_threshold=0.95)

@llm_dispatcher(cache=cache)
def cached_generation(prompt: str) -> str:
    """Generate text with caching."""
    return prompt

result = cached_generation("Repeated question")
```

##### With Monitoring
```python
from llm_dispatcher.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

@llm_dispatcher(monitor=monitor)
def monitored_generation(prompt: str) -> str:
    """Generate text with monitoring."""
    return prompt

result = monitored_generation("Monitored request")
```

### @llm_stream

Decorator for streaming responses in real-time.

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

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `task_type` | `TaskType` | `TEXT_GENERATION` | The type of task to perform |
| `chunk_size` | `int` | `100` | Size of each chunk |
| `optimization_strategy` | `OptimizationStrategy` | `BALANCED` | Optimization strategy |
| `fallback_enabled` | `bool` | `True` | Enable fallback to alternative providers |
| `max_retries` | `int` | `3` | Maximum number of retry attempts |
| `timeout` | `int` | `30000` | Request timeout in milliseconds |
| `cache` | `Cache` | `None` | Caching strategy to use |
| `monitor` | `Monitor` | `None` | Performance monitoring |
| `providers` | `List[str]` | `None` | Specific providers to use |
| `models` | `List[str]` | `None` | Specific models to use |

#### Examples

##### Basic Streaming
```python
@llm_stream
async def basic_stream(prompt: str):
    """Basic streaming text generation."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Hello", " world", "!"]
    for chunk in chunks:
        yield chunk

# Usage
async for chunk in basic_stream("Hello"):
    print(chunk, end="", flush=True)
```

##### Streaming with Metadata
```python
@llm_stream_with_metadata
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

##### Streaming with Progress
```python
from llm_dispatcher.streaming import ProgressTracker

@llm_stream(
    progress_tracker=ProgressTracker()
)
async def stream_with_progress(prompt: str):
    """Stream with progress tracking."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Chunk 1", "Chunk 2", "Chunk 3"]
    for chunk in chunks:
        yield chunk

# Usage
async for chunk in stream_with_progress("Write a story"):
    print(chunk, end="", flush=True)
```

### @llm_stream_with_metadata

Decorator for streaming responses with additional metadata.

```python
from llm_dispatcher import llm_stream_with_metadata

@llm_stream_with_metadata(
    task_type=TaskType.TEXT_GENERATION
)
async def stream_with_metadata(prompt: str):
    """Stream with additional metadata."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        {"chunk": "Chunk 1", "chunk_index": 0, "provider": "openai", "model": "gpt-4"},
        {"chunk": "Chunk 2", "chunk_index": 1, "provider": "openai", "model": "gpt-4"}
    ]
    for chunk_data in chunks:
        yield chunk_data

# Usage
async for metadata in stream_with_metadata("Write a story"):
    print(f"[{metadata['provider']}:{metadata['model']}] {metadata['chunk']}")
```

#### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `chunk` | `str` | The text chunk |
| `chunk_index` | `int` | Index of the chunk |
| `provider` | `str` | Provider that generated the chunk |
| `model` | `str` | Model used to generate the chunk |
| `tokens_used` | `int` | Number of tokens used so far |
| `cost` | `float` | Cost of the request so far |
| `latency` | `int` | Response latency in milliseconds |
| `metadata` | `Dict[str, Any]` | Additional metadata |

## Task-Specific Decorators

### @text_generation

Specialized decorator for text generation tasks.

```python
from llm_dispatcher import text_generation

@text_generation(
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def generate_text(prompt: str) -> str:
    """Generate text with optimized settings."""
    return prompt

result = generate_text("Write a story")
```

### @code_generation

Specialized decorator for code generation tasks.

```python
from llm_dispatcher import code_generation

@code_generation(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=2000
)
def generate_code(description: str) -> str:
    """Generate code with optimized settings."""
    return description

result = generate_code("Create a Python function to sort a list")
```

### @reasoning

Specialized decorator for reasoning tasks.

```python
from llm_dispatcher import reasoning

@reasoning(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    temperature=0.1
)
def solve_problem(problem: str) -> str:
    """Solve problems with optimized settings."""
    return problem

result = solve_problem("Solve this math problem: 2x + 5 = 15")
```

### @creative_writing

Specialized decorator for creative writing tasks.

```python
from llm_dispatcher import creative_writing

@creative_writing(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    temperature=0.8
)
def write_creatively(prompt: str) -> str:
    """Write creatively with optimized settings."""
    return prompt

result = write_creatively("Write a poem about the ocean")
```

### @analysis

Specialized decorator for analysis tasks.

```python
from llm_dispatcher import analysis

@analysis(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=1500
)
def analyze_content(content: str) -> str:
    """Analyze content with optimized settings."""
    return content

result = analyze_content("Analyze this business report")
```

### @summarization

Specialized decorator for summarization tasks.

```python
from llm_dispatcher import summarization

@summarization(
    optimization_strategy=OptimizationStrategy.COST,
    max_tokens=500
)
def summarize_text(text: str) -> str:
    """Summarize text with optimized settings."""
    return text

result = summarize_text("Summarize this long article")
```

### @translation

Specialized decorator for translation tasks.

```python
from llm_dispatcher import translation

@translation(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    target_language="Spanish"
)
def translate_text(text: str) -> str:
    """Translate text with optimized settings."""
    return text

result = translate_text("Translate this to Spanish")
```

### @question_answering

Specialized decorator for question answering tasks.

```python
from llm_dispatcher import question_answering

@question_answering(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=1000
)
def answer_question(question: str) -> str:
    """Answer questions with optimized settings."""
    return question

result = answer_question("What is the capital of France?")
```

### @vision_analysis

Specialized decorator for vision analysis tasks.

```python
from llm_dispatcher import vision_analysis

@vision_analysis(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=1000
)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images with optimized settings."""
    return prompt

result = analyze_image("Describe this image", [image_data])
```

### @audio_transcription

Specialized decorator for audio transcription tasks.

```python
from llm_dispatcher import audio_transcription

@audio_transcription(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=2000
)
def transcribe_audio(prompt: str, audio: str) -> str:
    """Transcribe audio with optimized settings."""
    return prompt

result = transcribe_audio("Transcribe this audio", audio_data)
```

### @multimodal_analysis

Specialized decorator for multimodal analysis tasks.

```python
from llm_dispatcher import multimodal_analysis

@multimodal_analysis(
    optimization_strategy=OptimizationStrategy.PERFORMANCE,
    max_tokens=1500
)
def analyze_multimodal(prompt: str, media: list) -> str:
    """Analyze multimodal content with optimized settings."""
    return prompt

result = analyze_multimodal("Analyze this content", [image_data, audio_data])
```

## Advanced Decorator Features

### Custom Configuration

```python
@llm_dispatcher(
    config={
        "custom_setting": "value",
        "another_setting": 123
    }
)
def custom_configured_generation(prompt: str) -> str:
    """Generate text with custom configuration."""
    return prompt
```

### Environment-Specific Settings

```python
import os

@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST if os.getenv("ENV") == "production" else OptimizationStrategy.PERFORMANCE,
    max_retries=5 if os.getenv("ENV") == "production" else 1
)
def environment_aware_generation(prompt: str) -> str:
    """Generate text with environment-aware settings."""
    return prompt
```

### Dynamic Provider Selection

```python
def select_provider(prompt: str) -> list:
    """Dynamically select providers based on prompt."""
    if "code" in prompt.lower():
        return ["openai"]  # Best for code
    elif "creative" in prompt.lower():
        return ["anthropic"]  # Best for creative writing
    else:
        return ["openai", "anthropic"]  # Use both

@llm_dispatcher(
    providers=select_provider
)
def dynamic_provider_generation(prompt: str) -> str:
    """Generate text with dynamic provider selection."""
    return prompt
```

### Conditional Optimization

```python
def get_optimization_strategy(prompt: str) -> OptimizationStrategy:
    """Get optimization strategy based on prompt length."""
    if len(prompt) > 1000:
        return OptimizationStrategy.COST  # Long prompts are expensive
    else:
        return OptimizationStrategy.PERFORMANCE  # Short prompts can use best quality

@llm_dispatcher(
    optimization_strategy=get_optimization_strategy
)
def conditional_optimization_generation(prompt: str) -> str:
    """Generate text with conditional optimization."""
    return prompt
```

## Error Handling in Decorators

### Automatic Error Handling

```python
@llm_dispatcher(
    fallback_enabled=True,
    max_retries=3,
    retry_delay=1000
)
def robust_generation(prompt: str) -> str:
    """Generate text with automatic error handling."""
    return prompt

# Errors are automatically handled with fallback and retry
result = robust_generation("Your prompt")
```

### Custom Error Handling

```python
from llm_dispatcher.exceptions import LLMDispatcherError

@llm_dispatcher
def custom_error_handling_generation(prompt: str) -> str:
    """Generate text with custom error handling."""
    try:
        return prompt
    except LLMDispatcherError as e:
        print(f"Dispatcher error: {e}")
        return "Error occurred"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Unexpected error occurred"
```

## Best Practices

### 1. **Choose Appropriate Task Types**
```python
# Good: Use specific task types
@code_generation
def generate_code(description: str) -> str:
    return description

# Avoid: Using generic decorator for specific tasks
@llm_dispatcher
def generate_code(description: str) -> str:
    return description
```

### 2. **Configure Optimization Strategy**
```python
# Good: Configure based on use case
@llm_dispatcher(optimization_strategy=OptimizationStrategy.COST)
def cost_sensitive_generation(prompt: str) -> str:
    return prompt

# Avoid: Using default strategy for all cases
@llm_dispatcher
def cost_sensitive_generation(prompt: str) -> str:
    return prompt
```

### 3. **Enable Fallbacks for Production**
```python
# Good: Enable fallbacks for reliability
@llm_dispatcher(fallback_enabled=True, max_retries=3)
def production_generation(prompt: str) -> str:
    return prompt

# Avoid: Disabling fallbacks in production
@llm_dispatcher(fallback_enabled=False)
def production_generation(prompt: str) -> str:
    return prompt
```

### 4. **Use Caching for Repeated Requests**
```python
# Good: Use caching for efficiency
@llm_dispatcher(cache=SemanticCache())
def cached_generation(prompt: str) -> str:
    return prompt

# Avoid: No caching for repeated requests
@llm_dispatcher
def cached_generation(prompt: str) -> str:
    return prompt
```

### 5. **Monitor Performance**
```python
# Good: Monitor performance
@llm_dispatcher(monitor=PerformanceMonitor())
def monitored_generation(prompt: str) -> str:
    return prompt

# Avoid: No monitoring in production
@llm_dispatcher
def monitored_generation(prompt: str) -> str:
    return prompt
```

## Next Steps

- [:octicons-puzzle-24: Core API](core.md) - Core API reference
- [:octicons-plug-24: Providers](providers.md) - Provider implementations
- [:octicons-exclamation-triangle-24: Exceptions](exceptions.md) - Exception handling
- [:octicons-gear-24: Configuration](configuration.md) - Configuration options


