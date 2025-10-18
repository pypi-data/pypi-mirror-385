# OpenAI Provider

The OpenAI provider integrates with OpenAI's GPT models, providing access to GPT-4, GPT-3.5-turbo, and other OpenAI models.

## Overview

The OpenAI provider offers:

- **High-quality text generation** with GPT-4 and GPT-3.5-turbo
- **Function calling** capabilities
- **Vision support** with GPT-4 Vision
- **Streaming responses** for real-time generation
- **Cost optimization** with different model tiers

## Configuration

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"]
        }
    }
)
```

### Advanced Configuration

```python
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.00003,
            "organization": "org-...",  # Optional organization ID
            "project": "proj-..."       # Optional project ID
        }
    }
)
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_ORGANIZATION="org-..."
export OPENAI_PROJECT="proj-..."
```

## Supported Models

### GPT-4 Models

| Model          | Description                      | Max Tokens | Cost per 1K Tokens            |
| -------------- | -------------------------------- | ---------- | ----------------------------- |
| `gpt-4`        | Most capable GPT-4 model         | 8,192      | $0.03 (input), $0.06 (output) |
| `gpt-4-turbo`  | Faster GPT-4 with larger context | 128,000    | $0.01 (input), $0.03 (output) |
| `gpt-4-vision` | GPT-4 with vision capabilities   | 128,000    | $0.01 (input), $0.03 (output) |

### GPT-3.5 Models

| Model               | Description                 | Max Tokens | Cost per 1K Tokens               |
| ------------------- | --------------------------- | ---------- | -------------------------------- |
| `gpt-3.5-turbo`     | Fast and efficient model    | 4,096      | $0.0015 (input), $0.002 (output) |
| `gpt-3.5-turbo-16k` | GPT-3.5 with larger context | 16,384     | $0.003 (input), $0.004 (output)  |

## Usage Examples

### Basic Text Generation

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType

@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"]
)
def generate_text(prompt: str) -> str:
    """Generate text using GPT-4."""
    return prompt

result = generate_text("Write a story about space exploration")
print(result)
```

### Code Generation

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],
    task_type=TaskType.CODE_GENERATION
)
def generate_code(description: str) -> str:
    """Generate code using GPT-4."""
    return description

code = generate_code("Create a Python function to sort a list")
print(code)
```

### Function Calling

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],
    functions=[
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    ]
)
def get_weather_info(query: str) -> str:
    """Get weather information with function calling."""
    return query

result = get_weather_info("What's the weather like in New York?")
print(result)
```

### Vision Analysis

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4-vision"],
    task_type=TaskType.VISION_ANALYSIS
)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images using GPT-4 Vision."""
    return prompt

# Analyze image
image_data = encode_image("path/to/image.jpg")
result = analyze_image("Describe this image", [image_data])
print(result)
```

### Streaming Responses

```python
from llm_dispatcher import llm_stream

@llm_stream(
    providers=["openai"],
    models=["gpt-4"]
)
async def stream_text(prompt: str):
    """Stream text generation using GPT-4."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["This is a streaming response from GPT-4. ", "Each chunk is delivered as it becomes available. ", "This provides a better user experience."]
    for chunk in chunks:
        yield chunk

# Usage
async for chunk in stream_text("Write a long story"):
    print(chunk, end="", flush=True)
```

## Advanced Features

### Custom Parameters

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],
    temperature=0.1,  # Low temperature for consistent output
    max_tokens=2000,
    top_p=0.9,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
def generate_with_custom_params(prompt: str) -> str:
    """Generate text with custom parameters."""
    return prompt

result = generate_with_custom_params("Write a technical explanation")
```

### System Messages

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],
    system_message="You are a helpful assistant that specializes in technical writing."
)
def technical_writing(prompt: str) -> str:
    """Generate technical content with system message."""
    return prompt

result = technical_writing("Explain how machine learning works")
```

### Multiple Models

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4", "gpt-3.5-turbo"]
)
def multi_model_generation(prompt: str) -> str:
    """Generate text using multiple models."""
    return prompt

result = multi_model_generation("Write a creative story")
```

## Error Handling

### Common Errors

```python
from llm_dispatcher.exceptions import (
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderQuotaExceededError
)

try:
    result = generate_text("Your prompt")
except ProviderAuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Check API key
except ProviderRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Retry after: {e.retry_after} seconds")
    # Implement backoff strategy
except ProviderQuotaExceededError as e:
    print(f"Quota exceeded: {e}")
    # Switch to alternative provider or wait for quota reset
```

### Retry Logic

```python
from llm_dispatcher.retry import ExponentialBackoff

@llm_dispatcher(
    providers=["openai"],
    max_retries=3,
    retry_strategy=ExponentialBackoff(
        base_delay=1,
        max_delay=60,
        multiplier=2
    )
)
def retry_generation(prompt: str) -> str:
    """Generate text with retry logic."""
    return prompt
```

## Performance Optimization

### Model Selection

