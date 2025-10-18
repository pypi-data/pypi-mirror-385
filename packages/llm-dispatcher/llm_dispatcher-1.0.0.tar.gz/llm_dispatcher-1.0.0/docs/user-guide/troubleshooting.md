# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with LLM-Dispatcher.

## Common Issues

### Installation Issues

#### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'llm_dispatcher'`

**Solutions**:

```bash
# Make sure the package is installed
pip install llm-dispatcher

# Or install from source
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"

# Verify installation
python -c "import llm_dispatcher; print(llm_dispatcher.__version__)"
```

#### Version Conflicts

**Problem**: Version conflicts with dependencies

**Solutions**:

```bash
# Create a clean virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with specific versions
pip install llm-dispatcher==0.1.0

# Check for conflicts
pip check
```

### Configuration Issues

#### API Key Problems

**Problem**: `AuthenticationError: Invalid API key`

**Solutions**:

```python
# Check API key format
import os
api_key = os.getenv("OPENAI_API_KEY")
print(f"API key format: {api_key[:10]}..." if api_key else "No API key found")

# Verify API key is set
from llm_dispatcher import LLMSwitch

try:
    switch = LLMSwitch(
        providers={
            "openai": {"api_key": "your-key-here"}
        }
    )
    print("Configuration successful")
except Exception as e:
    print(f"Configuration error: {e}")
```

#### Provider Configuration

**Problem**: `ProviderError: Provider not configured`

**Solutions**:

```python
# Check provider configuration
switch = LLMSwitch(providers={})
print(f"Available providers: {list(switch.providers.keys())}")

# Add missing provider
switch.add_provider("openai", {
    "api_key": "your-key",
    "models": ["gpt-4", "gpt-3.5-turbo"]
})
```

### Runtime Issues

#### Connection Timeouts

**Problem**: `TimeoutError: Request timed out`

**Solutions**:

```python
# Increase timeout
switch = LLMSwitch(
    providers={...},
    config={
        "request_timeout": 60,  # 60 seconds
        "max_retries": 3
    }
)

# Check network connectivity
import requests
try:
    response = requests.get("https://api.openai.com/v1/models", timeout=10)
    print("Network connectivity OK")
except Exception as e:
    print(f"Network issue: {e}")
```

#### Rate Limiting

**Problem**: `RateLimitError: Rate limit exceeded`

**Solutions**:

```python
# Implement rate limiting
from llm_dispatcher import LLMSwitch
import asyncio

switch = LLMSwitch(
    providers={...},
    config={
        "rate_limit": {
            "requests_per_minute": 60,
            "tokens_per_minute": 40000
        }
    }
)

# Add delays between requests
async def rate_limited_request(prompt):
    await asyncio.sleep(1)  # 1 second delay
    return await switch.process_request(prompt)
```

#### Memory Issues

**Problem**: `MemoryError: Unable to allocate memory`

**Solutions**:

```python
# Monitor memory usage
import psutil
import os

def check_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")

    if memory_mb > 1000:  # 1GB threshold
        print("High memory usage detected")

# Use streaming for large responses
@switch.route(stream=True)
async def stream_large_response(prompt):
    async for chunk in switch.stream_request(prompt):
        yield chunk
```

### Provider-Specific Issues

#### OpenAI Issues

**Problem**: `OpenAIError: Invalid model`

**Solutions**:

```python
# Check available models
from llm_dispatcher.providers.openai_provider import OpenAIProvider

provider = OpenAIProvider({"api_key": "your-key"})
models = provider.get_available_models()
print(f"Available models: {models}")

# Use correct model name
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "your-key",
            "models": ["gpt-4", "gpt-3.5-turbo"]  # Correct model names
        }
    }
)
```

#### Anthropic Issues

**Problem**: `AnthropicError: Invalid API key`

**Solutions**:

```python
# Verify Anthropic API key format
api_key = "sk-ant-api03-..."
if not api_key.startswith("sk-ant-"):
    print("Invalid Anthropic API key format")

# Check API key permissions
from anthropic import Anthropic
client = Anthropic(api_key="your-key")
try:
    models = client.models.list()
    print("API key is valid")
except Exception as e:
    print(f"API key error: {e}")
```

#### Google Issues

**Problem**: `GoogleError: Project not found`

**Solutions**:

```python
# Check Google Cloud configuration
import os
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

# Verify project ID
from google.cloud import aiplatform
try:
    project_id = "your-project-id"
    aiplatform.init(project=project_id)
    print("Google Cloud configuration OK")
except Exception as e:
    print(f"Google Cloud error: {e}")
```

### Performance Issues

#### Slow Response Times

**Problem**: Responses are slower than expected

**Solutions**:

```python
# Check provider selection
decision = await switch.select_llm(request)
print(f"Selected provider: {decision.provider}")
print(f"Estimated latency: {decision.estimated_latency}ms")

# Use faster models
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "your-key",
            "models": ["gpt-3.5-turbo"],  # Faster than gpt-4
            "prefer_fast_models": True
        }
    }
)

# Enable caching
from llm_dispatcher.cache import TTLCache
cache = TTLCache(ttl=3600)  # 1 hour cache

@switch.route(cache=cache)
def cached_generation(prompt):
    return prompt
```

#### High Costs

**Problem**: Unexpected high costs

**Solutions**:

```python
# Monitor costs
metrics = switch.get_cost_metrics()
print(f"Total cost: ${metrics.total_cost:.4f}")
print(f"Cost per request: ${metrics.avg_cost:.4f}")

# Set cost limits
switch = LLMSwitch(
    providers={...},
    config={
        "max_cost_per_request": 0.01,  # $0.01 limit
        "daily_budget": 10.0,  # $10 daily limit
        "cost_optimization": True
    }
)

# Use cheaper models
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "your-key",
            "models": ["gpt-3.5-turbo"],  # Cheaper than gpt-4
            "prefer_cost_efficiency": True
        }
    }
)
```

### Error Handling Issues

#### Unhandled Exceptions

**Problem**: Exceptions not being caught properly

**Solutions**:

```python
# Implement proper error handling
from llm_dispatcher.exceptions import (
    LLMDispatcherError,
    ProviderError,
    RateLimitError,
    TimeoutError
)

try:
    result = await switch.process_request(request)
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    # Implement backoff strategy
    await asyncio.sleep(60)
except TimeoutError as e:
    print(f"Request timed out: {e}")
    # Retry with longer timeout
except ProviderError as e:
    print(f"Provider error: {e}")
    # Try fallback provider
except LLMDispatcherError as e:
    print(f"LLM-Dispatcher error: {e}")
    # Handle general errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

#### Fallback Not Working

**Problem**: Fallback providers not being used

**Solutions**:

```python
# Check fallback configuration
switch = LLMSwitch(
    providers={...},
    config={
        "fallback_enabled": True,
        "fallback_providers": ["anthropic", "google"],
        "max_fallback_attempts": 3
    }
)

# Test fallback manually
try:
    result = await switch.process_request(request)
except Exception as e:
    print(f"Primary provider failed: {e}")
    # Manually try fallback
    for provider_name in switch.config.fallback_providers:
        try:
            result = await switch.providers[provider_name].process_request(request)
            print(f"Fallback successful with {provider_name}")
            break
        except Exception as fallback_error:
            print(f"Fallback {provider_name} failed: {fallback_error}")
```

### Debugging

#### Enable Debug Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("llm_dispatcher")

# Or configure specific loggers
logging.getLogger("llm_dispatcher.providers").setLevel(logging.DEBUG)
logging.getLogger("llm_dispatcher.core").setLevel(logging.DEBUG)
```

#### Debug Mode

```python
# Enable debug mode
switch = LLMSwitch(
    providers={...},
    config={
        "debug": True,
        "log_level": "DEBUG",
        "log_requests": True,
        "log_responses": True
    }
)
```

#### Request Tracing

```python
# Trace request flow
@switch.route
def traced_generation(prompt):
    print(f"Processing request: {prompt}")
    result = prompt
    print(f"Generated response: {result}")
    return result

# Or use decorator
from llm_dispatcher.decorators import trace_requests

@trace_requests
@switch.route
def traced_generation(prompt):
    return prompt
```

### Getting Help

#### Check Documentation

1. **API Reference**: Check the [API Reference](../api/core.md) for detailed information
2. **Examples**: Look at [Examples](../getting-started/examples.md) for usage patterns
3. **Configuration**: Review [Configuration Guide](../getting-started/configuration.md)

#### Community Support

1. **GitHub Issues**: [Report bugs and request features](https://github.com/ashhadahsan/llm-dispatcher/issues)
2. **Discussions**: [Ask questions and share ideas](https://github.com/ashhadahsan/llm-dispatcher/discussions)
3. **Discord**: [Join our Discord community](https://discord.gg/llm-dispatcher)

#### Professional Support

- **Email**: ashhadahsan@mail.com
- **Enterprise Support**: Available for enterprise customers
- **Consulting**: Custom implementation and optimization services

### Diagnostic Tools

#### System Information

```python
# Get system information
import platform
import sys
import llm_dispatcher

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"LLM-Dispatcher version: {llm_dispatcher.__version__}")

# Check dependencies
import pkg_resources
for package in ["openai", "anthropic", "google-cloud-aiplatform"]:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"{package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"{package}: Not installed")
```

#### Health Check

```python
# Run health check
async def health_check():
    switch = LLMSwitch(providers={...})

    # Check providers
    for provider_name, provider in switch.providers.items():
        try:
            health = await provider.health_check()
            print(f"{provider_name}: {health.status}")
        except Exception as e:
            print(f"{provider_name}: Error - {e}")

    # Check configuration
    config = switch.get_config()
    print(f"Configuration: {config}")

    # Check metrics
    metrics = switch.get_metrics()
    print(f"Metrics: {metrics}")

# Run health check
await health_check()
```

#### Performance Profiling

```python
# Profile performance
import cProfile
import pstats

def profile_function():
    # Your code here
    pass

# Run profiler
cProfile.run('profile_function()', 'profile_output.prof')

# Analyze results
stats = pstats.Stats('profile_output.prof')
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 functions
```

## Prevention

### Best Practices

1. **Always use error handling**
2. **Set appropriate timeouts**
3. **Monitor costs and usage**
4. **Use caching when appropriate**
5. **Test with small requests first**
6. **Keep dependencies updated**
7. **Use virtual environments**
8. **Document your configuration**

### Monitoring

```python
# Set up monitoring
from llm_dispatcher.monitoring import MetricsCollector

collector = MetricsCollector()
collector.start_monitoring()

# Check metrics regularly
metrics = collector.get_metrics()
if metrics.error_rate > 0.1:  # 10% error rate
    print("High error rate detected")
if metrics.avg_latency > 5000:  # 5 seconds
    print("High latency detected")
```

## Next Steps

- [:octicons-shield-check-24: Error Handling](error-handling.md) - Comprehensive error handling guide
- [:octicons-chart-line-24: Performance Tips](performance.md) - Performance optimization
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Advanced configuration options
- [:octicons-book-24: API Reference](../api/core.md) - Complete API documentation
