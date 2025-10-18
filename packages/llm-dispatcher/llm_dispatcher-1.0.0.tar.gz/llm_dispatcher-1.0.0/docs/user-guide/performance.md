# Performance Tips

This guide provides comprehensive performance optimization strategies for LLM-Dispatcher to help you achieve the best possible performance in your applications.

## Overview

Performance optimization in LLM-Dispatcher involves:

- **Latency optimization** - Reducing response times
- **Cost optimization** - Minimizing API costs
- **Throughput optimization** - Maximizing requests per second
- **Resource optimization** - Efficient memory and CPU usage

## Optimization Strategies

### Cost Optimization

#### Use Cost-Efficient Models

```python
from llm_dispatcher import llm_dispatcher
from llm_dispatcher.config.settings import OptimizationStrategy

@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.COST,
    max_cost=0.01
)
def cost_optimized_generation(prompt: str) -> str:
    """Optimized for cost efficiency."""
    return prompt

# Automatically selects cheaper models when appropriate
result = cost_optimized_generation("Simple question")
```

#### Implement Cost Limits

```python
@llm_dispatcher(
    max_cost_per_request=0.05,
    daily_cost_limit=10.0,
    monthly_cost_limit=100.0
)
def budget_controlled_generation(prompt: str) -> str:
    """Generation with strict cost controls."""
    return prompt
```

#### Use Caching for Repeated Requests

```python
from llm_dispatcher.cache import SemanticCache

cache = SemanticCache(
    similarity_threshold=0.95,
    max_cache_size=1000
)

@llm_dispatcher(cache=cache)
def cached_generation(prompt: str) -> str:
    """Generation with intelligent caching."""
    return prompt

# Similar requests will use cached responses
```

### Speed Optimization

#### Use Fast Models

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.SPEED,
    max_latency=2000
)
def speed_optimized_generation(prompt: str) -> str:
    """Optimized for speed."""
    return prompt

# Automatically selects faster models
result = speed_optimized_generation("Quick question")
```

#### Implement Connection Pooling

```python
from llm_dispatcher import LLMSwitch

switch = LLMSwitch(
    providers={...},
    config={
        "connection_pooling": True,
        "max_connections": 100,
        "keep_alive": True
    }
)
```

#### Use Async Operations

```python
import asyncio
from llm_dispatcher import llm_dispatcher

@llm_dispatcher
async def async_generation(prompt: str) -> str:
    """Async generation for better concurrency."""
    return prompt

