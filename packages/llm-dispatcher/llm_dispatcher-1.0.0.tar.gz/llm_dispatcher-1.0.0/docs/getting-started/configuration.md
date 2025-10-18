# Configuration

LLM-Dispatcher offers extensive configuration options to customize behavior for your specific use case.

## Configuration Methods

### 1. Environment Variables

Set API keys and basic configuration via environment variables:

```bash
# API Keys
export OPENAI_API_KEY="sk-your-openai-key"
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export XAI_API_KEY="xai-your-xai-key"

# Configuration
export LLM_DISPATCHER_OPTIMIZATION_STRATEGY="balanced"
export LLM_DISPATCHER_MAX_LATENCY_MS="5000"
export LLM_DISPATCHER_MAX_COST_PER_REQUEST="0.10"
export LLM_DISPATCHER_FALLBACK_ENABLED="true"
```

### 2. Configuration File

Create a `config.yaml` file for persistent configuration:

```yaml
# config.yaml
switching_rules:
  optimization_strategy: "balanced"  # balanced, cost, speed, performance
  max_latency_ms: 5000
  max_cost_per_request: 0.10
  fallback_enabled: true
  max_retries: 3
  retry_delay_ms: 1000

monitoring:
  enable_monitoring: true
  performance_window_hours: 24
  log_level: "INFO"
  metrics_retention_days: 30

providers:
  openai:
    api_key: "${OPENAI_API_KEY}"
    models: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
    default_model: "gpt-4"
    max_tokens: 4096
    temperature: 0.7
    
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    default_model: "claude-3-sonnet"
    max_tokens: 4096
    temperature: 0.7
    
  google:
    api_key: "${GOOGLE_API_KEY}"
    models: ["gemini-2.5-pro", "gemini-2.5-flash"]
    default_model: "gemini-2.5-pro"
    max_tokens: 4096
    temperature: 0.7
    
  xai:
    api_key: "${XAI_API_KEY}"
    models: ["grok-3-beta"]
    default_model: "grok-3-beta"
    max_tokens: 4096
    temperature: 0.7

task_routing:
  text_generation:
    preferred_providers: ["openai", "anthropic"]
    optimization_strategy: "balanced"
    
  code_generation:
    preferred_providers: ["openai", "anthropic"]
    optimization_strategy: "performance"
    
  vision_analysis:
    preferred_providers: ["openai", "google", "anthropic"]
    optimization_strategy: "performance"
    
  reasoning:
    preferred_providers: ["anthropic", "openai"]
    optimization_strategy: "performance"
    
  math:
    preferred_providers: ["xai", "openai"]
    optimization_strategy: "performance"

cost_limits:
  daily_budget: 10.0
  monthly_budget: 100.0
  per_request_limit: 0.50
  alert_threshold: 0.8  # Alert when 80% of budget is used

performance_targets:
  max_latency_ms: 5000
  min_confidence_score: 0.8
  target_success_rate: 0.95
```

### 3. Programmatic Configuration

Configure LLM-Dispatcher programmatically:

```python
from llm_dispatcher import LLMSwitch, SwitchConfig
from llm_dispatcher.config.settings import OptimizationStrategy

# Create configuration
config = SwitchConfig(
    optimization_strategy=OptimizationStrategy.BALANCED,
    max_latency_ms=5000,
    max_cost_per_request=0.10,
    fallback_enabled=True,
    max_retries=3
)

# Initialize switch with configuration
switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."},
        "google": {"api_key": "..."}
    },
    config=config
)
```

## Configuration Options

### Optimization Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| `balanced` | Balances cost, speed, and quality | General purpose |
| `cost` | Prioritizes cost efficiency | Budget-conscious applications |
| `speed` | Prioritizes response time | Real-time applications |
| `performance` | Prioritizes quality and accuracy | High-quality output required |

### Provider Configuration

#### OpenAI
```yaml
openai:
  api_key: "${OPENAI_API_KEY}"
  models: ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
  default_model: "gpt-4"
  max_tokens: 4096
  temperature: 0.7
  timeout: 30
  max_retries: 3
```

#### Anthropic
```yaml
anthropic:
  api_key: "${ANTHROPIC_API_KEY}"
  models: ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
  default_model: "claude-3-sonnet"
  max_tokens: 4096
  temperature: 0.7
  timeout: 30
  max_retries: 3
```

#### Google
```yaml
google:
  api_key: "${GOOGLE_API_KEY}"
  models: ["gemini-2.5-pro", "gemini-2.5-flash"]
  default_model: "gemini-2.5-pro"
  max_tokens: 4096
  temperature: 0.7
  timeout: 30
  max_retries: 3
```

#### xAI (Grok)
```yaml
xai:
  api_key: "${XAI_API_KEY}"
  models: ["grok-3-beta"]
  default_model: "grok-3-beta"
  max_tokens: 4096
  temperature: 0.7
  timeout: 30
  max_retries: 3
```

### Task Routing Configuration

Configure how different task types are routed:

```yaml
task_routing:
  text_generation:
    preferred_providers: ["openai", "anthropic"]
    optimization_strategy: "balanced"
    max_cost: 0.05
    max_latency: 3000
    
  code_generation:
    preferred_providers: ["openai", "anthropic"]
    optimization_strategy: "performance"
    max_cost: 0.10
    max_latency: 5000
    
  vision_analysis:
    preferred_providers: ["openai", "google", "anthropic"]
    optimization_strategy: "performance"
    max_cost: 0.15
    max_latency: 8000
    
  reasoning:
    preferred_providers: ["anthropic", "openai"]
    optimization_strategy: "performance"
    max_cost: 0.20
    max_latency: 10000
    
  math:
    preferred_providers: ["xai", "openai"]
    optimization_strategy: "performance"
    max_cost: 0.10
    max_latency: 5000
```

