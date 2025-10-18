# Grok Provider

The Grok provider integrates with xAI's Grok models, providing access to Grok Beta and other xAI models.

## Overview

The Grok provider offers:

- **Real-time information** access
- **Conversational AI** capabilities
- **Cost-effective** pricing
- **Fast response times**
- **Unique personality** and humor

## Configuration

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={
        "grok": {
            "api_key": "...",
            "models": ["grok-beta"]
        }
    }
)
```

### Advanced Configuration

```python
switch = LLMSwitch(
    providers={
        "grok": {
            "api_key": "...",
            "models": ["grok-beta"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.00002,
            "personality": "helpful"  # Optional personality setting
        }
    }
)
```

### Environment Variables

```bash
export GROK_API_KEY="..."
export GROK_PERSONALITY="helpful"
```

## Supported Models

### Grok Models

| Model       | Description        | Max Tokens | Cost per 1K Tokens             |
| ----------- | ------------------ | ---------- | ------------------------------ |
| `grok-beta` | Current Grok model | 8,192      | $0.002 (input), $0.01 (output) |

## Usage Examples

### Basic Text Generation

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType

@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"]
)
def generate_text(prompt: str) -> str:
    """Generate text using Grok Beta."""
    return prompt

result = generate_text("Explain quantum computing in simple terms")
print(result)
```

### Conversational AI

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    task_type=TaskType.TEXT_GENERATION,
    temperature=0.8
)
def conversational_ai(prompt: str) -> str:
    """Generate conversational responses using Grok."""
    return prompt

response = conversational_ai("Tell me a joke about programming")
print(response)
```

### Real-time Information

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    task_type=TaskType.QUESTION_ANSWERING
)
def get_current_info(prompt: str) -> str:
    """Get current information using Grok."""
    return prompt

info = get_current_info("What's the latest news about AI?")
print(info)
```

### Creative Writing

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    task_type=TaskType.CREATIVE_WRITING,
    temperature=0.9
)
def creative_writing(prompt: str) -> str:
    """Generate creative content using Grok."""
    return prompt

story = creative_writing("Write a humorous story about a robot learning to cook")
print(story)
```

### Analysis and Reasoning

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    task_type=TaskType.ANALYSIS
)
def analyze_content(prompt: str) -> str:
    """Analyze content using Grok."""
    return prompt

analysis = analyze_content("Analyze the pros and cons of renewable energy")
print(analysis)
```

### Streaming Responses

```python
from llm_dispatcher import llm_stream

@llm_stream(
    providers=["grok"],
    models=["grok-beta"]
)
async def stream_text(prompt: str):
    """Stream text generation using Grok."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["This is a streaming response from Grok. ", "Each chunk is delivered as it becomes available. ", "This provides a better user experience."]
    for chunk in chunks:
        yield chunk

# Usage
async for chunk in stream_text("Write a detailed analysis"):
    print(chunk, end="", flush=True)
```

## Advanced Features

### Custom Parameters

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    temperature=0.8,  # Higher temperature for more creative output
    max_tokens=2000,
    personality="helpful"
)
def generate_with_custom_params(prompt: str) -> str:
    """Generate text with custom parameters."""
    return prompt

result = generate_with_custom_params("Write a creative story")
```

### Personality Settings

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    personality="humorous"  # Set personality
)
def humorous_response(prompt: str) -> str:
    """Generate humorous responses using Grok."""
    return prompt

response = humorous_response("Explain how computers work")
```

### Multiple Models

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"]
)
def multi_model_generation(prompt: str) -> str:
    """Generate text using Grok models."""
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
    providers=["grok"],
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

### Cost Optimization

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
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
    providers=["grok"],
    models=["grok-beta"],
    max_tokens=500,  # Shorter responses
    timeout=10  # Shorter timeout
)
def speed_optimized_generation(prompt: str) -> str:
    """Generate text with speed optimization."""
    return prompt
```

### Quality Optimization

```python
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    max_tokens=2000,  # Allow longer responses
    temperature=0.1  # Low temperature for consistency
)
def quality_optimized_generation(prompt: str) -> str:
    """Generate text with quality optimization."""
    return prompt
```

## Best Practices

### 1. **Use Grok for Conversational Tasks**

```python
# Good: Use Grok for conversational AI
@llm_dispatcher(providers=["grok"], models=["grok-beta"])
def conversational_ai(prompt: str) -> str:
    return prompt

# Good: Use Grok for creative writing
@llm_dispatcher(providers=["grok"], models=["grok-beta"])
def creative_writing(prompt: str) -> str:
    return prompt

