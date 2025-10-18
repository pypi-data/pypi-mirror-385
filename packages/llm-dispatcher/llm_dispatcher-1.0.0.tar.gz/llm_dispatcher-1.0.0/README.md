# 🏆 LLM-Dispatcher: Intelligent LLM Routing

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://pytest.org/)
[![Coverage](https://codecov.io/gh/ashhadahsan/llm-dispatcher/branch/main/graph/badge.svg)](https://codecov.io/gh/ashhadahsan/llm-dispatcher)
[![Coverage](https://img.shields.io/badge/coverage-22%25-red.svg)](https://github.com/ashhadahsan/llm-dispatcher)

**LLM-Dispatcher** is an intelligent Python package that automatically selects the best Large Language Model (LLM) for your specific task based on performance metrics, cost optimization, and real-time availability.

## 🚀 Features

- **🧠 Intelligent Switching**: Performance-based LLM selection using credible benchmarks
- **📊 Real Metrics**: Based on 2024-2025 benchmark data (MMLU, HumanEval, GPQA, AIME, etc.)
- **💰 Cost Optimization**: Dynamic cost-quality balancing
- **🔄 Smart Fallbacks**: Automatic failover with intelligent routing
- **🎯 Multi-Modal**: Support for text, vision, audio, and structured output
- **⚡ Real-time**: Live performance monitoring and optimization
- **🔧 Simple API**: Decorator-based usage with minimal configuration

## 📈 Supported Providers

| Provider      | Models                            | Capabilities                                      |
| ------------- | --------------------------------- | ------------------------------------------------- |
| **OpenAI**    | GPT-4, GPT-4 Turbo, GPT-3.5 Turbo | Text, Vision, Function Calling, Structured Output |
| **Anthropic** | Claude-3 Opus, Sonnet, Haiku      | Text, Vision, Reasoning, Code                     |
| **Google**    | Gemini 2.5 Pro, Flash, Ultra      | Text, Vision, Multimodal, Fast                    |
| **xAI**       | Grok 3 Beta                       | Text, Reasoning, Math                             |

## 🎯 Performance Benchmarks

Based on latest 2024-2025 data:

| Model          | MMLU  | HumanEval | GPQA  | AIME  | HellaSwag | ARC   | VQA   |
| -------------- | ----- | --------- | ----- | ----- | --------- | ----- | ----- |
| GPT-4          | 86.3% | 67.4%     | 82.1% | 91.2% | 95.1%     | 96.4% | 78.2% |
| Claude-3 Opus  | 84.6% | 67.4%     | 84.6% | 89.8% | 94.2%     | 95.8% | 76.8% |
| Gemini 2.5 Pro | 84.0% | 65.2%     | 84.0% | 87.3% | 93.8%     | 94.2% | 74.5% |
| Grok 3 Beta    | 82.1% | 63.8%     | 84.6% | 93.3% | 92.1%     | 93.8% | 71.2% |

## 🚀 Quick Start

### Installation

```bash
pip install llm-dispatcher
```

### Basic Usage

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    """Automatically routed to the best LLM for text generation."""
    return prompt

# Usage
result = generate_text("Write a story about a robot")
print(result)
```

### Advanced Configuration

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
    """Automatically uses the best model for code generation."""
    return description

@switch.route(task_type=TaskType.VISION_ANALYSIS)
def analyze_image(image_path: str) -> dict:
    """Automatically uses vision-capable models."""
    return {"analysis": "Image processed"}
```

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Quick Start Tutorial](docs/quickstart.md)
- [Advanced Configuration](docs/configuration.md)
- [API Reference](docs/api.md)
- [Benchmark Data](docs/benchmarks.md)
- [Contributing](CONTRIBUTING.md)

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/ashhadahsan/llm-dispatcher.git
cd llm-dispatcher
pip install -e ".[dev]"
pre-commit install
```

### Testing & Coverage

#### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/llm_dispatcher --cov-report=term-missing --cov-report=html

# Run specific test categories
pytest tests/test_core_switching.py -v
pytest tests/test_providers/ -v
pytest tests/test_multimodal.py -v
```

#### Current Test Coverage

- **Overall Coverage**: 47% (7,344 statements, 3,886 missed)
- **Core Components**: 98% coverage on base classes
- **Provider Integration**: 48-91% coverage across providers
- **Multimodal Support**: 47-86% coverage
- **Monitoring & Analytics**: 0% coverage (new features)

#### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src/llm_dispatcher --cov-report=html
open htmlcov/index.html

# Generate XML report for CI/CD
pytest --cov=src/llm_dispatcher --cov-report=xml

# Update coverage badge in README
python scripts/update_coverage_badge.py
```

#### Automated Coverage

- **GitHub Actions**: Automated coverage reporting on every PR
- **Codecov Integration**: Real-time coverage tracking
- **Coverage Badge**: Automatically updated in README
- **Coverage Reports**: Available as GitHub Actions artifacts

### Run Benchmarks

```bash
pytest tests/benchmarks/ -v
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🧪 Testing

LLM-Dispatcher includes comprehensive tests to ensure reliability and performance.

### Test Coverage

Current test coverage: **22%** (29/29 core tests passing)

- ✅ **Core Functionality**: All basic tests passing
- ✅ **Performance Tests**: Latency and throughput tests working
- ✅ **Benchmark Utils**: Metric calculation and validation tests
- ✅ **Provider Integration**: OpenAI provider tests
- ✅ **Configuration**: Switch configuration and validation tests

### Running Tests

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src/llm_dispatcher --cov-report=html

# Run specific test categories
pytest tests/test_basic.py                    # Core functionality
pytest tests/test_performance.py              # Performance tests
pytest tests/test_benchmark_utils.py          # Benchmark utilities
```

### Test Categories

| Category        | Tests | Status     | Description                                    |
| --------------- | ----- | ---------- | ---------------------------------------------- |
| **Core**        | 27    | ✅ Passing | Basic functionality, configurations, providers |
| **Performance** | 1     | ✅ Passing | Latency and throughput testing                 |
| **Benchmarks**  | 1     | ✅ Passing | Metric calculations and validation             |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Benchmark data from [Musaix](https://musaix.com/benchmarks-2025/), [51D.co](https://www.51d.co/llm-performance-benchmarking/), and [Learnopoly](https://learnopoly.com/the-ultimate-2025-guide-to-code-llm-benchmarks-and-performance-measures/)
- LLM providers: OpenAI, Anthropic, Google, xAI
- Open source community

## 📞 Support

- 📧 Email: ashhadahsan@mail.com
- 🐛 Issues: [GitHub Issues](https://github.com/ashhadahsan/llm-dispatcher/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ashhadahsan/llm-dispatcher/discussions)

---

**Built with ❤️ for the AI community**
