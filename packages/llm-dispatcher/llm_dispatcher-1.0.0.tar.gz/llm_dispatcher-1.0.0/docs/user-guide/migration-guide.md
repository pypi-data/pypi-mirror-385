# Migration Guide

This guide helps you migrate from other LLM libraries to LLM-Dispatcher.

## From OpenAI Python Library

### Basic Migration

**Before (OpenAI)**:

```python
import openai

client = openai.OpenAI(api_key="your-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello, world!"}]
)

print(response.choices[0].message.content)
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    return prompt

result = generate_text("Hello, world!")
print(result)
```

### Advanced Migration

**Before (OpenAI with custom logic)**:

```python
import openai
import asyncio

async def generate_with_fallback(prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"GPT-4 failed: {e}")
        # Fallback to GPT-3.5
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

result = await generate_with_fallback("Hello, world!")
```

**After (LLM-Dispatcher with automatic fallback)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4", "gpt-3.5-turbo"],
    fallback_enabled=True
)
def generate_with_fallback(prompt: str) -> str:
    return prompt

result = generate_with_fallback("Hello, world!")
```

## From Anthropic Python Library

### Basic Migration

**Before (Anthropic)**:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello, world!"}]
)

print(response.content[0].text)
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(providers=["anthropic"])
def generate_text(prompt: str) -> str:
    return prompt

result = generate_text("Hello, world!")
print(result)
```

### Streaming Migration

**Before (Anthropic streaming)**:

```python
import anthropic

client = anthropic.Anthropic(api_key="your-key")

stream = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Hello, world!"}],
    stream=True
)

for event in stream:
    if event.type == "content_block_delta":
        print(event.delta.text, end="")
```

**After (LLM-Dispatcher streaming)**:

```python
from llm_dispatcher import llm_stream

@llm_stream(providers=["anthropic"])
async def stream_text(prompt: str):
    # Streaming is handled automatically
    yield prompt

async def main():
    async for chunk in stream_text("Hello, world!"):
        print(chunk, end="")

import asyncio
asyncio.run(main())
```

## From Google AI Python Library

### Basic Migration

**Before (Google AI)**:

```python
import google.generativeai as genai

genai.configure(api_key="your-key")
model = genai.GenerativeModel('gemini-pro')

response = model.generate_content("Hello, world!")
print(response.text)
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(providers=["google"])
def generate_text(prompt: str) -> str:
    return prompt

result = generate_text("Hello, world!")
print(result)
```

## From LangChain

### Basic LLM Migration

**Before (LangChain)**:

```python
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OpenAI(model_name="gpt-3.5-turbo")
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Write a story about {topic}"
)
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run(topic="robots")
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_story(topic: str) -> str:
    return f"Write a story about {topic}"

result = generate_story("robots")
```

### Chain Migration

**Before (LangChain chains)**:

```python
from langchain.chains import SimpleSequentialChain
from langchain.llms import OpenAI

llm = OpenAI(model_name="gpt-3.5-turbo")

# Create chains
chain1 = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["topic"],
    template="Summarize this topic: {topic}"
))
chain2 = LLMChain(llm=llm, prompt=PromptTemplate(
    input_variables=["summary"],
    template="Expand on this summary: {summary}"
))

# Combine chains
overall_chain = SimpleSequentialChain(chains=[chain1, chain2])
result = overall_chain.run("artificial intelligence")
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def summarize_topic(topic: str) -> str:
    return f"Summarize this topic: {topic}"

@llm_dispatcher
def expand_summary(summary: str) -> str:
    return f"Expand on this summary: {summary}"

def process_topic(topic: str) -> str:
    summary = summarize_topic(topic)
    expanded = expand_summary(summary)
    return expanded

result = process_topic("artificial intelligence")
```

## From Custom LLM Wrappers

### Custom Provider Migration

**Before (Custom wrapper)**:

```python
class CustomLLMWrapper:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_async(self, prompt: str) -> str:
        # Async implementation
        pass

# Usage
llm = CustomLLMWrapper(api_key="your-key")
result = llm.generate("Hello, world!")
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import LLMSwitch

# Create custom switch
switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "your-key",
            "models": ["gpt-4"]
        }
    }
)

@switch.route
def generate_text(prompt: str) -> str:
    return prompt

result = generate_text("Hello, world!")
```

## From Multiple Provider Libraries

### Multi-Provider Migration

**Before (Multiple libraries)**:

