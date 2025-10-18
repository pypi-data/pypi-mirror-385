# 🏆 LLM-Dispatcher: Intelligent LLM Routing

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-blue.svg)](https://pytest.org/)

**LLM-Dispatcher** is an intelligent Python package that automatically selects the best Large Language Model (LLM) for your specific task based on performance metrics, cost optimization, and real-time availability.

## 🚀 Key Features

<div class="grid cards" markdown>

- :material-brain:{ .lg .middle } **Intelligent Switching**

  ***

  Performance-based LLM selection using credible benchmarks from 2024-2025

  [:octicons-arrow-right-24: Learn more](user-guide/basic-usage.md)

- :material-chart-line:{ .lg .middle } **Real Metrics**

  ***

  Based on MMLU, HumanEval, GPQA, AIME, and other authoritative benchmarks

  [:octicons-arrow-right-24: View benchmarks](benchmarks/performance.md)

- :material-currency-usd:{ .lg .middle } **Cost Optimization**

  ***

  Dynamic cost-quality balancing with intelligent routing decisions

  [:octicons-arrow-right-24: Cost analysis](benchmarks/cost.md)

- :material-refresh:{ .lg .middle } **Smart Fallbacks**

  ***

  Automatic failover with intelligent routing and error recovery

  [:octicons-arrow-right-24: Error handling](user-guide/error-handling.md)

- :material-eye:{ .lg .middle } **Multi-Modal**

  ***

  Support for text, vision, audio, and structured output across providers

  [:octicons-arrow-right-24: Multimodal guide](user-guide/multimodal.md)

- :material-lightning-bolt:{ .lg .middle } **Real-time**

  ***

  Live performance monitoring and optimization with streaming support

  [:octicons-arrow-right-24: Streaming guide](user-guide/streaming.md)

</div>

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
```

## 🔗 Integrations

<div class="grid cards" markdown>

- :material-link:{ .lg .middle } **LangChain**

  ***

  Seamless integration with LangChain for complex workflows

  [:octicons-arrow-right-24: LangChain integration](integrations/coming-soon.md)

- :material-graph:{ .lg .middle } **LangGraph**

  ***

  Advanced graph-based workflows with intelligent routing

  [:octicons-arrow-right-24: LangGraph integration](integrations/coming-soon.md)

- :material-rocket-launch:{ .lg .middle } **Coming Soon**

  ***

  More integrations and providers on the roadmap

  [:octicons-arrow-right-24: Roadmap](integrations/coming-soon.md)

</div>

## 📚 Documentation

- [:octicons-book-24: Getting Started](getting-started/installation.md) - Installation and setup
- [:octicons-rocket-24: Quick Start](getting-started/quickstart.md) - Your first steps
- [:octicons-gear-24: Configuration](getting-started/configuration.md) - Advanced configuration
- [:octicons-code-24: API Reference](api/core.md) - Complete API documentation
- [:octicons-graph-24: Benchmarks](benchmarks/performance.md) - Performance data
- [:octicons-heart-24: Contributing](development/contributing.md) - How to contribute

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](about/license.md) file for details.

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
