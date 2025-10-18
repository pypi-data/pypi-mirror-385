# Installation

## System Requirements

LLM-Dispatcher requires Python 3.8 or higher and supports all major operating systems.

### Python Version Support

| Python Version | Support Status |
| -------------- | -------------- |
| 3.8            | ✅ Supported   |
| 3.9            | ✅ Supported   |
| 3.10           | ✅ Supported   |
| 3.11           | ✅ Supported   |
| 3.12           | ✅ Supported   |

## Installation Methods

### PyPI Installation (Recommended)

The easiest way to install LLM-Dispatcher is using pip:

```bash
pip install llm-dispatcher
```

### Development Installation

For development or to get the latest features:

```bash
git clone https://github.com/ashhadahsan/llm-dispatcher.git
cd llm-dispatcher
pip install -e ".[dev]"
```

### Install with Optional Dependencies

#### For Documentation Development

```bash
pip install llm-dispatcher[docs]
```

#### For Benchmarking

```bash
pip install llm-dispatcher[benchmark]
```

#### For All Optional Dependencies

```bash
pip install llm-dispatcher[dev,docs,benchmark]
```

## Provider Setup

### OpenAI

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

### Anthropic

1. Get your API key from [Anthropic Console](https://console.anthropic.com/)
2. Set the environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

### Google

1. Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set the environment variable:

```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### xAI (Grok)

1. Get your API key from [xAI Console](https://console.x.ai/)
2. Set the environment variable:

```bash
export XAI_API_KEY="xai-your-api-key-here"
```

## Environment Configuration

### Using .env File

Create a `.env` file in your project root:

```bash
# .env
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
XAI_API_KEY=xai-your-xai-key
```

### Using Environment Variables

```bash
# Set all at once
export OPENAI_API_KEY="sk-your-key"
export ANTHROPIC_API_KEY="sk-ant-your-key"
export GOOGLE_API_KEY="your-key"
export XAI_API_KEY="xai-your-key"
```

## Verification

Test your installation:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def test_installation(prompt: str) -> str:
    return prompt

# This should work without errors
result = test_installation("Hello, LLM-Dispatcher!")
print(result)
```

## Troubleshooting

### Common Issues

#### Import Errors

If you encounter import errors, ensure you're using Python 3.8+:

```bash
python --version
```

#### API Key Issues

Verify your API keys are correctly set:

```python
import os
print("OpenAI:", "OPENAI_API_KEY" in os.environ)
print("Anthropic:", "ANTHROPIC_API_KEY" in os.environ)
print("Google:", "GOOGLE_API_KEY" in os.environ)
print("xAI:", "XAI_API_KEY" in os.environ)
```

#### Network Issues

If you're behind a corporate firewall, you may need to configure proxy settings:

```python
import os
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'https://your-proxy:port'
```

### Getting Help

If you encounter issues:

1. Check the [FAQ](../about/support.md#faq)
2. Search [GitHub Issues](https://github.com/ashhadahsan/llm-dispatcher/issues)
3. Create a new issue with:
   - Python version
   - Operating system
   - Error message
   - Steps to reproduce

## Next Steps

Once installed, proceed to the [Quick Start Guide](quickstart.md) to begin using LLM-Dispatcher.
