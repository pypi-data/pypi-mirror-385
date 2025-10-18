# Anthropic Provider

The Anthropic provider integrates with Anthropic's Claude models, providing access to Claude-3 Sonnet, Claude-3 Haiku, and Claude-3 Opus.

## Overview

The Anthropic provider offers:

- **High-quality reasoning** with Claude-3 models
- **System messages** for better context control
- **Tool use** capabilities for structured interactions
- **Streaming responses** for real-time generation
- **Cost-effective** alternatives to GPT-4

## Configuration

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-sonnet", "claude-3-haiku"]
        }
    }
)
```

### Advanced Configuration

```python
switch = LLMSwitch(
    providers={
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "cost_per_token": 0.000015,
            "anthropic_version": "2023-06-01"  # API version
        }
    }
)
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export ANTHROPIC_VERSION="2023-06-01"
```

## Supported Models

### Claude-3 Models

| Model             | Description                     | Max Tokens | Cost per 1K Tokens                  |
| ----------------- | ------------------------------- | ---------- | ----------------------------------- |
| `claude-3-opus`   | Most capable Claude-3 model     | 200,000    | $0.015 (input), $0.075 (output)     |
| `claude-3-sonnet` | Balanced performance and cost   | 200,000    | $0.003 (input), $0.015 (output)     |
| `claude-3-haiku`  | Fastest and most cost-effective | 200,000    | $0.00025 (input), $0.00125 (output) |

## Usage Examples

### Basic Text Generation

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.core.base import TaskType

@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-sonnet"]
)
def generate_text(prompt: str) -> str:
    """Generate text using Claude-3 Sonnet."""
    return prompt

result = generate_text("Explain quantum computing in simple terms")
print(result)
```

### Reasoning Tasks

```python
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-opus"],
    task_type=TaskType.REASONING
)
def solve_problem(problem: str) -> str:
    """Solve complex problems using Claude-3 Opus."""
    return problem

solution = solve_problem("Solve this math problem: 2x + 5 = 15")
print(solution)
```

### Creative Writing

```python
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-sonnet"],
    task_type=TaskType.CREATIVE_WRITING,
    temperature=0.8
)
def creative_writing(prompt: str) -> str:
    """Generate creative content using Claude-3 Sonnet."""
    return prompt

story = creative_writing("Write a poem about the ocean")
print(story)
```

### System Messages

```python
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-sonnet"],
    system_message="You are a helpful assistant that specializes in technical writing and explanations."
)
def technical_explanation(prompt: str) -> str:
    """Generate technical explanations with system message."""
    return prompt

explanation = technical_explanation("Explain how machine learning works")
print(explanation)
```

### Tool Use

```python
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-sonnet"],
    tools=[
        {
            "name": "search",
            "description": "Search the web for information",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "calculate",
            "description": "Perform mathematical calculations",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    ]
)
def tool_use_example(prompt: str) -> str:
    """Use tools with Claude-3."""
    return prompt

result = tool_use_example("Search for information about AI and calculate 2^10")
print(result)
```

### Streaming Responses

```python
from llm_dispatcher import llm_stream

@llm_stream(
    providers=["anthropic"],
    models=["claude-3-sonnet"]
)
async def stream_text(prompt: str):
    """Stream text generation using Claude-3 Sonnet."""
    # This is a placeholder - actual streaming would be handled internally
    chunks = ["This is a streaming response from Claude-3. ", "Each chunk is delivered as it becomes available. ", "This provides a better user experience."]
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
    providers=["anthropic"],
    models=["claude-3-sonnet"],
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

### Multiple Models

```python
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
)
def multi_model_generation(prompt: str) -> str:
    """Generate text using multiple Claude models."""
    return prompt

result = multi_model_generation("Write a creative story")
```

### Model Selection Based on Task

```python
def select_claude_model(prompt: str) -> str:
    """Select best Claude model based on prompt."""
    if "complex" in prompt.lower() or "reasoning" in prompt.lower():
        return "claude-3-opus"  # Best for complex reasoning
    elif "creative" in prompt.lower() or "story" in prompt.lower():
        return "claude-3-sonnet"  # Good for creative tasks
    else:
        return "claude-3-haiku"  # Fast and cost-effective

