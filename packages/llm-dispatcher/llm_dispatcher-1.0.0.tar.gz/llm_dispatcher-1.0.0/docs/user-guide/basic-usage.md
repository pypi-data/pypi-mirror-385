# Basic Usage

This guide covers the fundamental concepts and usage patterns of LLM-Dispatcher.

## Core Concepts

### LLM Switch

The `LLMSwitch` is the central component that manages provider selection and routing decisions.

```python
from llm_dispatcher import LLMSwitch

# Create a switch instance
switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."},
        "google": {"api_key": "..."}
    }
)
```

### Task Types

LLM-Dispatcher supports various task types to optimize model selection:

```python
from llm_dispatcher.core.base import TaskType

# Available task types
TaskType.TEXT_GENERATION      # General text generation
TaskType.CODE_GENERATION      # Code writing and debugging
TaskType.VISION_ANALYSIS      # Image and visual content analysis
TaskType.AUDIO_TRANSCRIPTION  # Audio to text conversion
TaskType.REASONING           # Complex reasoning tasks
TaskType.MATH                # Mathematical problem solving
TaskType.MULTIMODAL_ANALYSIS # Multiple media types
```

### Optimization Strategies

Choose how LLM-Dispatcher optimizes provider selection:

```python
from llm_dispatcher.config.settings import OptimizationStrategy

# Available strategies
OptimizationStrategy.BALANCED    # Balance cost, speed, and quality
OptimizationStrategy.COST        # Prioritize cost efficiency
OptimizationStrategy.SPEED       # Prioritize response time
OptimizationStrategy.PERFORMANCE # Prioritize quality and accuracy
```

## Basic Decorator Usage

### Simple Text Generation

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    """Automatically routed to the best LLM for text generation."""
    return prompt

# Usage
result = generate_text("Write a story about a robot")
print(result)
```

### Task-Specific Generation

```python
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Automatically uses the best model for code generation."""
    return description

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(prompt: str, image_path: str) -> str:
    """Automatically uses vision-capable models."""
    return prompt

# Usage
code = generate_code("Create a Python function to sort a list")
analysis = analyze_image("Describe this image", "path/to/image.jpg")
```

### Optimization Strategy

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.config.settings import OptimizationStrategy

@llm_dispatcher(optimization_strategy=OptimizationStrategy.COST)
def cost_optimized_generation(prompt: str) -> str:
    """Optimized for cost efficiency."""
    return prompt

@llm_dispatcher(optimization_strategy=OptimizationStrategy.SPEED)
def speed_optimized_generation(prompt: str) -> str:
    """Optimized for speed."""
    return prompt

@llm_dispatcher(optimization_strategy=OptimizationStrategy.PERFORMANCE)
def quality_optimized_generation(prompt: str) -> str:
    """Optimized for best quality."""
    return prompt
```

## Advanced Decorator Options

### Cost and Performance Limits

```python
@llm_dispatcher(
    max_cost=0.05,        # Maximum cost per request
    max_latency=3000,     # Maximum latency in milliseconds
    fallback_enabled=True # Enable automatic fallback
)
def generate_with_limits(prompt: str) -> str:
    """Generation with cost and performance constraints."""
    return prompt
```

### Provider Selection

```python
@llm_dispatcher(
    providers=["openai", "google"],  # Only use these providers
    fallback_enabled=True
)
def generate_with_providers(prompt: str) -> str:
    """Generation with specific provider selection."""
    return prompt
```

### Retry Configuration

```python
@llm_dispatcher(
    max_retries=3,        # Maximum number of retries
    retry_delay=1000,     # Delay between retries in milliseconds
    fallback_enabled=True
)
def generate_with_retries(prompt: str) -> str:
    """Generation with retry logic."""
    return prompt
```

## Switch Instance Usage

### Custom Switch Configuration

```python
from llm_dispatcher import LLMSwitch, TaskType

# Create a custom switch
switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."},
        "google": {"api_key": "..."}
    },
    config={
        "prefer_cost_efficiency": True,
        "max_latency_ms": 2000,
        "fallback_enabled": True
    }
)

# Use the switch for routing
@switch.route(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Uses the configured switch instance."""
    return description
```

### Global Switch Management

```python
from llm_dispatcher import init, get_global_switch, set_global_switch

# Initialize global switch
switch = init(
    openai_api_key="sk-...",
    anthropic_api_key="sk-ant-...",
    google_api_key="..."
)

# Get global switch
global_switch = get_global_switch()

# Set custom global switch
set_global_switch(switch)
```

## Error Handling

### Basic Error Handling

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.exceptions import LLMDispatcherError

@llm_dispatcher(fallback_enabled=True)
def reliable_generation(prompt: str) -> str:
    """Generation with automatic fallback."""
    return prompt

try:
    result = reliable_generation("Your prompt here")
    print(result)
except LLMDispatcherError as e:
    print(f"Error: {e}")
    # Handle fallback or retry logic
```

### Provider-Specific Error Handling

