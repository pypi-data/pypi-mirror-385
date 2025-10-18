# Examples

This page provides comprehensive examples of LLM-Dispatcher usage across different scenarios and use cases.

## Basic Examples

### Simple Text Generation

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    """Automatically routed to the best LLM for text generation."""
    return prompt

# Usage
result = generate_text("Write a story about a robot learning to paint")
print(result)
```

### Code Generation

```python
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Generate code based on description."""
    return description

# Usage
code = generate_code("Create a Python function to calculate fibonacci numbers")
print(code)
```

### Math Problem Solving

```python
@llm_dispatcher(task_type=TaskType.MATH)
def solve_math(problem: str) -> str:
    """Solve mathematical problems."""
    return problem

# Usage
solution = solve_math("What is the derivative of x^2 + 3x + 5?")
print(solution)
```

## Advanced Examples

### Cost-Optimized Generation

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.config.settings import OptimizationStrategy

@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST,
    max_cost=0.01
)
def cost_optimized_generation(prompt: str) -> str:
    """Generate text with cost optimization."""
    return prompt

# Usage
result = cost_optimized_generation("Summarize the benefits of renewable energy")
print(result)
```

### Speed-Optimized Generation

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.SPEED,
    max_latency=2000
)
def fast_generation(prompt: str) -> str:
    """Generate text with speed optimization."""
    return prompt

# Usage
result = fast_generation("What is the capital of France?")
print(result)
```

### Quality-Optimized Generation

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def quality_generation(prompt: str) -> str:
    """Generate high-quality text."""
    return prompt

# Usage
result = quality_generation("Write a detailed analysis of climate change impacts")
print(result)
```

## Multimodal Examples

### Image Analysis

```python
import base64
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images with vision-capable models."""
    return prompt

# Usage with base64 encoded images
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_data = encode_image("path/to/image.jpg")
result = analyze_image("What's in this image?", [image_data])
print(result)
```

### Audio Transcription

```python
@llm_dispatcher(task_type=TaskType.AUDIO_TRANSCRIPTION)
def transcribe_audio(prompt: str, audio: str) -> str:
    """Transcribe audio with appropriate models."""
    return prompt

# Usage with base64 encoded audio
def encode_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

audio_data = encode_audio("path/to/audio.mp3")
transcript = transcribe_audio("Transcribe this audio", audio_data)
print(transcript)
```

### Multimodal Analysis

```python
@llm_dispatcher(task_type=TaskType.MULTIMODAL_ANALYSIS)
def analyze_multimodal(prompt: str, images: list, audio: str) -> str:
    """Analyze multiple media types."""
    return prompt

# Usage
result = analyze_multimodal(
    "Analyze this image and audio together",
    [image_data],
    audio_data
)
print(result)
```

## Streaming Examples

### Basic Streaming

```python
from llm_dispatcher import llm_stream, TaskType

@llm_stream(task_type=TaskType.TEXT_GENERATION)
async def stream_text(prompt: str):
    """Stream text generation in real-time."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        "This is a streaming response. ",
        "Each chunk is delivered ",
        "as it becomes available. ",
        "This provides a better ",
        "user experience for long responses."
    ]

    for chunk in chunks:
        yield chunk

# Usage
async def main():
    async for chunk in stream_text("Write a long story about space exploration"):
        print(chunk, end="", flush=True)

# Run the async function
import asyncio
asyncio.run(main())
```

### Streaming with Metadata

```python
from llm_dispatcher import llm_stream_with_metadata, TaskType

@llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
async def stream_with_metadata(prompt: str):
    """Stream with additional metadata."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = [
        {"chunk": "Chunk 1: ", "chunk_index": 0, "provider": "openai", "model": "gpt-4"},
        {"chunk": "Chunk 2: ", "chunk_index": 1, "provider": "openai", "model": "gpt-4"},
        {"chunk": "Chunk 3: ", "chunk_index": 2, "provider": "openai", "model": "gpt-4"}
    ]

    for chunk_data in chunks:
        yield chunk_data

# Usage
async def main():
    async for metadata in stream_with_metadata("Write a story"):
        print(f"[{metadata['provider']}:{metadata['model']}] {metadata['chunk']}")

asyncio.run(main())
```

## Error Handling Examples

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

### Custom Error Handling

```python
@llm_dispatcher(
    fallback_enabled=True,
    providers=["openai", "google"],  # Try these in order
    max_retries=3
)
def robust_generation(prompt: str) -> str:
    """Generation with custom retry logic."""
    return prompt

try:
    result = robust_generation("Your prompt here")
    print(result)
except Exception as e:
    print(f"All providers failed: {e}")
    # Implement custom fallback logic
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
    # Implement rate limit handling
except ProviderQuotaExceededError:
    print("Quota exceeded, switching to alternative provider...")
    # Implement quota handling
except ProviderError as e:
    print(f"Provider error: {e}")
    # Implement general provider error handling
```

## Custom Switch Examples

### Custom Switch Instance

```python
from llm_dispatcher import LLMSwitch, TaskType

# Initialize with custom configuration
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

@switch.route(task_type=TaskType.CODE_GENERATION)
def generate_code(description: str) -> str:
    """Uses the configured switch instance."""
    return description

# Usage
code = generate_code("Create a Python class for handling HTTP requests")
print(code)
```

### Custom Routing Logic

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

def custom_routing_logic(request: TaskRequest) -> str:
    """Custom logic to determine optimal provider."""
    if request.task_type == TaskType.CODE_GENERATION:
        return "openai"  # Prefer OpenAI for code
    elif request.task_type == TaskType.REASONING:
        return "anthropic"  # Prefer Anthropic for reasoning
    elif "creative" in request.prompt.lower():
        return "anthropic"  # Prefer Anthropic for creative tasks
    else:
        return "auto"  # Let LLM-Dispatcher decide

switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."}
    },
    config={
        "custom_routing_logic": custom_routing_logic
    }
)

@switch.route
def custom_routed_generation(prompt: str) -> str:
    """Uses custom routing logic."""
    return prompt
```