@llm_dispatcher(
    providers=["anthropic"],
    models=select_claude_model
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
    # Check API key format (should start with 'sk-ant-')
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
    providers=["anthropic"],
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
    providers=["anthropic"],
    models=["claude-3-haiku"],  # Use cheapest model
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
    providers=["anthropic"],
    models=["claude-3-haiku"],  # Fastest model
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
    providers=["anthropic"],
    models=["claude-3-opus"],  # Highest quality model
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
# Good: Use Claude-3 Opus for complex reasoning
@llm_dispatcher(providers=["anthropic"], models=["claude-3-opus"])
def complex_reasoning(prompt: str) -> str:
    return prompt

# Good: Use Claude-3 Haiku for simple tasks
@llm_dispatcher(providers=["anthropic"], models=["claude-3-haiku"])
def simple_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for simple tasks
@llm_dispatcher(providers=["anthropic"], models=["claude-3-opus"])
def simple_generation(prompt: str) -> str:
    return prompt
```

### 2. **Leverage System Messages**

```python
# Good: Use system messages for context
@llm_dispatcher(
    providers=["anthropic"],
    system_message="You are a helpful coding assistant."
)
def code_help(prompt: str) -> str:
    return prompt

# Avoid: Not using system messages when they would be helpful
@llm_dispatcher(providers=["anthropic"])
def code_help(prompt: str) -> str:
    return prompt
```

### 3. **Use Tool Use for Structured Tasks**

```python
# Good: Use tools for structured data
@llm_dispatcher(
    providers=["anthropic"],
    tools=[search_tool, calculate_tool]
)
def structured_task(prompt: str) -> str:
    return prompt

# Avoid: Not using tools when they would be beneficial
@llm_dispatcher(providers=["anthropic"])
def structured_task(prompt: str) -> str:
    return prompt
```

### 4. **Optimize for Cost**

```python
# Good: Use cost-effective models for bulk operations
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-haiku"],
    max_tokens=500
)
def bulk_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for bulk operations
@llm_dispatcher(
    providers=["anthropic"],
    models=["claude-3-opus"],
    max_tokens=2000
)
def bulk_generation(prompt: str) -> str:
    return prompt
```

### 5. **Handle Errors Gracefully**

```python
# Good: Handle Anthropic-specific errors
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
    providers=["anthropic"],
    monitor=monitor
)
def monitored_generation(prompt: str) -> str:
    """Generate text with monitoring."""
    return prompt

# Get Anthropic-specific metrics
stats = monitor.get_provider_statistics("anthropic")
print(f"Anthropic requests: {stats.requests}")
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Total cost: ${stats.total_cost:.4f}")
```

### Cost Tracking

```python
# Track costs by model
cost_by_model = monitor.get_cost_by_model("anthropic")
for model, cost in cost_by_model.items():
    print(f"{model}: ${cost:.4f}")
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```python
# Check API key format
api_key = "sk-ant-..."  # Should start with 'sk-ant-'
if not api_key.startswith("sk-ant-"):
    raise ValueError("Invalid Anthropic API key format")
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

| Feature              | Anthropic      | OpenAI           |
| -------------------- | -------------- | ---------------- |
| **Reasoning**        | Excellent      | Good             |
| **Creative Writing** | Excellent      | Good             |
| **Code Generation**  | Good           | Excellent        |
| **Function Calling** | Tool Use       | Function Calling |
| **System Messages**  | Native Support | Limited          |
| **Cost**             | Competitive    | Varies by model  |

### vs Google

| Feature            | Anthropic   | Google           |
| ------------------ | ----------- | ---------------- |
| **Reasoning**      | Excellent   | Good             |
| **Multimodal**     | Limited     | Excellent        |
| **Context Length** | 200K tokens | 128K tokens      |
| **Cost**           | Competitive | Very competitive |
| **Speed**          | Good        | Excellent        |

## Next Steps

- [:octicons-plug-24: OpenAI Provider](openai.md) - OpenAI GPT integration
- [:octicons-plug-24: Google Provider](google.md) - Google Gemini integration
- [:octicons-plug-24: Grok Provider](grok.md) - xAI Grok integration
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Provider configuration