# Process multiple requests concurrently
async def process_multiple_requests(prompts: list):
    tasks = [async_generation(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results
```

### Quality Optimization

#### Use High-Quality Models

```python
@llm_dispatcher(
    optimization_strategy=OptimizationStrategy.PERFORMANCE
)
def quality_optimized_generation(prompt: str) -> str:
    """Optimized for best quality."""
    return prompt

# Automatically selects highest quality models
result = quality_optimized_generation("Complex analysis")
```

#### Implement Quality-Based Routing

```python
from llm_dispatcher import LLMSwitch
from llm_dispatcher.core.base import TaskRequest, TaskType

def quality_based_routing(request: TaskRequest) -> str:
    """Route based on quality requirements."""
    if request.task_type == TaskType.CODE_GENERATION:
        return "openai"  # Best for code
    elif request.task_type == TaskType.REASONING:
        return "anthropic"  # Best for reasoning
    else:
        return "auto"

switch = LLMSwitch(
    providers={...},
    config={
        "custom_routing_logic": quality_based_routing
    }
)
```

## Caching Strategies

### Semantic Caching

```python
from llm_dispatcher.cache import SemanticCache

# Cache based on semantic similarity
semantic_cache = SemanticCache(
    similarity_threshold=0.95,
    max_cache_size=1000,
    embedding_model="text-embedding-ada-002"
)

@llm_dispatcher(cache=semantic_cache)
def semantically_cached_generation(prompt: str) -> str:
    """Generation with semantic caching."""
    return prompt

# Similar prompts will use cached responses
```

### TTL Caching

```python
from llm_dispatcher.cache import TTLCache

# Cache with time-to-live
ttl_cache = TTLCache(
    ttl=3600,  # 1 hour
    max_cache_size=500
)

@llm_dispatcher(cache=ttl_cache)
def ttl_cached_generation(prompt: str) -> str:
    """Generation with TTL caching."""
    return prompt
```

### LRU Caching

```python
from llm_dispatcher.cache import LRUCache

# Least recently used cache
lru_cache = LRUCache(
    max_cache_size=1000,
    max_memory_mb=100
)

@llm_dispatcher(cache=lru_cache)
def lru_cached_generation(prompt: str) -> str:
    """Generation with LRU caching."""
    return prompt
```

## Batch Processing

### Efficient Batch Operations

```python
from llm_dispatcher import LLMSwitch
import asyncio

async def batch_process(requests: list):
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
    TaskRequest(prompt="Question 1", task_type=TaskType.TEXT_GENERATION),
    TaskRequest(prompt="Question 2", task_type=TaskType.TEXT_GENERATION),
    TaskRequest(prompt="Question 3", task_type=TaskType.TEXT_GENERATION)
]

results = await batch_process(requests)
```

### Request Batching

```python
from llm_dispatcher.batching import RequestBatcher

# Batch requests for efficiency
batcher = RequestBatcher(
    batch_size=10,
    batch_timeout=1000  # 1 second
)

@llm_dispatcher(batcher=batcher)
def batched_generation(prompt: str) -> str:
    """Generation with request batching."""
    return prompt
```

## Load Balancing

### Provider Load Balancing

```python
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
```

### Weighted Load Balancing

```python
from llm_dispatcher.load_balancer import WeightedBalancer

# Weighted load balancing based on performance
weighted_balancer = WeightedBalancer(
    weights={
        "openai": 0.5,
        "anthropic": 0.3,
        "google": 0.2
    }
)

switch = LLMSwitch(
    providers={...},
    config={
        "load_balancer": weighted_balancer
    }
)
```

## Monitoring and Analytics

### Performance Metrics

```python
from llm_dispatcher.monitoring import MetricsCollector

# Monitor performance metrics
metrics = MetricsCollector()

@llm_dispatcher
def monitored_generation(prompt: str) -> str:
    """Generation with performance monitoring."""
    return prompt

# Get performance statistics
stats = monitor.get_statistics()
print(f"Average latency: {stats.avg_latency}ms")
print(f"Success rate: {stats.success_rate:.2%}")
print(f"Cost per request: ${stats.avg_cost:.4f}")
```

### Real-Time Monitoring

```python
from llm_dispatcher.monitoring import MetricsCollector

# Real-time performance monitoring
# Real-time performance monitoring with available tools
metrics_collector = MetricsCollector()
await metrics_collector.start_collection()

@llm_dispatcher
def realtime_monitored_generation(prompt: str) -> str:
    """Generation with real-time monitoring."""
    return prompt
```

## Memory Optimization

### Efficient Data Structures

```python
from llm_dispatcher import LLMSwitch

# Configure memory-efficient settings
switch = LLMSwitch(
    providers={...},
    config={
        "max_memory_mb": 512,
        "garbage_collection_interval": 300,  # 5 minutes
        "cache_compression": True
    }
)
```

### Memory Monitoring

```python
from llm_dispatcher.monitoring import MemoryMonitor

# Monitor memory usage
memory_monitor = MemoryMonitor(
    max_memory_mb=1024,
    alert_threshold=0.8  # 80% of max memory
)

@llm_dispatcher(monitor=memory_monitor)
def memory_monitored_generation(prompt: str) -> str:
    """Generation with memory monitoring."""
    return prompt
```

## Network Optimization

### Connection Optimization

```python
from llm_dispatcher import LLMSwitch

# Optimize network connections
switch = LLMSwitch(
    providers={...},
    config={
        "connection_pooling": True,
        "max_connections": 100,
        "keep_alive": True,
        "timeout": 30,
        "retry_attempts": 3
    }
)
```

### Compression

```python
from llm_dispatcher import LLMSwitch

# Enable compression for large requests
switch = LLMSwitch(
    providers={...},
    config={
        "compression": True,
        "compression_threshold": 1024  # Compress requests > 1KB
    }
)
```

## Best Practices

### 1. **Choose Appropriate Optimization Strategy**

```python
# For cost-sensitive applications
@llm_dispatcher(optimization_strategy=OptimizationStrategy.COST)
def cost_optimized(prompt: str) -> str:
    return prompt

# For real-time applications
@llm_dispatcher(optimization_strategy=OptimizationStrategy.SPEED)
def speed_optimized(prompt: str) -> str:
    return prompt

# For quality-critical applications
@llm_dispatcher(optimization_strategy=OptimizationStrategy.PERFORMANCE)
def quality_optimized(prompt: str) -> str:
    return prompt
```

### 2. **Implement Proper Caching**

```python
# Use semantic caching for similar requests
@llm_dispatcher(cache=SemanticCache(similarity_threshold=0.95))
def cached_generation(prompt: str) -> str:
    return prompt

# Use TTL caching for time-sensitive data
@llm_dispatcher(cache=TTLCache(ttl=3600))
def ttl_cached_generation(prompt: str) -> str:
    return prompt
```

### 3. **Use Async Operations**

```python
# Process multiple requests concurrently
async def process_requests(prompts: list):
    tasks = [generate_text(prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return results
```

### 4. **Monitor Performance**

```python
# Always monitor performance metrics
def monitor_performance():
    metrics = monitor.get_statistics()
    if metrics.avg_latency > 5000:
        logger.warning("Average latency too high")
    if metrics.success_rate < 0.95:
        logger.warning("Success rate below threshold")
    if metrics.avg_cost > 0.10:
        logger.warning("Average cost too high")
```

### 5. **Implement Proper Error Handling**

```python
# Always enable fallbacks for reliability
@llm_dispatcher(
    fallback_enabled=True,
    max_retries=3,
    retry_delay=1000
)
def reliable_generation(prompt: str) -> str:
    return prompt
```

## Performance Testing

### Load Testing

```python
from llm_dispatcher.testing import LoadTester

# Test performance under load
load_tester = LoadTester(
    concurrent_requests=100,
    duration=300,  # 5 minutes
    ramp_up_time=60  # 1 minute
)

results = load_tester.run_test(
    lambda: generate_text("Test prompt")
)

print(f"Average latency: {results.avg_latency}ms")
print(f"Throughput: {results.throughput} requests/second")
print(f"Error rate: {results.error_rate:.2%}")
```

### Stress Testing

```python
from llm_dispatcher.testing import StressTester

# Test system limits
stress_tester = StressTester(
    max_concurrent_requests=1000,
    duration=600  # 10 minutes
)

results = stress_tester.run_test(
    lambda: generate_text("Stress test prompt")
)

print(f"Max concurrent requests: {results.max_concurrent}")
print(f"System breakdown point: {results.breakdown_point}")
```

## Performance Tuning

### Provider-Specific Tuning

```python
# Tune OpenAI provider
openai_config = {
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
}

# Tune Anthropic provider
anthropic_config = {
    "max_tokens": 4096,
    "temperature": 0.7,
    "timeout": 30,
    "max_retries": 3
}

switch = LLMSwitch(
    providers={
        "openai": {**openai_config, "api_key": "sk-..."},
        "anthropic": {**anthropic_config, "api_key": "sk-ant-..."}
    }
)
```

### System-Level Tuning

```python
# Tune system-level settings
system_config = {
    "max_memory_mb": 1024,
    "max_connections": 100,
    "connection_timeout": 30,
    "read_timeout": 60,
    "write_timeout": 60
}

switch = LLMSwitch(
    providers={...},
    config=system_config
)
```

## Next Steps

- [:octicons-gear-24: Advanced Features](advanced-features.md) - Advanced capabilities
- [:octicons-shield-check-24: Error Handling](error-handling.md) - Robust error handling
- [:octicons-lightning-bolt-24: Streaming](streaming.md) - Real-time response streaming
- [:octicons-eye-24: Multimodal Support](multimodal.md) - Working with images and audio