```python
def select_openai_model(prompt: str) -> str:
    """Select best OpenAI model based on prompt."""
    if len(prompt) > 1000:
        return "gpt-4-turbo"  # Better for long prompts
    elif "code" in prompt.lower():
        return "gpt-4"  # Best for code generation
    else:
        return "gpt-3.5-turbo"  # Cost-effective for simple tasks

@llm_dispatcher(
    providers=["openai"],
    models=select_openai_model
)
def optimized_generation(prompt: str) -> str:
    """Generate text with optimized model selection."""
    return prompt
```

### Cost Optimization

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-3.5-turbo"],  # Use cheaper model
    max_tokens=1000,  # Limit tokens
    temperature=0.7
)
def cost_optimized_generation(prompt: str) -> str:
    """Generate text with cost optimization."""
    return prompt
```

### Speed Optimization

```python
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-3.5-turbo"],  # Faster model
    max_tokens=500,  # Shorter responses
    timeout=10  # Shorter timeout
)
def speed_optimized_generation(prompt: str) -> str:
    """Generate text with speed optimization."""
    return prompt
```

## Best Practices

### 1. **Use Appropriate Models**

```python
# Good: Use GPT-4 for complex tasks
@llm_dispatcher(providers=["openai"], models=["gpt-4"])
def complex_analysis(prompt: str) -> str:
    return prompt

# Good: Use GPT-3.5-turbo for simple tasks
@llm_dispatcher(providers=["openai"], models=["gpt-3.5-turbo"])
def simple_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for simple tasks
@llm_dispatcher(providers=["openai"], models=["gpt-4"])
def simple_generation(prompt: str) -> str:
    return prompt
```

### 2. **Implement Proper Error Handling**

```python
# Good: Handle OpenAI-specific errors
try:
    result = generate_text("Your prompt")
except ProviderRateLimitError as e:
    time.sleep(e.retry_after)
    result = generate_text("Your prompt")
except ProviderQuotaExceededError as e:
    # Switch to alternative provider
    result = generate_text_with_fallback("Your prompt")

# Avoid: Ignoring errors
result = generate_text("Your prompt")  # May raise unhandled exceptions
```

### 3. **Use Function Calling When Appropriate**

```python
# Good: Use function calling for structured data
@llm_dispatcher(
    providers=["openai"],
    functions=[weather_function, search_function]
)
def structured_query(prompt: str) -> str:
    return prompt

# Avoid: Not using function calling when it would be beneficial
@llm_dispatcher(providers=["openai"])
def unstructured_query(prompt: str) -> str:
    return prompt
```

### 4. **Optimize for Cost**

```python
# Good: Use cost-effective models for bulk operations
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-3.5-turbo"],
    max_tokens=500
)
def bulk_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for bulk operations
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],
    max_tokens=2000
)
def bulk_generation(prompt: str) -> str:
    return prompt
```

### 5. **Use Streaming for Long Responses**

```python
# Good: Use streaming for long responses
@llm_stream(providers=["openai"])
async def stream_long_response(prompt: str):
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["Long response chunk 1", "Long response chunk 2", "Long response chunk 3"]
    for chunk in chunks:
        yield chunk

# Avoid: Not using streaming for long responses
@llm_dispatcher(providers=["openai"])
def long_response(prompt: str) -> str:
    return prompt  # May cause timeout or poor UX
```

## Monitoring and Analytics

### Performance Metrics

```python
from llm_dispatcher.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

@llm_dispatcher(
    providers=["openai"],
    monitor=monitor
)
def monitored_generation(prompt: str) -> str:
    """Generate text with monitoring."""
    return prompt

# Get OpenAI-specific metrics
stats = monitor.get_provider_statistics("openai")
print(f"OpenAI requests: {stats.requests}")
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Total cost: ${stats.total_cost:.4f}")
```

### Cost Tracking

```python
# Track costs by model
cost_by_model = monitor.get_cost_by_model("openai")
for model, cost in cost_by_model.items():
    print(f"{model}: ${cost:.4f}")
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```python
# Check API key format
api_key = "sk-..."  # Should start with 'sk-'
if not api_key.startswith("sk-"):
    raise ValueError("Invalid OpenAI API key format")
```

#### Rate Limit Errors

```python
# Implement exponential backoff
import time
import random

def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """Calculate exponential backoff delay."""
    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
    return min(delay, 60)  # Cap at 60 seconds

# Use in retry logic
for attempt in range(max_retries):
    try:
        result = generate_text("Your prompt")
        break
    except ProviderRateLimitError as e:
        if attempt < max_retries - 1:
            delay = exponential_backoff(attempt)
            time.sleep(delay)
        else:
            raise
```

#### Context Length Errors

```python
# Truncate long prompts
def truncate_prompt(prompt: str, max_length: int = 4000) -> str:
    """Truncate prompt to fit context length."""
    if len(prompt) <= max_length:
        return prompt

    # Truncate from the end, keeping the beginning
    return prompt[:max_length-3] + "..."

# Use truncated prompt
truncated_prompt = truncate_prompt(long_prompt)
result = generate_text(truncated_prompt)
```

## Next Steps

- [:octicons-plug-24: Anthropic Provider](anthropic.md) - Anthropic Claude integration
- [:octicons-plug-24: Google Provider](google.md) - Google Gemini integration
- [:octicons-plug-24: Grok Provider](grok.md) - xAI Grok integration
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Provider configuration