```python
from llm_dispatcher.exceptions import (
    ProviderError,
    ProviderRateLimitError,
    ProviderQuotaExceededError
)

@llm_dispatcher
def handle_provider_errors(prompt: str) -> str:
    """Handle different types of provider errors."""
    return prompt

try:
    result = handle_provider_errors("Your prompt here")
    print(result)
except ProviderRateLimitError:
    print("Rate limit exceeded, waiting before retry...")
except ProviderQuotaExceededError:
    print("Quota exceeded, switching to alternative provider...")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Monitoring and Analytics

### System Status

```python
from llm_dispatcher import get_global_switch

# Get system status
switch = get_global_switch()
status = switch.get_system_status()
print(f"Providers: {status['total_providers']}")
print(f"Models: {status['total_models']}")
print(f"Active connections: {status['active_connections']}")
```

### Decision Analysis

```python
from llm_dispatcher.core.base import TaskRequest, TaskType

# See which model would be selected
request = TaskRequest(
    prompt="Write a story about AI",
    task_type=TaskType.TEXT_GENERATION
)

decision = await switch.select_llm(request)
print(f"Selected: {decision.provider}:{decision.model}")
print(f"Confidence: {decision.confidence}")
print(f"Reasoning: {decision.reasoning}")
print(f"Estimated cost: ${decision.estimated_cost}")
print(f"Estimated latency: {decision.estimated_latency}ms")
```

### Performance Metrics

```python
# Get performance metrics
metrics = switch.get_performance_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Average latency: {metrics['avg_latency']:.2f}ms")
print(f"Total cost: ${metrics['total_cost']:.4f}")
```

## Best Practices

### 1. Use Appropriate Task Types

```python
# Good: Use specific task types
@llm_dispatcher(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    return description

# Avoid: Using generic task type when specific is available
@llm_dispatcher  # Uses default TEXT_GENERATION
def generate_code(description: str) -> str:
    return description
```

### 2. Set Reasonable Limits

```python
# Good: Set appropriate limits
@llm_dispatcher(
    max_cost=0.05,
    max_latency=3000,
    fallback_enabled=True
)
def generate_with_limits(prompt: str) -> str:
    return prompt

# Avoid: Setting unrealistic limits
@llm_dispatcher(
    max_cost=0.001,  # Too low
    max_latency=100  # Too low
)
def generate_with_unrealistic_limits(prompt: str) -> str:
    return prompt
```

### 3. Enable Fallbacks

```python
# Good: Always enable fallbacks for production
@llm_dispatcher(fallback_enabled=True)
def reliable_generation(prompt: str) -> str:
    return prompt

# Avoid: Disabling fallbacks in production
@llm_dispatcher(fallback_enabled=False)
def unreliable_generation(prompt: str) -> str:
    return prompt
```

### 4. Handle Errors Gracefully

```python
# Good: Proper error handling
try:
    result = generate_text("Your prompt")
except LLMDispatcherError as e:
    logger.error(f"Generation failed: {e}")
    # Implement fallback logic
    result = "Fallback response"

# Avoid: Ignoring errors
result = generate_text("Your prompt")  # May raise unhandled exceptions
```

### 5. Monitor Performance

```python
# Good: Monitor performance regularly
def monitor_performance():
    metrics = switch.get_performance_metrics()
    if metrics['success_rate'] < 0.95:
        logger.warning("Success rate below threshold")
    if metrics['avg_latency'] > 5000:
        logger.warning("Average latency too high")

# Call periodically
monitor_performance()
```

## Common Patterns

### Batch Processing

```python
@llm_dispatcher(max_cost=0.01)
def process_single_item(item: str) -> str:
    """Process a single item."""
    return item

def process_batch(items: list) -> list:
    """Process multiple items efficiently."""
    return [process_single_item(item) for item in items]

# Usage
items = ["Item 1", "Item 2", "Item 3"]
results = process_batch(items)
```

### Conditional Processing

```python
@llm_dispatcher(task_type=TaskType.TEXT_GENERATION)
def process_text(text: str) -> str:
    """Process text based on content."""
    return text

def smart_processing(input_text: str) -> str:
    """Process text with conditional logic."""
    if len(input_text) > 1000:
        # Use cost-optimized processing for long text
        return process_text(input_text)
    else:
        # Use quality-optimized processing for short text
        return process_text(input_text)
```

### Caching Integration

```python
import functools

@functools.lru_cache(maxsize=100)
@llm_dispatcher(task_type=TaskType.TEXT_GENERATION)
def cached_generation(prompt: str) -> str:
    """Generation with caching."""
    return prompt

# Usage - repeated calls with same prompt will use cache
result1 = cached_generation("Same prompt")
result2 = cached_generation("Same prompt")  # Uses cache
```

## Next Steps

- [:octicons-gear-24: Advanced Features](advanced-features.md) - Explore advanced capabilities
- [:octicons-eye-24: Multimodal Support](multimodal.md) - Work with images and audio
- [:octicons-lightning-bolt-24: Streaming](streaming.md) - Real-time response streaming
- [:octicons-shield-check-24: Error Handling](error-handling.md) - Robust error handling
- [:octicons-chart-line-24: Performance Tips](performance.md) - Optimization strategies
