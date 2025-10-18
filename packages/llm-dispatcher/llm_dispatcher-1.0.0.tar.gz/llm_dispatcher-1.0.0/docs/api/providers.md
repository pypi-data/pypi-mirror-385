# Providers API Reference

This page provides comprehensive documentation for the LLM-Dispatcher provider implementations.

## Overview

LLM-Dispatcher supports multiple LLM providers through a unified interface. Each provider implements the `LLMProvider` base class and provides consistent functionality across different services.

## Base Provider Interface

### LLMProvider

The base class that all providers must implement.

```python
from llm_dispatcher.providers.base_provider import LLMProvider
from llm_dispatcher.core.base import TaskRequest, TaskResponse

class LLMProvider:
    """Base class for all LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration."""
        self.config = config
        self.name = config.get("name", "unknown")
        self.models = config.get("models", [])

    async def generate_text(self, request: TaskRequest) -> TaskResponse:
        """Generate text using the provider."""
        raise NotImplementedError

    async def stream_text(self, request: TaskRequest):
        """Stream text generation."""
        raise NotImplementedError

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return self.models

    def get_cost_estimate(self, request: TaskRequest) -> float:
        """Estimate cost for a request."""
        raise NotImplementedError

    def get_latency_estimate(self, request: TaskRequest) -> int:
        """Estimate latency for a request."""
        raise NotImplementedError

    def is_healthy(self) -> bool:
        """Check if the provider is healthy."""
        raise NotImplementedError
```

## Supported Providers

### OpenAI Provider

Integration with OpenAI's GPT models.

```python
from llm_dispatcher.providers.openai_provider import OpenAIProvider

# Initialize OpenAI provider
openai_provider = OpenAIProvider({
    "name": "openai",
    "api_key": "sk-...",
    "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
})
```

#### Configuration Options

| Option           | Type        | Default                      | Description                |
| ---------------- | ----------- | ---------------------------- | -------------------------- |
| `api_key`        | `str`       | Required                     | OpenAI API key             |
| `models`         | `List[str]` | `["gpt-4", "gpt-3.5-turbo"]` | Available models           |
| `max_tokens`     | `int`       | `4096`                       | Maximum tokens per request |
| `temperature`    | `float`     | `0.7`                        | Sampling temperature       |
| `timeout`        | `int`       | `30`                         | Request timeout in seconds |
| `max_retries`    | `int`       | `3`                          | Maximum retry attempts     |
| `cost_per_token` | `float`     | `0.00003`                    | Cost per token             |

#### Methods

##### `generate_text(request: TaskRequest) -> TaskResponse`

```python
from llm_dispatcher.core.base import TaskRequest, TaskType

request = TaskRequest(
    prompt="Write a story about space exploration",
    task_type=TaskType.TEXT_GENERATION,
    max_tokens=1000
)

response = await openai_provider.generate_text(request)
print(response.content)
```

##### `stream_text(request: TaskRequest)`

```python
async for chunk in openai_provider.stream_text(request):
    print(chunk, end="", flush=True)
```

##### `get_cost_estimate(request: TaskRequest) -> float`

```python
cost = openai_provider.get_cost_estimate(request)
print(f"Estimated cost: ${cost:.4f}")
```

### Anthropic Provider

Integration with Anthropic's Claude models.

```python
from llm_dispatcher.providers.anthropic_provider import AnthropicProvider

# Initialize Anthropic provider
anthropic_provider = AnthropicProvider({
    "name": "anthropic",
    "api_key": "sk-ant-...",
    "models": ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus"],
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
})
```

#### Configuration Options

| Option           | Type        | Default                                 | Description                |
| ---------------- | ----------- | --------------------------------------- | -------------------------- |
| `api_key`        | `str`       | Required                                | Anthropic API key          |
| `models`         | `List[str]` | `["claude-3-sonnet", "claude-3-haiku"]` | Available models           |
| `max_tokens`     | `int`       | `4096`                                  | Maximum tokens per request |
| `temperature`    | `float`     | `0.7`                                   | Sampling temperature       |
| `timeout`        | `int`       | `30`                                    | Request timeout in seconds |
| `max_retries`    | `int`       | `3`                                     | Maximum retry attempts     |
| `cost_per_token` | `float`     | `0.000015`                              | Cost per token             |

