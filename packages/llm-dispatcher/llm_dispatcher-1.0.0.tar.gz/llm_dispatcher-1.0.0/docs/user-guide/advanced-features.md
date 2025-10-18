# Advanced Features

This guide covers advanced features and capabilities of LLM-Dispatcher for power users and enterprise deployments.

## Custom Routing Logic

### Provider-Specific Routing

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
    elif request.estimated_tokens > 4000:
        return "google"  # Use Google for long content
    else:
        return "auto"  # Let LLM-Dispatcher decide

switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-..."},
        "anthropic": {"api_key": "sk-ant-..."},
        "google": {"api_key": "..."}
    },
    config={
        "custom_routing_logic": custom_routing_logic
    }
)
```

### Context-Aware Routing

```python
def context_aware_routing(request: TaskRequest, context: dict) -> str:
    """Route based on request context and history."""
    user_preference = context.get("user_preference")
    previous_provider = context.get("last_provider")
    cost_budget = context.get("cost_budget", 0.10)

    if user_preference:
        return user_preference

    if request.estimated_cost > cost_budget:
        return "google"  # Use cheaper provider

    if previous_provider == "openai" and request.task_type == TaskType.REASONING:
        return "anthropic"  # Try different provider for variety

    return "auto"

# Use with context
context = {
    "user_preference": "anthropic",
    "last_provider": "openai",
    "cost_budget": 0.05
}

decision = await switch.select_llm_with_context(request, context)
```

## Advanced Configuration

### Dynamic Configuration Updates

```python
from llm_dispatcher import get_global_switch

# Get current switch
switch = get_global_switch()

# Update configuration dynamically
switch.update_config({
    "optimization_strategy": "cost",
    "max_cost_per_request": 0.01,
    "fallback_enabled": True
})

# Add new provider at runtime
switch.add_provider("new_provider", {
    "api_key": "new-key",
    "models": ["model1", "model2"]
})

# Remove provider
switch.remove_provider("old_provider")
```

### Environment-Specific Configuration

```python
import os
from llm_dispatcher import LLMSwitch