### Cost Management

Configure cost limits and budgets:

```yaml
cost_limits:
  daily_budget: 10.0
  monthly_budget: 100.0
  per_request_limit: 0.50
  alert_threshold: 0.8
  currency: "USD"
  
cost_optimization:
  enable_cost_tracking: true
  cost_alert_email: "admin@example.com"
  cost_report_frequency: "daily"
  cost_breakdown_by_provider: true
```

### Performance Targets

Set performance targets and monitoring:

```yaml
performance_targets:
  max_latency_ms: 5000
  min_confidence_score: 0.8
  target_success_rate: 0.95
  target_cost_efficiency: 0.9
  
performance_monitoring:
  enable_monitoring: true
  metrics_retention_days: 30
  performance_window_hours: 24
  alert_on_performance_degradation: true
```

### Monitoring Configuration

Configure monitoring and logging:

```yaml
monitoring:
  enable_monitoring: true
  log_level: "INFO"
  metrics_retention_days: 30
  performance_window_hours: 24
  
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "llm_dispatcher.log"
  max_file_size: "10MB"
  backup_count: 5
```

## Advanced Configuration

### Custom Routing Logic

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

def custom_routing_logic(request: TaskRequest) -> str:
    """Custom logic to determine optimal provider."""
    if request.task_type == TaskType.CODE_GENERATION:
        return "openai"  # Prefer OpenAI for code
    elif request.task_type == TaskType.REASONING:
        return "anthropic"  # Prefer Anthropic for reasoning
    elif "creative" in request.prompt.lower():
        return "anthropic"  # Prefer Anthropic for creative tasks
    else:
        return "auto"  # Let LLM-Dispatcher decide

switch = LLMSwitch(
    providers={...},
    config={
        "custom_routing_logic": custom_routing_logic
    }
)
```

### Provider-Specific Configuration

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={
        "openai": {
            "api_key": "sk-...",
            "models": ["gpt-4", "gpt-4-turbo"],
            "default_model": "gpt-4",
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3,
            "rate_limit": {
                "requests_per_minute": 60,
                "tokens_per_minute": 150000
            }
        },
        "anthropic": {
            "api_key": "sk-ant-...",
            "models": ["claude-3-opus", "claude-3-sonnet"],
            "default_model": "claude-3-sonnet",
            "max_tokens": 4096,
            "temperature": 0.7,
            "timeout": 30,
            "max_retries": 3
        }
    }
)
```

### Environment-Specific Configuration

```python
import os
from llm_dispatcher import LLMSwitch

# Development configuration
if os.getenv("ENVIRONMENT") == "development":
    config = {
        "optimization_strategy": "cost",
        "max_cost_per_request": 0.01,
        "fallback_enabled": True,
        "log_level": "DEBUG"
    }
# Production configuration
elif os.getenv("ENVIRONMENT") == "production":
    config = {
        "optimization_strategy": "balanced",
        "max_cost_per_request": 0.50,
        "fallback_enabled": True,
        "log_level": "INFO",
        "monitoring": {
            "enable_monitoring": True,
            "metrics_retention_days": 90
        }
    }

switch = LLMSwitch(providers={...}, config=config)
```

## Configuration Validation

LLM-Dispatcher validates configuration on startup:

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.exceptions import ConfigurationError

try:
    switch = LLMSwitch(providers={...}, config={...})
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    # Handle configuration error
```

## Configuration Best Practices

### 1. Use Environment Variables for Secrets
```bash
# Good: Use environment variables
export OPENAI_API_KEY="sk-..."

# Bad: Hardcode in configuration
api_key: "sk-your-actual-key"
```

### 2. Set Appropriate Limits
```yaml
# Good: Set reasonable limits
max_cost_per_request: 0.10
max_latency_ms: 5000

# Bad: Set unrealistic limits
max_cost_per_request: 0.001
max_latency_ms: 100
```

### 3. Enable Monitoring in Production
```yaml
# Good: Enable monitoring
monitoring:
  enable_monitoring: true
  log_level: "INFO"

# Bad: Disable monitoring
monitoring:
  enable_monitoring: false
  log_level: "DEBUG"
```

### 4. Use Fallbacks
```yaml
# Good: Enable fallbacks
fallback_enabled: true
max_retries: 3

# Bad: Disable fallbacks
fallback_enabled: false
max_retries: 0
```

## Troubleshooting Configuration

### Common Issues

#### Invalid API Keys
```python
# Check API key format
import re

def validate_openai_key(key):
    return re.match(r'^sk-[A-Za-z0-9]{48}$', key) is not None

def validate_anthropic_key(key):
    return re.match(r'^sk-ant-[A-Za-z0-9]{48}$', key) is not None
```

#### Configuration File Not Found
```python
import os
from pathlib import Path

config_path = Path("config.yaml")
if not config_path.exists():
    print(f"Configuration file not found: {config_path}")
    # Create default configuration or handle error
```

#### Invalid Configuration Values
```python
from llm_dispatcher.exceptions import InvalidConfigurationError

try:
    switch = LLMSwitch(config={"max_cost_per_request": -1})
except InvalidConfigurationError as e:
    print(f"Invalid configuration: {e}")
```

## Next Steps

- [:octicons-rocket-24: Quick Start](quickstart.md) - Get started with basic usage
- [:octicons-gear-24: Advanced Features](../user-guide/advanced-features.md) - Explore advanced features
- [:octicons-chart-line-24: Performance Tips](../user-guide/performance.md) - Optimize performance

