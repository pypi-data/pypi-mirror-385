# Providers Overview

LLM-Dispatcher supports multiple LLM providers through a unified interface, allowing you to easily switch between different AI models and services.

## Supported Providers

### OpenAI

- **Models**: GPT-4, GPT-3.5-turbo, GPT-4-turbo, GPT-4-vision
- **Features**: Function calling, vision support, streaming
- **Best for**: Code generation, general purpose tasks
- **Cost**: $0.03/1K tokens (GPT-4), $0.0015/1K tokens (GPT-3.5-turbo)

### Anthropic

- **Models**: Claude-3 Opus, Claude-3 Sonnet, Claude-3 Haiku
- **Features**: System messages, tool use, large context windows
- **Best for**: Reasoning, creative writing, analysis
- **Cost**: $0.015/1K tokens (Opus), $0.003/1K tokens (Sonnet)

### Google

- **Models**: Gemini 2.5 Pro, Gemini 2.5 Flash
- **Features**: Multimodal support, large context windows
- **Best for**: Multimodal tasks, cost-effective alternatives
- **Cost**: $0.00125/1K tokens (Pro), $0.000075/1K tokens (Flash)

### Grok

- **Models**: Grok Beta
- **Features**: Real-time information, conversational AI
- **Best for**: Current events, conversational applications
- **Cost**: $0.002/1K tokens

## Provider Selection

### Automatic Selection

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher  # Automatically selects best provider
def generate_text(prompt: str) -> str:
    return prompt
```

### Manual Selection

```python
@llm_dispatcher(providers=["openai"])
def generate_with_openai(prompt: str) -> str:
    return prompt

@llm_dispatcher(providers=["anthropic"])
def generate_with_anthropic(prompt: str) -> str:
    return prompt
```

### Task-Based Selection

```python
def select_provider_for_task(prompt: str) -> str:
    if "code" in prompt.lower():
        return "openai"  # Best for code generation
    elif "creative" in prompt.lower():
        return "anthropic"  # Best for creative tasks
    else:
        return "auto"  # Let dispatcher decide

@llm_dispatcher(providers=select_provider_for_task)
def smart_generation(prompt: str) -> str:
    return prompt
```

## Provider Configuration

### Basic Configuration

```python
from llm_dispatcher import LLMSwitch

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
    }
)
```

### Advanced Configuration

```python
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3
        }
    },
    config={
        "optimization_strategy": "balanced",
        "fallback_enabled": True
    }
)
```

## Provider Comparison

| Feature              | OpenAI     | Anthropic  | Google     | Grok     |
| -------------------- | ---------- | ---------- | ---------- | -------- |
| **Code Generation**  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐   |
| **Creative Writing** | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐ |
| **Reasoning**        | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐   |
| **Multimodal**       | ⭐⭐⭐⭐   | ⭐⭐       | ⭐⭐⭐⭐⭐ | ⭐⭐     |
| **Cost**             | ⭐⭐⭐     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed**            | ⭐⭐⭐⭐   | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

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
    }
}

# Avoid: Using default settings for all providers
providers = {
    "openai": {"api_key": "sk-..."}
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

# Avoid: No monitoring
# No monitoring setup
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

- [:octicons-plug-24: OpenAI Provider](openai.md) - OpenAI GPT integration
- [:octicons-plug-24: Anthropic Provider](anthropic.md) - Anthropic Claude integration
- [:octicons-plug-24: Google Provider](google.md) - Google Gemini integration
- [:octicons-plug-24: Grok Provider](grok.md) - xAI Grok integration
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Provider configuration