#### Methods

##### `generate_text(request: TaskRequest) -> TaskResponse`

```python
request = TaskRequest(
    prompt="Explain quantum computing in simple terms",
    task_type=TaskType.TEXT_GENERATION,
    max_tokens=1000
)

response = await anthropic_provider.generate_text(request)
print(response.content)
```

##### `stream_text(request: TaskRequest)`

```python
async for chunk in anthropic_provider.stream_text(request):
    print(chunk, end="", flush=True)
```

### Google Provider

Integration with Google's Gemini models.

```python
from llm_dispatcher.providers.google_provider import GoogleProvider

# Initialize Google provider
google_provider = GoogleProvider({
    "name": "google",
    "api_key": "...",
    "models": ["gemini-2.5-pro", "gemini-2.5-flash"],
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
})
```

#### Configuration Options

| Option           | Type        | Default                                  | Description                |
| ---------------- | ----------- | ---------------------------------------- | -------------------------- |
| `api_key`        | `str`       | Required                                 | Google API key             |
| `models`         | `List[str]` | `["gemini-2.5-pro", "gemini-2.5-flash"]` | Available models           |
| `max_tokens`     | `int`       | `4096`                                   | Maximum tokens per request |
| `temperature`    | `float`     | `0.7`                                    | Sampling temperature       |
| `timeout`        | `int`       | `30`                                     | Request timeout in seconds |
| `max_retries`    | `int`       | `3`                                      | Maximum retry attempts     |
| `cost_per_token` | `float`     | `0.00001`                                | Cost per token             |

#### Methods

##### `generate_text(request: TaskRequest) -> TaskResponse`

```python
request = TaskRequest(
    prompt="Analyze this data and provide insights",
    task_type=TaskType.ANALYSIS,
    max_tokens=1000
)

response = await google_provider.generate_text(request)
print(response.content)
```

### Grok Provider

Integration with xAI's Grok models.

```python
from llm_dispatcher.providers.grok_provider import GrokProvider

# Initialize Grok provider
grok_provider = GrokProvider({
    "name": "grok",
    "api_key": "...",
    "models": ["grok-beta"],
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
})
```

#### Configuration Options

| Option           | Type        | Default         | Description                |
| ---------------- | ----------- | --------------- | -------------------------- |
| `api_key`        | `str`       | Required        | Grok API key               |
| `models`         | `List[str]` | `["grok-beta"]` | Available models           |
| `max_tokens`     | `int`       | `4096`          | Maximum tokens per request |
| `temperature`    | `float`     | `0.7`           | Sampling temperature       |
| `timeout`        | `int`       | `30`            | Request timeout in seconds |
| `max_retries`    | `int`       | `3`             | Maximum retry attempts     |
| `cost_per_token` | `float`     | `0.00002`       | Cost per token             |

## Provider Management

### Adding Providers

```python
from llm_dispatcher import LLMSwitch

# Create switch with multiple providers
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"]
        },
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-sonnet", "claude-3-haiku"]
        },
        "google": {
            "api_key": "...",
            "models": ["gemini-2.5-pro", "gemini-2.5-flash"]
        }
    }
)
```

### Provider Status

```python
# Get provider status
status = switch.get_provider_status()
for provider_name, provider_status in status.items():
    print(f"{provider_name}:")
    print(f"  Status: {provider_status.status}")
    print(f"  Latency: {provider_status.avg_latency}ms")
    print(f"  Success Rate: {provider_status.success_rate:.2%}")
    print(f"  Requests: {provider_status.total_requests}")
```

### Provider Health Checks

```python
# Check individual provider health
for provider_name, provider in switch.providers.items():
    is_healthy = provider.is_healthy()
    print(f"{provider_name}: {'Healthy' if is_healthy else 'Unhealthy'}")
```

## Custom Provider Implementation

### Creating a Custom Provider