## Monitoring Examples

### System Status Monitoring

```python
from llm_dispatcher import get_global_switch

# Get system status
switch = get_global_switch()
status = switch.get_system_status()
print(f"Providers: {status['total_providers']}")
print(f"Models: {status['total_models']}")
print(f"Active connections: {status['active_connections']}")

# Get decision weights
weights = switch.get_decision_weights()
print(f"Decision weights: {weights}")
```

### Task Analysis

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

### Performance Monitoring

```python
# Get performance metrics
metrics = switch.get_performance_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Success rate: {metrics['success_rate']:.2%}")
print(f"Average latency: {metrics['avg_latency']:.2f}ms")
print(f"Total cost: ${metrics['total_cost']:.4f}")

# Get provider-specific metrics
for provider, provider_metrics in metrics['providers'].items():
    print(f"{provider}: {provider_metrics['requests']} requests, "
          f"{provider_metrics['avg_latency']:.2f}ms avg latency")
```

## Configuration Examples

### Environment-Based Configuration

```python
import os
from llm_dispatcher import LLMSwitch

# Development configuration
if os.getenv("ENVIRONMENT") == "development":
    config = {
        "optimization_strategy": "cost",
        "max_cost_per_request": 0.01,
        "fallback_enabled": True,
        "log_level": "DEBUG"
    }
# Production configuration
elif os.getenv("ENVIRONMENT") == "production":
    config = {
        "optimization_strategy": "balanced",
        "max_cost_per_request": 0.50,
        "fallback_enabled": True,
        "log_level": "INFO",
        "monitoring": {
            "enable_monitoring": True,
            "metrics_retention_days": 90
        }
    }

switch = LLMSwitch(
    providers={
        "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
        "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY")}
    },
    config=config
)
```

### Configuration File Loading

```python
from llm_dispatcher import init_config

# Load configuration from file
switch = init_config("config.yaml")

@switch.route
def configured_generation(prompt: str) -> str:
    """Uses configuration from file."""
    return prompt
```

## Real-World Use Cases

### Content Generation Pipeline

```python
from llm_dispatcher import llm_dispatcher, TaskType

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, max_cost=0.05)
def generate_blog_post(topic: str) -> str:
    """Generate blog post content."""
    return f"Blog post about {topic}"

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, max_cost=0.02)
def generate_social_media_post(content: str) -> str:
    """Generate social media post from blog content."""
    return f"Social media post: {content}"

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, max_cost=0.01)
def generate_seo_description(content: str) -> str:
    """Generate SEO description."""
    return f"SEO description: {content}"

# Content generation pipeline
def content_pipeline(topic: str):
    blog_post = generate_blog_post(topic)
    social_post = generate_social_media_post(blog_post)
    seo_desc = generate_seo_description(blog_post)

    return {
        "blog_post": blog_post,
        "social_post": social_post,
        "seo_description": seo_desc
    }

# Usage
content = content_pipeline("Artificial Intelligence in Healthcare")
print(content)
```

### Code Review Assistant

```python
@llm_dispatcher(task_type=TaskType.CODE_GENERATION, optimization_strategy="performance")
def review_code(code: str) -> str:
    """Review code for issues and improvements."""
    return f"Code review for: {code}"

@llm_dispatcher(task_type=TaskType.CODE_GENERATION, optimization_strategy="cost")
def suggest_improvements(code: str) -> str:
    """Suggest code improvements."""
    return f"Improvements for: {code}"

@llm_dispatcher(task_type=TaskType.CODE_GENERATION, optimization_strategy="speed")
def generate_tests(code: str) -> str:
    """Generate unit tests for code."""
    return f"Tests for: {code}"

# Code review pipeline
def code_review_pipeline(code: str):
    review = review_code(code)
    improvements = suggest_improvements(code)
    tests = generate_tests(code)

    return {
        "review": review,
        "improvements": improvements,
        "tests": tests
    }

# Usage
review_results = code_review_pipeline("def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)")
print(review_results)
```

### Customer Support Bot

```python
@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, optimization_strategy="speed")
def classify_inquiry(inquiry: str) -> str:
    """Classify customer inquiry."""
    return f"Classification: {inquiry}"

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, optimization_strategy="balanced")
def generate_response(inquiry: str, classification: str) -> str:
    """Generate response to customer inquiry."""
    return f"Response to {classification}: {inquiry}"

@llm_dispatcher(task_type=TaskType.TEXT_GENERATION, optimization_strategy="cost")
def escalate_inquiry(inquiry: str) -> str:
    """Escalate complex inquiries."""
    return f"Escalated: {inquiry}"

# Customer support pipeline
def customer_support_pipeline(inquiry: str):
    classification = classify_inquiry(inquiry)

    if "complex" in classification.lower():
        return escalate_inquiry(inquiry)
    else:
        return generate_response(inquiry, classification)

# Usage
response = customer_support_pipeline("I'm having trouble with my account login")
print(response)
```

## Next Steps

- [:octicons-gear-24: Configuration](configuration.md) - Learn about advanced configuration options
- [:octicons-eye-24: Multimodal Support](../user-guide/multimodal.md) - Explore multimodal capabilities
- [:octicons-lightning-bolt-24: Streaming](../user-guide/streaming.md) - Learn about streaming responses
- [:octicons-shield-check-24: Error Handling](../user-guide/error-handling.md) - Master error handling
- [:octicons-chart-line-24: Performance Tips](../user-guide/performance.md) - Optimize performance