# Avoid: Using Grok for technical code generation
@llm_dispatcher(providers=["grok"], models=["grok-beta"])
def code_generation(prompt: str) -> str:
    return prompt
```

### 2. **Leverage Grok's Personality**

```python
# Good: Use personality settings
@llm_dispatcher(
    providers=["grok"],
    personality="humorous"
)
def humorous_response(prompt: str) -> str:
    return prompt

# Avoid: Not using personality when it would be beneficial
@llm_dispatcher(providers=["grok"])
def humorous_response(prompt: str) -> str:
    return prompt
```

### 3. **Use Grok for Real-time Information**

```python
# Good: Use Grok for current information
@llm_dispatcher(providers=["grok"], models=["grok-beta"])
def get_current_info(prompt: str) -> str:
    return prompt

# Avoid: Using Grok for historical information
@llm_dispatcher(providers=["grok"], models=["grok-beta"])
def get_historical_info(prompt: str) -> str:
    return prompt
```

### 4. **Optimize for Cost**

```python
# Good: Use cost-effective settings for bulk operations
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    max_tokens=500
)
def bulk_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive settings for bulk operations
@llm_dispatcher(
    providers=["grok"],
    models=["grok-beta"],
    max_tokens=2000
)
def bulk_generation(prompt: str) -> str:
    return prompt
```

### 5. **Handle Errors Gracefully**

```python
# Good: Handle Grok-specific errors
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

## Monitoring and Analytics

### Performance Metrics

```python
from llm_dispatcher.monitoring import PerformanceMonitor

monitor = PerformanceMonitor()

@llm_dispatcher(
    providers=["grok"],
    monitor=monitor
)
def monitored_generation(prompt: str) -> str:
    """Generate text with monitoring."""
    return prompt

# Get Grok-specific metrics
stats = monitor.get_provider_statistics("grok")
print(f"Grok requests: {stats.requests}")
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Total cost: ${stats.total_cost:.4f}")
```

### Cost Tracking

```python
# Track costs by model
cost_by_model = monitor.get_cost_by_model("grok")
for model, cost in cost_by_model.items():
    print(f"{model}: ${cost:.4f}")
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```python
# Check API key format
api_key = "..."  # Should be a valid Grok API key
if not api_key:
    raise ValueError("Grok API key is required")
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

## Comparison with Other Providers

### vs OpenAI

| Feature                   | Grok        | OpenAI          |
| ------------------------- | ----------- | --------------- |
| **Conversational AI**     | Excellent   | Good            |
| **Real-time Information** | Excellent   | Limited         |
| **Code Generation**       | Good        | Excellent       |
| **Cost**                  | Competitive | Varies by model |
| **Speed**                 | Good        | Good            |

### vs Anthropic

| Feature                   | Grok        | Anthropic   |
| ------------------------- | ----------- | ----------- |
| **Conversational AI**     | Excellent   | Good        |
| **Real-time Information** | Excellent   | Limited     |
| **Reasoning**             | Good        | Excellent   |
| **Cost**                  | Competitive | Competitive |
| **Speed**                 | Good        | Good        |

### vs Google

| Feature                   | Grok        | Google           |
| ------------------------- | ----------- | ---------------- |
| **Conversational AI**     | Excellent   | Good             |
| **Real-time Information** | Excellent   | Limited          |
| **Multimodal**            | Limited     | Excellent        |
| **Cost**                  | Competitive | Very competitive |
| **Speed**                 | Good        | Excellent        |

## Use Cases

### Best Use Cases for Grok

1. **Conversational AI Applications**

   - Chatbots and virtual assistants
   - Customer service automation
   - Interactive storytelling

2. **Real-time Information**

   - News analysis and summarization
   - Current events discussion
   - Live data interpretation

3. **Creative Writing**

   - Story generation
   - Content creation
   - Humorous content

4. **Casual Analysis**
   - Opinion pieces
   - Social commentary
   - Trend analysis

### When to Use Other Providers

1. **Technical Code Generation** → Use OpenAI
2. **Complex Reasoning** → Use Anthropic
3. **Multimodal Analysis** → Use Google
4. **Production Systems** → Use multiple providers with fallback

## Next Steps

- [:octicons-plug-24: OpenAI Provider](openai.md) - OpenAI GPT integration
- [:octicons-plug-24: Anthropic Provider](anthropic.md) - Anthropic Claude integration
- [:octicons-plug-24: Google Provider](google.md) - Google Gemini integration
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Provider configuration