```python
from llm_dispatcher.providers.base_provider import LLMProvider
from llm_dispatcher.core.base import TaskRequest, TaskResponse

class CustomProvider(LLMProvider):
    """Custom provider implementation."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.base_url = config.get("base_url", "https://api.custom.com")

    async def generate_text(self, request: TaskRequest) -> TaskResponse:
        """Generate text using custom API."""
        # Implement custom API call
        response_data = await self._call_api(request)

        return TaskResponse(
            content=response_data["text"],
            provider=self.name,
            model=request.model or self.models[0],
            tokens_used=response_data["tokens_used"],
            cost=self.get_cost_estimate(request),
            latency=response_data["latency"],
            metadata={"custom_field": "value"}
        )

    async def stream_text(self, request: TaskRequest):
        """Stream text generation."""
        # Implement streaming
        async for chunk in self._stream_api(request):
            yield chunk

    def get_cost_estimate(self, request: TaskRequest) -> float:
        """Estimate cost for request."""
        # Implement cost calculation
        return len(request.prompt) * 0.00001

    def get_latency_estimate(self, request: TaskRequest) -> int:
        """Estimate latency for request."""
        # Implement latency estimation
        return 1000  # 1 second

    def is_healthy(self) -> bool:
        """Check provider health."""
        # Implement health check
        return True

    async def _call_api(self, request: TaskRequest) -> Dict[str, Any]:
        """Make API call to custom service."""
        # Implementation details
        pass

    async def _stream_api(self, request: TaskRequest):
        """Stream API call to custom service."""
        # Implementation details
        pass
```

### Using Custom Provider

```python
# Register custom provider
switch = LLMSwitch(
    providers={
        "custom": {
            "api_key": "custom-api-key",
            "base_url": "https://api.custom.com",
            "models": ["custom-model-1", "custom-model-2"]
        }
    }
)

# Use custom provider
@llm_dispatcher(providers=["custom"])
def use_custom_provider(prompt: str) -> str:
    """Use custom provider for generation."""
    return prompt
```

## Provider-Specific Features

### OpenAI Features

#### Function Calling

```python
# OpenAI supports function calling
openai_request = TaskRequest(
    prompt="What's the weather like?",
    task_type=TaskType.TEXT_GENERATION,
    functions=[
        {
            "name": "get_weather",
            "description": "Get current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                }
            }
        }
    ]
)

response = await openai_provider.generate_text(openai_request)
```

#### Vision Support

```python
# OpenAI supports vision models
vision_request = TaskRequest(
    prompt="Describe this image",
    task_type=TaskType.VISION_ANALYSIS,
    images=[image_data]
)

response = await openai_provider.generate_text(vision_request)
```

### Anthropic Features

#### System Messages

```python
# Anthropic supports system messages
anthropic_request = TaskRequest(
    prompt="Write a story",
    task_type=TaskType.CREATIVE_WRITING,
    system_message="You are a creative writing assistant."
)

response = await anthropic_provider.generate_text(anthropic_request)
```

#### Tool Use

```python
# Anthropic supports tool use
anthropic_request = TaskRequest(
    prompt="Search for information about AI",
    task_type=TaskType.TEXT_GENERATION,
    tools=[
        {
            "name": "search",
            "description": "Search the web",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                }
            }
        }
    ]
)

response = await anthropic_provider.generate_text(anthropic_request)
```

### Google Features

#### Multimodal Support

```python
# Google supports multimodal inputs
multimodal_request = TaskRequest(
    prompt="Analyze this content",
    task_type=TaskType.MULTIMODAL_ANALYSIS,
    images=[image_data],
    audio=[audio_data]
)

response = await google_provider.generate_text(multimodal_request)
```

## Error Handling

### Provider-Specific Errors

```python
from llm_dispatcher.exceptions import (
    ProviderError,
    ProviderConnectionError,
    ProviderAuthenticationError,
    ProviderRateLimitError
)

try:
    response = await provider.generate_text(request)
except ProviderConnectionError as e:
    print(f"Connection failed: {e}")
except ProviderAuthenticationError as e:
    print(f"Authentication failed: {e}")
except ProviderRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Retry after: {e.retry_after} seconds")
except ProviderError as e:
    print(f"Provider error: {e}")
```

