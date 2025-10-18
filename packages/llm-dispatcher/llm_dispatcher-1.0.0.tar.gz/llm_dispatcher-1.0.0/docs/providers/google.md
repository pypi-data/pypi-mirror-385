# Google Provider

The Google provider integrates with Google's Gemini models, providing access to Gemini 2.5 Pro, Gemini 2.5 Flash, and other Google AI models.

## Overview

The Google provider offers:

- **Multimodal capabilities** with text, image, and audio support
- **Large context windows** up to 128K tokens
- **Cost-effective** pricing
- **Fast response times** with Gemini Flash
- **Advanced reasoning** with Gemini Pro

## Configuration

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={
        "google": {
            "api_key": "...",
            "models": ["gemini-2.5-pro", "gemini-2.5-flash"]
        }
    }
)
```

### Advanced Configuration

```python
switch = LLMSwitch(
    providers={
        "google": {
            "api_key": "...",
            "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.00001,
            "safety_settings": {
                "harassment": "BLOCK_MEDIUM_AND_ABOVE",
                "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
                "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
                "sexual_content": "BLOCK_MEDIUM_AND_ABOVE"
            }
        }
    }
)
```

### Environment Variables

```bash
export GOOGLE_API_KEY="..."
export GOOGLE_PROJECT_ID="your-project-id"
```

## Supported Models

### Gemini Models

| Model              | Description                     | Max Tokens | Cost per 1K Tokens                  |
| ------------------ | ------------------------------- | ---------- | ----------------------------------- |
| `gemini-2.5-pro`   | Most capable Gemini model       | 128,000    | $0.00125 (input), $0.005 (output)   |
| `gemini-2.5-flash` | Fast and efficient model        | 128,000    | $0.000075 (input), $0.0003 (output) |
| `gemini-1.5-pro`   | Previous generation Pro model   | 128,000    | $0.00125 (input), $0.005 (output)   |
| `gemini-1.5-flash` | Previous generation Flash model | 128,000    | $0.000075 (input), $0.0003 (output) |

## Usage Examples

### Basic Text Generation

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType

@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"]
)
def generate_text(prompt: str) -> str:
    """Generate text using Gemini 2.5 Pro."""
    return prompt

result = generate_text("Explain machine learning in simple terms")
print(result)
```

### Multimodal Analysis

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    task_type=TaskType.MULTIMODAL_ANALYSIS
)
def analyze_multimodal(prompt: str, images: list = None, audio: list = None) -> str:
    """Analyze multimodal content using Gemini."""
    return prompt

# Analyze image
image_data = encode_image("path/to/image.jpg")
result = analyze_multimodal("Describe this image", images=[image_data])
print(result)

# Analyze audio
audio_data = encode_audio("path/to/audio.mp3")
result = analyze_multimodal("Transcribe this audio", audio=[audio_data])
print(result)
```

### Vision Analysis

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    task_type=TaskType.VISION_ANALYSIS
)
def analyze_image(prompt: str, images: list) -> str:
    """Analyze images using Gemini Vision."""
    return prompt

# Analyze single image
image_data = encode_image("path/to/image.jpg")
result = analyze_image("What do you see in this image?", [image_data])
print(result)

# Analyze multiple images
images = [encode_image("image1.jpg"), encode_image("image2.jpg")]
result = analyze_image("Compare these two images", images)
print(result)
```

### Audio Transcription

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    task_type=TaskType.AUDIO_TRANSCRIPTION
)
def transcribe_audio(prompt: str, audio: str) -> str:
    """Transcribe audio using Gemini."""
    return prompt

audio_data = encode_audio("path/to/audio.mp3")
result = transcribe_audio("Transcribe this audio", audio_data)
print(result)
```

### Code Generation

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    task_type=TaskType.CODE_GENERATION
)
def generate_code(description: str) -> str:
    """Generate code using Gemini."""
    return description

code = generate_code("Create a Python function to sort a list")
print(code)
```

### Streaming Responses

```python
from llm_dispatcher import llm_stream

@llm_stream(
    providers=["google"],
    models=["gemini-2.5-flash"]
)
async def stream_text(prompt: str):
    """Stream text generation using Gemini Flash."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["This is a streaming response from Gemini. ", "Each chunk is delivered as it becomes available. ", "This provides a better user experience."]
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
    providers=["google"],
    models=["gemini-2.5-pro"],
    temperature=0.1,  # Low temperature for consistent output
    max_tokens=2000,
    top_p=0.9,
    top_k=40
)
def generate_with_custom_params(prompt: str) -> str:
    """Generate text with custom parameters."""
    return prompt

result = generate_with_custom_params("Write a technical explanation")
```

### Safety Settings

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    safety_settings={
        "harassment": "BLOCK_MEDIUM_AND_ABOVE",
        "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
        "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE",
        "sexual_content": "BLOCK_MEDIUM_AND_ABOVE"
    }
)
def safe_generation(prompt: str) -> str:
    """Generate text with safety settings."""
    return prompt

result = safe_generation("Write a story")
```

### Multiple Models

```python
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro", "gemini-2.5-flash"]
)
def multi_model_generation(prompt: str) -> str:
    """Generate text using multiple Gemini models."""
    return prompt

