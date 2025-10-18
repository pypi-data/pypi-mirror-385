# LLM-Dispatcher Documentation

This directory contains the documentation for LLM-Dispatcher, built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

2. Build the documentation:

```bash
./build.sh
```

3. Serve locally:

```bash
mkdocs serve
```

The documentation will be available at `http://localhost:8000`.

## 📁 Structure

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Getting started guides
│   ├── installation.md
│   ├── quickstart.md
│   ├── configuration.md
│   └── examples.md
├── user-guide/                 # User documentation
│   ├── basic-usage.md
│   ├── advanced-features.md
│   ├── multimodal.md
│   ├── streaming.md
│   ├── error-handling.md
│   └── performance.md
├── api/                        # API reference
│   ├── core.md
│   ├── decorators.md
│   ├── providers.md
│   ├── exceptions.md
│   └── configuration.md
├── providers/                  # Provider documentation
│   ├── overview.md
│   ├── openai.md
│   ├── anthropic.md
│   ├── google.md
│   └── grok.md
├── benchmarks/                 # Benchmark data
│   ├── performance.md
│   ├── cost.md
│   └── comparison.md
│   ├── security.md
│   ├── compliance.md
│   ├── monitoring.md
│   └── analytics.md
├── integrations/               # Integration guides
│   ├── langchain.md
│   ├── langgraph.md
│   └── coming-soon.md
├── development/                # Development docs
│   ├── contributing.md
│   ├── testing.md
│   ├── building.md
│   └── changelog.md
├── about/                      # About and support
│   ├── license.md
│   └── support.md
├── assets/                     # Static assets
├── mkdocs.yml                  # MkDocs configuration
├── requirements.txt            # Python dependencies
└── build.sh                   # Build script
```

## 🛠️ Development

### Adding New Pages

1. Create a new Markdown file in the appropriate directory
2. Add the page to the navigation in `mkdocs.yml`
3. Follow the existing documentation style and format

### Styling Guidelines

- Use Material for MkDocs features like admonitions, code blocks, and tabs
- Include code examples with syntax highlighting
- Use consistent formatting and structure
- Add cross-references between related pages

### Building and Testing

```bash
# Build the documentation
mkdocs build

# Serve locally for testing
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## 🎨 Features

The documentation uses Material for MkDocs with the following features:

- **Responsive Design** - Works on all devices
- **Dark/Light Mode** - Automatic theme switching
- **Search** - Built-in search functionality
- **Navigation** - Hierarchical navigation with sections
- **Code Highlighting** - Syntax highlighting for code blocks
- **Admonitions** - Callouts, warnings, and tips
- **Tabs** - Tabbed content for better organization
- **Icons** - Material Design icons throughout
- **Social Links** - Links to GitHub, Twitter, etc.

## 📝 Writing Guidelines

### Markdown Extensions

The documentation uses several Markdown extensions:

- **Admonitions** - For callouts and warnings
- **Code Blocks** - With syntax highlighting
- **Tables** - For structured data
- **Links** - Internal and external links
- **Images** - With proper alt text
- **Lists** - Ordered and unordered lists

### Code Examples

Always include working code examples:

```python
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
def generate_text(prompt: str) -> str:
    """Generate text using the best available LLM."""
    return prompt

# Usage
result = generate_text("Hello, world!")
print(result)
```

### Admonitions

Use admonitions for important information:

!!! note "Note"
This is a note with important information.

!!! warning "Warning"
This is a warning about potential issues.

!!! tip "Tip"
This is a helpful tip for users.

## 🚀 Deployment

### GitHub Pages

The documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch.

### Manual Deployment

```bash
# Deploy to GitHub Pages
mkdocs gh-deploy

# Deploy to a custom domain
mkdocs build
# Upload the 'site' directory to your web server
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the documentation locally
5. Submit a pull request

## 📞 Support

For questions about the documentation:

- 📧 Email: ashhadahsan@mail.com
- 🐛 Issues: [GitHub Issues](https://github.com/ashhadahsan/llm-dispatcher/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/ashhadahsan/llm-dispatcher/discussions)

## 📄 License

The documentation is licensed under the same MIT License as the main project.