### Retry Logic

```python
from llm_dispatcher.retry import ExponentialBackoff

# Configure retry logic
retry_strategy = ExponentialBackoff(
    base_delay=1,
    max_delay=60,
    multiplier=2
)

@llm_dispatcher(
    max_retries=5,
    retry_strategy=retry_strategy
)
def retry_generation(prompt: str) -> str:
    """Generation with retry logic."""
    return prompt
```

## Performance Optimization

### Provider Selection

```python
def select_best_provider(request: TaskRequest) -> str:
    """Select best provider based on request characteristics."""
    if request.task_type == TaskType.CODE_GENERATION:
        return "openai"  # Best for code
    elif request.task_type == TaskType.REASONING:
        return "anthropic"  # Best for reasoning
    elif request.task_type == TaskType.MULTIMODAL_ANALYSIS:
        return "google"  # Best for multimodal
    else:
        return "auto"  # Let dispatcher decide

@llm_dispatcher(
    providers=select_best_provider
)
def optimized_generation(prompt: str) -> str:
    """Generation with optimized provider selection."""
    return prompt
```

### Load Balancing

```python
from llm_dispatcher.load_balancer import WeightedBalancer

# Configure load balancing
load_balancer = WeightedBalancer(
    weights={
        "openai": 0.4,
        "anthropic": 0.3,
        "google": 0.2,
        "grok": 0.1
    }
)

switch = LLMSwitch(
    providers={...},
    config={
        "load_balancer": load_balancer
    }
)
```

## Best Practices

### 1. **Use Appropriate Providers for Tasks**

```python
# Good: Use specific providers for specific tasks
@llm_dispatcher(providers=["openai"])
def generate_code(description: str) -> str:
    return description

@llm_dispatcher(providers=["anthropic"])
def creative_writing(prompt: str) -> str:
    return prompt

# Avoid: Using all providers for all tasks
@llm_dispatcher
def generate_code(description: str) -> str:
    return description
```

### 2. **Configure Provider-Specific Settings**

```python
# Good: Configure providers with appropriate settings
providers = {
    "openai": {
        "api_key": "sk-...",
        "models": ["gpt-4", "gpt-3.5-turbo"],
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "anthropic": {
        "api_key": "sk-ant-...",
        "models": ["claude-3-sonnet", "claude-3-haiku"],
        "max_tokens": 4096,
        "temperature": 0.7
    }
}

# Avoid: Using default settings for all providers
providers = {
    "openai": {"api_key": "sk-..."},
    "anthropic": {"api_key": "sk-ant-..."}
}
```

### 3. **Monitor Provider Performance**

```python
# Good: Monitor provider performance
def monitor_providers():
    status = switch.get_provider_status()
    for provider_name, provider_status in status.items():
        if provider_status.success_rate < 0.95:
            logger.warning(f"{provider_name} success rate below threshold")
        if provider_status.avg_latency > 5000:
            logger.warning(f"{provider_name} latency too high")

# Call periodically
monitor_providers()
```

### 4. **Handle Provider Failures Gracefully**

```python
# Good: Enable fallbacks for reliability
@llm_dispatcher(
    fallback_enabled=True,
    max_retries=3
)
def reliable_generation(prompt: str) -> str:
    return prompt

# Avoid: No fallback configuration
@llm_dispatcher
def unreliable_generation(prompt: str) -> str:
    return prompt
```

### 5. **Use Provider-Specific Features**

```python
# Good: Use provider-specific features
@llm_dispatcher(providers=["openai"])
def function_calling(prompt: str) -> str:
    # Use OpenAI's function calling
    return prompt

@llm_dispatcher(providers=["anthropic"])
def system_message(prompt: str) -> str:
    # Use Anthropic's system messages
    return prompt
```

## Next Steps

- [:octicons-puzzle-24: Core API](core.md) - Core API reference
- [:octicons-puzzle-24: Decorators](decorators.md) - Decorator API reference
- [:octicons-exclamation-triangle-24: Exceptions](exceptions.md) - Exception handling
- [:octicons-gear-24: Configuration](configuration.md) - Configuration options