def get_environment_config():
    """Get configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")

    base_config = {
        "fallback_enabled": True,
        "max_retries": 3
    }

    if env == "development":
        return {
            **base_config,
            "optimization_strategy": "cost",
            "max_cost_per_request": 0.01,
            "log_level": "DEBUG"
        }
    elif env == "staging":
        return {
            **base_config,
            "optimization_strategy": "balanced",
            "max_cost_per_request": 0.05,
            "log_level": "INFO"
        }
    elif env == "production":
        return {
            **base_config,
            "optimization_strategy": "performance",
            "max_cost_per_request": 0.50,
            "log_level": "WARNING",
            "monitoring": {
                "enable_monitoring": True,
                "metrics_retention_days": 90
            }
        }

switch = LLMSwitch(
    providers=get_providers_for_environment(),
    config=get_environment_config()
)
```

## Performance Optimization

### Caching Strategies

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.cache import SemanticCache
import functools

# Enable semantic caching
cache = SemanticCache(
    similarity_threshold=0.95,
    max_cache_size=1000
)

@llm_dispatcher(cache=cache)
def cached_generation(prompt: str) -> str:
    """Generation with semantic caching."""
    return prompt

# Manual cache management
@functools.lru_cache(maxsize=100)
@llm_dispatcher
def lru_cached_generation(prompt: str) -> str:
    """Generation with LRU caching."""
    return prompt

# Cache with TTL
from llm_dispatcher.cache import TTLCache

ttl_cache = TTLCache(ttl=3600)  # 1 hour TTL

@llm_dispatcher(cache=ttl_cache)
def ttl_cached_generation(prompt: str) -> str:
    """Generation with TTL caching."""
    return prompt
```

### Batch Processing

```python
from llm_dispatcher import LLMSwitch
import asyncio

async def batch_process(requests: list) -> list:
    """Process multiple requests efficiently."""
    switch = get_global_switch()

    # Group requests by provider for efficiency
    grouped_requests = switch.group_requests_by_provider(requests)

    results = []
    for provider, provider_requests in grouped_requests.items():
        # Process each provider's requests in parallel
        provider_results = await asyncio.gather(*[
            switch.process_request(req) for req in provider_requests
        ])
        results.extend(provider_results)

    return results

# Usage
requests = [
    TaskRequest(prompt="Generate code for sorting", task_type=TaskType.CODE_GENERATION),
    TaskRequest(prompt="Explain quantum computing", task_type=TaskType.REASONING),
    TaskRequest(prompt="Write a story", task_type=TaskType.TEXT_GENERATION)
]

results = await batch_process(requests)
```

### Load Balancing

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.load_balancer import RoundRobinBalancer

# Configure load balancing
switch = LLMSwitch(
    providers={
        "openai": {"api_key": "sk-...", "weight": 3},
        "anthropic": {"api_key": "sk-ant-...", "weight": 2},
        "google": {"api_key": "...", "weight": 1}
    },
    config={
        "load_balancer": RoundRobinBalancer(),
        "health_check_interval": 60
    }
)

# Health monitoring
async def monitor_health():
    """Monitor provider health."""
    for provider_name, provider in switch.providers.items():
        health = await provider.check_health()
        if not health.is_healthy:
            print(f"Provider {provider_name} is unhealthy: {health.reason}")
            # Automatically disable unhealthy providers
            switch.disable_provider(provider_name)
```

## Enterprise Features

### Multi-Tenant Support

```python
from llm_dispatcher import LLMSwitch
# Tenant management not available - enterprise features removed

# Initialize tenant manager
tenant_manager = TenantManager()

# Create tenant-specific switches
tenant_switch = tenant_manager.create_tenant_switch(
    tenant_id="company_a",
    config={
        "max_cost_per_request": 0.10,
        "allowed_providers": ["openai", "anthropic"],
        "quota_limit": 1000
    }
)

# Use tenant-specific switch
@tenant_switch.route
def tenant_specific_generation(prompt: str) -> str:
    """Generation with tenant-specific configuration."""
    return prompt

# Monitor tenant usage
usage = tenant_manager.get_tenant_usage("company_a")
print(f"Tenant usage: {usage.requests_used}/{usage.quota_limit}")
```

### Audit Logging

```python
from llm_dispatcher import LLMSwitch
# Audit logging not available - enterprise features removed

# Configure audit logging
audit_logger = AuditLogger(
    log_level="INFO",
    include_request_data=True,
    include_response_data=False,  # For privacy
    retention_days=90
)

switch = LLMSwitch(
    providers={...},
    config={
        "audit_logger": audit_logger
    }
)

# Audit logs are automatically created for all requests
# Access audit logs
logs = audit_logger.get_logs(
    start_date="2024-01-01",
    end_date="2024-01-31",
    tenant_id="company_a"
)
```

### Compliance and Security

```python
from llm_dispatcher import LLMSwitch
# Compliance management not available - enterprise features removed

# Configure compliance
compliance_manager = ComplianceManager(
    data_residency="EU",  # Ensure EU data residency
    encryption_required=True,
    audit_required=True
)

switch = LLMSwitch(
    providers={...},
    config={
        "compliance_manager": compliance_manager
    }
)

# Check compliance
compliance_status = compliance_manager.check_compliance(request)
if not compliance_status.is_compliant:
    raise ComplianceError(f"Request not compliant: {compliance_status.reason}")
```

## Monitoring and Analytics

### Real-Time Metrics

```python
from llm_dispatcher import get_global_switch
from llm_dispatcher.monitoring import MetricsCollector

# Get metrics collector
switch = get_global_switch()
metrics = switch.get_metrics_collector()

# Real-time metrics
realtime_metrics = metrics.get_realtime_metrics()
print(f"Current requests/minute: {realtime_metrics.requests_per_minute}")
print(f"Average latency: {realtime_metrics.avg_latency}ms")
print(f"Success rate: {realtime_metrics.success_rate:.2%}")

# Provider-specific metrics
for provider, provider_metrics in realtime_metrics.providers.items():
    print(f"{provider}: {provider_metrics.requests} requests, {provider_metrics.avg_latency}ms avg")
```

### Custom Dashboards

```python
from llm_dispatcher.monitoring import DashboardBuilder

# Create custom dashboard
dashboard = DashboardBuilder()
dashboard.add_metric("requests_per_minute", "line")
dashboard.add_metric("success_rate", "gauge")
dashboard.add_metric("cost_per_request", "histogram")
dashboard.add_metric("provider_distribution", "pie")

# Export dashboard configuration
dashboard_config = dashboard.export_config()
# Use with your preferred dashboard tool (Grafana, etc.)
```

### Alerting

```python
from llm_dispatcher.monitoring import AlertManager

# Configure alerts
alert_manager = AlertManager()
alert_manager.add_alert(
    name="high_latency",
    condition=lambda metrics: metrics.avg_latency > 5000,
    severity="warning",
    message="Average latency is above 5 seconds"
)

alert_manager.add_alert(
    name="low_success_rate",
    condition=lambda metrics: metrics.success_rate < 0.95,
    severity="critical",
    message="Success rate is below 95%"
)

# Check alerts
alerts = alert_manager.check_alerts(current_metrics)
for alert in alerts:
    print(f"ALERT: {alert.name} - {alert.message}")
```

## Advanced Error Handling

### Custom Error Handlers

```python
from llm_dispatcher.exceptions import LLMDispatcherError
from llm_dispatcher.error_handling import ErrorHandler

class CustomErrorHandler(ErrorHandler):
    def handle_provider_error(self, error: ProviderError) -> str:
        """Custom provider error handling."""
        if isinstance(error, ProviderRateLimitError):
            # Implement exponential backoff
            return self.retry_with_backoff(error)
        elif isinstance(error, ProviderQuotaExceededError):
            # Switch to alternative provider
            return self.switch_provider(error)
        else:
            return self.default_handler(error)

    def handle_timeout_error(self, error: RequestTimeoutError) -> str:
        """Custom timeout handling."""
        # Try with a faster provider
        return self.retry_with_faster_provider(error)

# Use custom error handler
switch = LLMSwitch(
    providers={...},
    config={
        "error_handler": CustomErrorHandler()
    }
)
```

### Circuit Breaker Pattern

```python
from llm_dispatcher.error_handling import CircuitBreaker

# Configure circuit breaker
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=ProviderError
)

@circuit_breaker
@llm_dispatcher
def resilient_generation(prompt: str) -> str:
    """Generation with circuit breaker protection."""
    return prompt

# Check circuit breaker status
for provider_name, provider in switch.providers.items():
    if circuit_breaker.is_open(provider_name):
        print(f"Circuit breaker is OPEN for {provider_name}")
    elif circuit_breaker.is_half_open(provider_name):
        print(f"Circuit breaker is HALF-OPEN for {provider_name}")
    else:
        print(f"Circuit breaker is CLOSED for {provider_name}")
```

## Best Practices

### 1. **Use Appropriate Optimization Strategies**

```python
# For cost-sensitive applications
@llm_dispatcher(optimization_strategy="cost")
def cost_optimized_generation(prompt: str) -> str:
    return prompt

# For real-time applications
@llm_dispatcher(optimization_strategy="speed")
def speed_optimized_generation(prompt: str) -> str:
    return prompt

# For quality-critical applications
@llm_dispatcher(optimization_strategy="performance")
def quality_optimized_generation(prompt: str) -> str:
    return prompt
```

### 2. **Implement Proper Monitoring**

```python
# Monitor key metrics
def monitor_performance():
    metrics = switch.get_performance_metrics()
    if metrics.success_rate < 0.95:
        logger.warning("Success rate below threshold")
    if metrics.avg_latency > 5000:
        logger.warning("Average latency too high")
    if metrics.cost_per_request > 0.10:
        logger.warning("Cost per request too high")
```

### 3. **Use Caching Strategically**

```python
# Cache expensive operations
@llm_dispatcher(cache=SemanticCache(similarity_threshold=0.95))
def expensive_generation(prompt: str) -> str:
    return prompt

# Don't cache time-sensitive operations
@llm_dispatcher(cache=None)
def real_time_generation(prompt: str) -> str:
    return prompt
```

### 4. **Handle Errors Gracefully**

```python
# Always enable fallbacks
@llm_dispatcher(fallback_enabled=True, max_retries=3)
def reliable_generation(prompt: str) -> str:
    return prompt

# Implement custom error handling
try:
    result = reliable_generation("Your prompt")
except LLMDispatcherError as e:
    logger.error(f"Generation failed: {e}")
    # Implement fallback logic
    result = "Fallback response"
```

## Next Steps

- [:octicons-eye-24: Multimodal Support](multimodal.md) - Working with images and audio
- [:octicons-lightning-bolt-24: Streaming](streaming.md) - Real-time response streaming
- [:octicons-shield-check-24: Error Handling](error-handling.md) - Robust error handling
- [:octicons-chart-line-24: Performance Tips](performance.md) - Optimization strategies
