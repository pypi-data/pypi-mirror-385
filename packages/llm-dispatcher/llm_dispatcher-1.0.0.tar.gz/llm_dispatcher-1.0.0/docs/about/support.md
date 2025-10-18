# Support

Get help with LLM-Dispatcher through various channels and resources.

## 📞 Contact Information

### Primary Support

- **Email**: ashhadahsan@mail.com
- **GitHub Issues**: [Report bugs and request features](https://github.com/ashhadahsan/llm-dispatcher/issues)
- **GitHub Discussions**: [Community discussions and Q&A](https://github.com/ashhadahsan/llm-dispatcher/discussions)

### Social Media

- **Twitter**: [@ashhadahsan](https://twitter.com/ashhadahsan)
- **LinkedIn**: [ashhadahsan](https://linkedin.com/in/ashhadahsan)

## 🐛 Reporting Issues

### Before Reporting

1. **Check existing issues** - Search [GitHub Issues](https://github.com/ashhadahsan/llm-dispatcher/issues) to see if your issue has already been reported
2. **Update to latest version** - Make sure you're using the latest version of LLM-Dispatcher
3. **Check documentation** - Review the relevant documentation pages
4. **Try minimal example** - Create a minimal example that reproduces the issue

### Issue Template

When reporting an issue, please include:

````markdown
## Bug Report

### Description

Brief description of the issue.

### Environment

- Python version: 3.x.x
- LLM-Dispatcher version: x.x.x
- Operating system: macOS/Windows/Linux
- Provider(s) used: OpenAI/Anthropic/Google/xAI

### Steps to Reproduce

1. Step one
2. Step two
3. Step three

### Expected Behavior

What you expected to happen.

### Actual Behavior

What actually happened.

### Code Example

```python
# Minimal code that reproduces the issue
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def test_function(prompt: str) -> str:
    return prompt

result = test_function("test")
```
````

### Error Message

```
Full error message and stack trace
```

### Additional Context

Any other relevant information.

````

## 💡 Feature Requests

### Before Requesting

1. **Check roadmap** - Review the [Coming Soon](integrations/coming-soon.md) page
2. **Search existing requests** - Look for similar feature requests
3. **Consider alternatives** - Check if there's already a way to achieve what you need

### Feature Request Template

```markdown
## Feature Request

### Description
Brief description of the feature you'd like to see.

### Use Case
Describe the specific use case or problem this feature would solve.

### Proposed Solution
Describe your proposed solution or implementation.

### Alternatives Considered
Describe any alternative solutions you've considered.

### Additional Context
Any other relevant information, mockups, or examples.
````

## ❓ Frequently Asked Questions {#faq}

### Installation Issues

**Q: I'm getting import errors after installation.**
A: Make sure you're using Python 3.8 or higher and that all dependencies are installed correctly. Try:

```bash
pip install --upgrade llm-dispatcher
pip install --upgrade pip
```

**Q: How do I install with specific providers?**
A: LLM-Dispatcher includes all providers by default. If you want to install only specific dependencies:

```bash
pip install llm-dispatcher[openai]  # Only OpenAI
pip install llm-dispatcher[anthropic]  # Only Anthropic
```

### Configuration Issues

**Q: My API keys aren't being recognized.**
A: Make sure your API keys are set correctly:

```bash
# Check if environment variables are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
echo $GOOGLE_API_KEY
echo $XAI_API_KEY
```

**Q: How do I configure multiple providers?**
A: You can configure multiple providers in several ways:

```python
# Method 1: Environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Method 2: Configuration file
# config.yaml
providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"

# Method 3: Programmatic
from llm_dispatcher import LLMSwitch
switch = LLMSwitch(providers={
    "openai": {"api_key": "sk-..."},
    "anthropic": {"api_key": "sk-ant-..."}
})
```

### Performance Issues

**Q: My requests are taking too long.**
A: Try these optimizations:

```python
# Use speed optimization
@llm_dispatcher(optimization_strategy=OptimizationStrategy.SPEED)
def fast_generation(prompt: str) -> str:
    return prompt

# Set latency limits
@llm_dispatcher(max_latency=2000)
def limited_latency_generation(prompt: str) -> str:
    return prompt
```

**Q: My costs are too high.**
A: Use cost optimization:

```python
# Use cost optimization
@llm_dispatcher(optimization_strategy=OptimizationStrategy.COST)
def cost_optimized_generation(prompt: str) -> str:
    return prompt

# Set cost limits
@llm_dispatcher(max_cost=0.01)
def limited_cost_generation(prompt: str) -> str:
    return prompt
```

### Error Handling

**Q: I'm getting provider errors.**
A: Enable fallbacks and proper error handling:

```python
from llm_dispatcher.exceptions import LLMDispatcherError

@llm_dispatcher(fallback_enabled=True)
def reliable_generation(prompt: str) -> str:
    return prompt

try:
    result = reliable_generation("Your prompt")
except LLMDispatcherError as e:
    print(f"Error: {e}")
    # Handle error appropriately
```

**Q: How do I handle rate limits?**
A: LLM-Dispatcher handles rate limits automatically, but you can also:

```python
@llm_dispatcher(
    max_retries=3,
    retry_delay=1000,
    fallback_enabled=True
)
def rate_limit_handling(prompt: str) -> str:
    return prompt
```

## 📚 Documentation

### Getting Started

- [Installation](../getting-started/installation.md)
- [Quick Start](../getting-started/quickstart.md)
- [Configuration](../getting-started/configuration.md)
- [Examples](../getting-started/examples.md)

### User Guide

- [Basic Usage](../user-guide/basic-usage.md)
- [Advanced Features](../user-guide/advanced-features.md)
- [Multimodal Support](../user-guide/multimodal.md)
- [Streaming](../user-guide/streaming.md)
- [Error Handling](../user-guide/error-handling.md)
- [Performance Tips](../user-guide/performance.md)

### API Reference

- [Core Classes](../api/core.md)
- [Decorators](../api/decorators.md)
- [Providers](../api/providers.md)
- [Exceptions](../api/exceptions.md)
- [Configuration](../api/configuration.md)

## 🏢 Enterprise Support

For enterprise customers, we offer:

### Premium Support

- **Priority support** - Faster response times
- **Direct email support** - Dedicated support channel
- **Phone support** - For critical issues
- **Custom integrations** - Help with specific use cases

### Professional Services

- **Implementation consulting** - Help with deployment
- **Custom development** - Tailored solutions
- **Training and workshops** - Team training sessions
- **Architecture review** - Best practices guidance

### Contact Enterprise Support

- **Email**: enterprise@llm-dispatcher.com
- **Phone**: +1 (555) 123-4567
- **Sales**: sales@llm-dispatcher.com

## 🤝 Community

### Contributing

- [Contributing Guide](../development/contributing.md)
- [Code of Conduct](../development/code-of-conduct.md)
- [Development Setup](../development/testing.md)

### Community Resources

- **Discord**: [Join our Discord server](https://discord.gg/llm-dispatcher)
- **Reddit**: [r/llmdispatcher](https://reddit.com/r/llmdispatcher)
- **Stack Overflow**: Tag questions with `llm-dispatcher`
- **Twitter**: Follow [@llmdispatcher](https://twitter.com/llmdispatcher) for updates

### Events and Meetups

- **Monthly Office Hours** - First Tuesday of each month
- **Community Calls** - Quarterly community discussions
- **Conference Talks** - Regular presentations at AI conferences
- **Workshops** - Hands-on training sessions

## 📊 Status and Updates

### Service Status

- **Status Page**: [status.llm-dispatcher.com](https://status.llm-dispatcher.com)
- **Uptime**: 99.9% availability target
- **Incident Updates**: Real-time status updates

### Release Information

- **Release Notes**: [GitHub Releases](https://github.com/ashhadahsan/llm-dispatcher/releases)
- **Changelog**: [Development Changelog](../development/changelog.md)
- **Roadmap**: [Coming Soon](../integrations/coming-soon.md)

### Security

- **Security Policy**: [SECURITY.md](https://github.com/ashhadahsan/llm-dispatcher/security/policy)
- **Vulnerability Reporting**: security@llm-dispatcher.com
- **Security Updates**: Immediate notification for security issues

## 🎯 Getting Help

### Quick Help

1. **Check FAQ** - Review the frequently asked questions above
2. **Search Issues** - Look through existing GitHub issues
3. **Read Documentation** - Check the relevant documentation pages
4. **Ask Community** - Post in GitHub Discussions or Discord

### Escalation Path

1. **GitHub Discussions** - For general questions and community help
2. **GitHub Issues** - For bugs and feature requests
3. **Email Support** - For direct assistance
4. **Enterprise Support** - For premium customers

### Response Times

- **GitHub Issues**: 2-3 business days
- **GitHub Discussions**: 1-2 business days
- **Email Support**: 1 business day
- **Enterprise Support**: 4-8 hours

## 📝 Feedback

We value your feedback! Please help us improve by:

- **Rating the project** - Star us on GitHub
- **Sharing your experience** - Tell us how you're using LLM-Dispatcher
- **Suggesting improvements** - Help us make it better
- **Reporting issues** - Help us fix bugs and improve reliability

Thank you for using LLM-Dispatcher! 🚀