result = multi_model_generation("Write a creative story")
```

### Model Selection Based on Task

```python
def select_gemini_model(prompt: str) -> str:
    """Select best Gemini model based on prompt."""
    if "image" in prompt.lower() or "audio" in prompt.lower():
        return "gemini-2.5-pro"  # Best for multimodal
    elif "complex" in prompt.lower() or "analysis" in prompt.lower():
        return "gemini-2.5-pro"  # Best for complex tasks
    else:
        return "gemini-2.5-flash"  # Fast and cost-effective

@llm_dispatcher(
    providers=["google"],
    models=select_gemini_model
)
def optimized_generation(prompt: str) -> str:
    """Generate text with optimized model selection."""
    return prompt
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
    providers=["google"],
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
    providers=["google"],
    models=["gemini-2.5-flash"],  # Use cheapest model
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
    providers=["google"],
    models=["gemini-2.5-flash"],  # Fastest model
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
    providers=["google"],
    models=["gemini-2.5-pro"],  # Highest quality model
    max_tokens=2000,  # Allow longer responses
    temperature=0.1  # Low temperature for consistency
)
def quality_optimized_generation(prompt: str) -> str:
    """Generate text with quality optimization."""
    return prompt
```

## Best Practices

### 1. **Use Appropriate Models for Tasks**

```python
# Good: Use Gemini Pro for complex multimodal tasks
@llm_dispatcher(providers=["google"], models=["gemini-2.5-pro"])
def multimodal_analysis(prompt: str, images: list) -> str:
    return prompt

# Good: Use Gemini Flash for simple text tasks
@llm_dispatcher(providers=["google"], models=["gemini-2.5-flash"])
def simple_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for simple tasks
@llm_dispatcher(providers=["google"], models=["gemini-2.5-pro"])
def simple_generation(prompt: str) -> str:
    return prompt
```

### 2. **Leverage Multimodal Capabilities**

```python
# Good: Use multimodal features when available
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    task_type=TaskType.MULTIMODAL_ANALYSIS
)
def analyze_content(prompt: str, images: list, audio: list) -> str:
    return prompt

# Avoid: Not using multimodal features when they would be beneficial
@llm_dispatcher(providers=["google"])
def analyze_content(prompt: str, images: list, audio: list) -> str:
    return prompt
```

### 3. **Configure Safety Settings**

```python
# Good: Configure appropriate safety settings
@llm_dispatcher(
    providers=["google"],
    safety_settings={
        "harassment": "BLOCK_MEDIUM_AND_ABOVE",
        "hate_speech": "BLOCK_MEDIUM_AND_ABOVE"
    }
)
def safe_generation(prompt: str) -> str:
    return prompt

# Avoid: Not configuring safety settings
@llm_dispatcher(providers=["google"])
def safe_generation(prompt: str) -> str:
    return prompt
```

### 4. **Optimize for Cost**

```python
# Good: Use cost-effective models for bulk operations
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-flash"],
    max_tokens=500
)
def bulk_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for bulk operations
@llm_dispatcher(
    providers=["google"],
    models=["gemini-2.5-pro"],
    max_tokens=2000
)
def bulk_generation(prompt: str) -> str:
    return prompt
```

### 5. **Handle Errors Gracefully**

```python
# Good: Handle Google-specific errors
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
    providers=["google"],
    monitor=monitor
)
def monitored_generation(prompt: str) -> str:
    """Generate text with monitoring."""
    return prompt

# Get Google-specific metrics
stats = monitor.get_provider_statistics("google")
print(f"Google requests: {stats.requests}")
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Total cost: ${stats.total_cost:.4f}")
```

### Cost Tracking

```python
# Track costs by model
cost_by_model = monitor.get_cost_by_model("google")
for model, cost in cost_by_model.items():
    print(f"{model}: ${cost:.4f}")
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```python
# Check API key format
api_key = "..."  # Should be a valid Google API key
if not api_key:
    raise ValueError("Google API key is required")
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
def truncate_prompt(prompt: str, max_length: int = 100000) -> str:
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

| Feature             | Google           | OpenAI          |
| ------------------- | ---------------- | --------------- |
| **Multimodal**      | Excellent        | Good            |
| **Context Length**  | 128K tokens      | 8K-128K tokens  |
| **Cost**            | Very competitive | Varies by model |
| **Speed**           | Excellent        | Good            |
| **Code Generation** | Good             | Excellent       |

### vs Anthropic

| Feature            | Google           | Anthropic   |
| ------------------ | ---------------- | ----------- |
| **Multimodal**     | Excellent        | Limited     |
| **Context Length** | 128K tokens      | 200K tokens |
| **Cost**           | Very competitive | Competitive |
| **Speed**          | Excellent        | Good        |
| **Reasoning**      | Good             | Excellent   |

## Next Steps

- [:octicons-plug-24: OpenAI Provider](openai.md) - OpenAI GPT integration
- [:octicons-plug-24: Anthropic Provider](anthropic.md) - Anthropic Claude integration
- [:octicons-plug-24: Grok Provider](grok.md) - xAI Grok integration
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Provider configuration