```python
import openai
import anthropic
import google.generativeai as genai

def generate_with_multiple_providers(prompt: str) -> str:
    # Try OpenAI first
    try:
        client = openai.OpenAI(api_key="openai-key")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI failed: {e}")

    # Try Anthropic
    try:
        client = anthropic.Anthropic(api_key="anthropic-key")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Anthropic failed: {e}")

    # Try Google
    try:
        genai.configure(api_key="google-key")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Google failed: {e}")

    raise Exception("All providers failed")

result = generate_with_multiple_providers("Hello, world!")
```

**After (LLM-Dispatcher)**:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher(
    providers=["openai", "anthropic", "google"],
    fallback_enabled=True,
    max_retries=3
)
def generate_with_multiple_providers(prompt: str) -> str:
    return prompt

result = generate_with_multiple_providers("Hello, world!")
```

## Configuration Migration

### Environment Variables

**Before (Manual configuration)**:

```python
import os
import openai

# Set API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic.api_key = os.getenv("ANTHROPIC_API_KEY")

# Configure models
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet")
```

**After (LLM-Dispatcher configuration)**:

```python
from llm_dispatcher import init

# Initialize with environment variables
switch = init(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Or use configuration file
switch = init("config.yaml")
```

### Configuration File Migration

**Before (Custom config)**:

```python
# config.py
OPENAI_CONFIG = {
    "api_key": "your-key",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 1000
}

ANTHROPIC_CONFIG = {
    "api_key": "your-key",
    "model": "claude-3-sonnet",
    "max_tokens": 1000
}
```

**After (LLM-Dispatcher config)**:

```yaml
# config.yaml
providers:
  openai:
    api_key: "your-key"
    models: ["gpt-4", "gpt-3.5-turbo"]
    temperature: 0.7
    max_tokens: 1000

  anthropic:
    api_key: "your-key"
    models: ["claude-3-sonnet", "claude-3-haiku"]
    max_tokens: 1000

switching_rules:
  optimization_strategy: "balanced"
  fallback_enabled: true
  max_retries: 3
```

## Error Handling Migration

### Custom Error Handling

**Before (Manual error handling)**:

```python
def generate_with_error_handling(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except openai.RateLimitError:
        print("Rate limit exceeded, waiting...")
        time.sleep(60)
        return generate_with_error_handling(prompt)
    except openai.APIError as e:
        print(f"API error: {e}")
        return "Error generating response"
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Error generating response"
```

**After (LLM-Dispatcher error handling)**:

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.exceptions import LLMDispatcherError

@llm_dispatcher(
    fallback_enabled=True,
    max_retries=3,
    retry_delay=60
)
def generate_with_error_handling(prompt: str) -> str:
    return prompt

try:
    result = generate_with_error_handling("Hello, world!")
except LLMDispatcherError as e:
    print(f"LLM-Dispatcher error: {e}")
    result = "Error generating response"
```

## Performance Optimization Migration

### Caching Migration

**Before (Manual caching)**:

```python
import functools
import hashlib

cache = {}

def cached_generate(prompt: str) -> str:
    # Create cache key
    cache_key = hashlib.md5(prompt.encode()).hexdigest()

    # Check cache
    if cache_key in cache:
        return cache[cache_key]

    # Generate response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    result = response.choices[0].message.content

    # Cache result
    cache[cache_key] = result
    return result
```

**After (LLM-Dispatcher caching)**:

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.cache import TTLCache

cache = TTLCache(ttl=3600)  # 1 hour cache

@llm_dispatcher(cache=cache)
def cached_generate(prompt: str) -> str:
    return prompt

result = cached_generate("Hello, world!")
```

### Batch Processing Migration

**Before (Manual batching)**:

```python
import asyncio

async def batch_generate(prompts: list) -> list:
    tasks = []
    for prompt in prompts:
        task = asyncio.create_task(
            openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
        )
        tasks.append(task)

    responses = await asyncio.gather(*tasks)
    return [response.choices[0].message.content for response in responses]
```

**After (LLM-Dispatcher batching)**:

```python
from llm_dispatcher import llm_dispatcher
import asyncio

@llm_dispatcher
def generate_text(prompt: str) -> str:
    return prompt

async def batch_generate(prompts: list) -> list:
    tasks = [generate_text(prompt) for prompt in prompts]
    return await asyncio.gather(*tasks)

results = await batch_generate(["Hello", "World", "AI"])
```

## Testing Migration

### Test Migration

**Before (Custom testing)**:

```python
import unittest
from unittest.mock import patch, MagicMock

class TestLLMGeneration(unittest.TestCase):
    def setUp(self):
        self.prompt = "Test prompt"

    @patch('openai.ChatCompletion.create')
    def test_generate_text(self, mock_create):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_create.return_value = mock_response

        result = generate_text(self.prompt)
        self.assertEqual(result, "Test response")
```

**After (LLM-Dispatcher testing)**:

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_switch():
    with patch('llm_dispatcher.LLMSwitch') as mock:
        yield mock

def test_generate_text(mock_switch):
    mock_switch.return_value.process_request.return_value = "Test response"

    result = generate_text("Test prompt")
    assert result == "Test response"
```

## Migration Checklist

### Pre-Migration

- [ ] **Audit current usage**: Document all current LLM calls and patterns
- [ ] **Identify providers**: List all providers currently used
- [ ] **Review error handling**: Document current error handling strategies
- [ ] **Check dependencies**: List all LLM-related dependencies
- [ ] **Test environment**: Set up test environment for migration

### During Migration

- [ ] **Install LLM-Dispatcher**: `pip install llm-dispatcher`
- [ ] **Migrate basic calls**: Start with simple text generation
- [ ] **Update configuration**: Move to LLM-Dispatcher configuration
- [ ] **Migrate error handling**: Update to use LLM-Dispatcher exceptions
- [ ] **Test functionality**: Ensure all features work as expected
- [ ] **Update tests**: Migrate test cases to use LLM-Dispatcher

### Post-Migration

- [ ] **Remove old dependencies**: Uninstall unused LLM libraries
- [ ] **Update documentation**: Update any internal documentation
- [ ] **Monitor performance**: Check that performance is maintained or improved
- [ ] **Train team**: Ensure team understands new patterns
- [ ] **Deploy gradually**: Use feature flags or gradual rollout

## Common Migration Issues

### Issue 1: Different Response Formats

**Problem**: Different libraries return responses in different formats

**Solution**:

```python
# LLM-Dispatcher normalizes response formats
@llm_dispatcher
def generate_text(prompt: str) -> str:
    return prompt  # Always returns string

# If you need more details
@llm_dispatcher
def generate_with_metadata(prompt: str) -> dict:
    # Access metadata through switch
    return {"content": prompt, "metadata": "available"}
```

### Issue 2: Different Parameter Names

**Problem**: Different libraries use different parameter names

**Solution**:

```python
# LLM-Dispatcher standardizes parameter names
@llm_dispatcher(
    max_tokens=1000,  # Standardized name
    temperature=0.7,  # Standardized name
    top_p=0.9        # Standardized name
)
def generate_text(prompt: str) -> str:
    return prompt
```

### Issue 3: Different Streaming Formats

**Problem**: Different libraries stream data differently

**Solution**:

```python
# LLM-Dispatcher standardizes streaming
@llm_stream
async def stream_text(prompt: str):
    yield prompt  # Standardized streaming format

# Access streaming metadata
@llm_stream_with_metadata
async def stream_with_metadata(prompt: str):
    yield {"chunk": prompt, "metadata": "available"}
```

## Getting Help

### Migration Support

- **Documentation**: Check the [API Reference](../api/core.md) for detailed information
- **Examples**: Look at [Examples](../getting-started/examples.md) for migration patterns
- **Community**: Ask questions in [GitHub Discussions](https://github.com/ashhadahsan/llm-dispatcher/discussions)
- **Professional**: Contact ashhadahsan@mail.com for migration consulting

### Migration Tools

```python
# Migration helper tool
from llm_dispatcher.migration import MigrationHelper

helper = MigrationHelper()

# Analyze current code
analysis = helper.analyze_code("path/to/your/code.py")
print(f"Found {len(analysis.llm_calls)} LLM calls")
print(f"Providers used: {analysis.providers}")

# Generate migration suggestions
suggestions = helper.generate_suggestions(analysis)
for suggestion in suggestions:
    print(f"Migrate: {suggestion.old_code}")
    print(f"To: {suggestion.new_code}")
```

## Next Steps

- [:octicons-rocket-24: Quick Start](../getting-started/quickstart.md) - Get started with LLM-Dispatcher
- [:octicons-gear-24: Configuration](../getting-started/configuration.md) - Learn about configuration options
- [:octicons-book-24: API Reference](../api/core.md) - Complete API documentation
- [:octicons-shield-check-24: Troubleshooting](troubleshooting.md) - Common issues and solutions
