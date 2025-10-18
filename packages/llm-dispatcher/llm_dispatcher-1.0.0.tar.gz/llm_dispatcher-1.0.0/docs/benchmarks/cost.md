# Cost Benchmarks

Cost benchmarks analyze the cost-effectiveness of different LLM providers and models, helping you optimize your spending while maintaining quality.

## Overview

Cost benchmarks evaluate:

- **Cost per request** - Total cost for individual requests
- **Cost per token** - Cost efficiency based on token usage
- **Total cost** - Overall spending across all requests
- **Cost per quality unit** - Cost relative to response quality
- **ROI analysis** - Return on investment for different configurations

## Basic Cost Benchmarking

### Simple Cost Analysis

```python
from llm_dispatcher.benchmarks import CostBenchmark

# Create cost benchmark
benchmark = CostBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=10
)

# Run benchmark
results = await benchmark.run()

# Analyze results
print(f"Average cost per request: ${results.avg_cost:.4f}")
print(f"Total cost: ${results.total_cost:.4f}")
print(f"Cost per token: ${results.cost_per_token:.6f}")
print(f"Total tokens used: {results.total_tokens}")
```

### Provider Cost Comparison

```python
# Compare costs across providers
benchmark = CostBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=20
)

results = await benchmark.run()

# Compare provider costs
for provider, metrics in results.provider_metrics.items():
    print(f"{provider}:")
    print(f"  Average cost per request: ${metrics.avg_cost:.4f}")
    print(f"  Total cost: ${metrics.total_cost:.4f}")
    print(f"  Cost per token: ${metrics.cost_per_token:.6f}")
    print(f"  Total tokens: {metrics.total_tokens}")
```

## Advanced Cost Analysis

### Cost vs Quality Analysis

```python
from llm_dispatcher.benchmarks import CostQualityBenchmark

# Analyze cost vs quality trade-offs
benchmark = CostQualityBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    quality_metrics=["accuracy", "relevance", "creativity"],
    iterations=20
)

results = await benchmark.run()

# Analyze cost vs quality
for provider, metrics in results.provider_metrics.items():
    print(f"{provider}:")
    print(f"  Cost per request: ${metrics.avg_cost:.4f}")
    print(f"  Quality score: {metrics.quality_score:.2f}")
    print(f"  Cost per quality unit: ${metrics.cost_per_quality:.4f}")
    print(f"  Value score: {metrics.value_score:.2f}")
```

### Cost Optimization Analysis

```python
from llm_dispatcher.benchmarks import CostOptimizationBenchmark

# Analyze cost optimization strategies
benchmark = CostOptimizationBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku", "gemini-2.5-pro", "gemini-2.5-flash"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    optimization_strategies=["cost", "speed", "quality", "balanced"],
    iterations=20
)

results = await benchmark.run()

# Analyze optimization strategies
for strategy, metrics in results.strategy_metrics.items():
    print(f"{strategy} strategy:")
    print(f"  Average cost: ${metrics.avg_cost:.4f}")
    print(f"  Average latency: {metrics.avg_latency}ms")
    print(f"  Quality score: {metrics.quality_score:.2f}")
    print(f"  Overall score: {metrics.overall_score:.2f}")
```

### Bulk Cost Analysis

```python
from llm_dispatcher.benchmarks import BulkCostBenchmark

# Analyze costs for bulk operations
benchmark = BulkCostBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    batch_sizes=[1, 10, 50, 100, 500],
    iterations=10
)

results = await benchmark.run()

# Analyze bulk costs
for batch_size, metrics in results.batch_metrics.items():
    print(f"Batch size {batch_size}:")
    print(f"  Average cost per request: ${metrics.avg_cost_per_request:.4f}")
    print(f"  Total cost: ${metrics.total_cost:.4f}")
    print(f"  Cost efficiency: {metrics.cost_efficiency:.2f}")
```

## Cost Metrics

### Detailed Cost Analysis

```python
# Detailed cost metrics
cost_metrics = results.get_cost_metrics()
print(f"Average cost per request: ${cost_metrics.avg_cost:.4f}")
print(f"Median cost per request: ${cost_metrics.median_cost:.4f}")
print(f"Min cost per request: ${cost_metrics.min_cost:.4f}")
print(f"Max cost per request: ${cost_metrics.max_cost:.4f}")
print(f"Standard deviation: ${cost_metrics.std_cost:.4f}")
print(f"Total cost: ${cost_metrics.total_cost:.4f}")
print(f"Cost per token: ${cost_metrics.cost_per_token:.6f}")
```

### Token Usage Analysis

```python
# Token usage analysis
token_metrics = results.get_token_metrics()
print(f"Average tokens per request: {token_metrics.avg_tokens}")
print(f"Total tokens used: {token_metrics.total_tokens}")
print(f"Input tokens: {token_metrics.input_tokens}")
print(f"Output tokens: {token_metrics.output_tokens}")
print(f"Token efficiency: {token_metrics.token_efficiency:.2f}")
```

### Cost Distribution Analysis

```python
# Cost distribution analysis
distribution = results.get_cost_distribution()
print(f"Cost distribution:")
print(f"  < $0.01: {distribution.under_1_cent:.2%}")
print(f"  $0.01 - $0.05: {distribution.1_to_5_cents:.2%}")
print(f"  $0.05 - $0.10: {distribution.5_to_10_cents:.2%}")
print(f"  > $0.10: {distribution.over_10_cents:.2%}")
```

## Cost Optimization Strategies

### Model Selection for Cost Optimization

```python
# Test different models for cost optimization
models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku", "gemini-2.5-pro", "gemini-2.5-flash"]

for model in models:
    benchmark = CostBenchmark(
        providers=["openai" if "gpt" in model else "anthropic" if "claude" in model else "google"],
        models=[model],
        test_prompts=["Write a short story"],
        iterations=20
    )

    results = await benchmark.run()
    print(f"{model}: ${results.avg_cost:.4f} avg cost")
```

### Token Limit Optimization

```python
# Test different token limits for cost optimization
token_limits = [100, 500, 1000, 2000, 4000]

for limit in token_limits:
    benchmark = CostBenchmark(
        test_prompts=["Write a short story"],
        iterations=20,
        max_tokens=limit
    )

    results = await benchmark.run()
    print(f"Token limit {limit}: ${results.avg_cost:.4f} avg cost")
```

### Temperature Optimization

```python
# Test different temperatures for cost optimization
temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]

for temp in temperatures:
    benchmark = CostBenchmark(
        test_prompts=["Write a short story"],
        iterations=20,
        temperature=temp
    )

    results = await benchmark.run()
    print(f"Temperature {temp}: ${results.avg_cost:.4f} avg cost")
```

## Cost Monitoring

### Real-time Cost Monitoring

```python
from llm_dispatcher.benchmarks import RealtimeCostMonitor

# Monitor costs in real-time
monitor = RealtimeCostMonitor(
    test_prompts=["Write a short story"],
    duration=300,  # 5 minutes
    check_interval=10  # Check every 10 seconds
)

# Start monitoring
await monitor.start()

# Get real-time cost metrics
while monitor.is_running():
    metrics = monitor.get_current_metrics()
    print(f"Current cost: ${metrics.current_cost:.4f}")
    print(f"Cost per minute: ${metrics.cost_per_minute:.4f}")
    print(f"Projected daily cost: ${metrics.projected_daily_cost:.2f}")
    await asyncio.sleep(10)

# Stop monitoring
await monitor.stop()
```

### Cost Alerts

```python
# Set up cost alerts
monitor = RealtimeCostMonitor(
    test_prompts=["Write a short story"],
    duration=300,
    check_interval=10,
    alerts={
        "cost_threshold": 0.10,  # Alert if cost > $0.10
        "daily_budget": 10.0,  # Alert if daily budget exceeded
        "cost_per_minute_threshold": 0.01  # Alert if cost per minute > $0.01
    }
)

# Start monitoring with alerts
await monitor.start()
```

## Cost Analysis

### Statistical Analysis

```python
from llm_dispatcher.benchmarks.analysis import CostAnalyzer

# Analyze cost results
analyzer = CostAnalyzer(results)

# Statistical analysis
stats = analyzer.get_statistical_analysis()
print(f"Mean cost: ${stats.cost.mean:.4f}")
print(f"Standard deviation: ${stats.cost.std:.4f}")
print(f"95th percentile: ${stats.cost.p95:.4f}")
print(f"99th percentile: ${stats.cost.p99:.4f}")

# Distribution analysis
distribution = analyzer.get_distribution_analysis()
print(f"Cost distribution: {distribution.cost}")
print(f"Token distribution: {distribution.tokens}")
```

### Trend Analysis

```python
# Analyze cost trends
trends = analyzer.get_trend_analysis()
print(f"Cost trend: {trends.cost.direction}")
print(f"Token usage trend: {trends.tokens.direction}")
print(f"Efficiency trend: {trends.efficiency.direction}")
```

### Comparative Analysis

```python
# Compare costs across providers
comparison = analyzer.compare_providers()
for provider, metrics in comparison.items():
    print(f"{provider}:")
    print(f"  Average cost: ${metrics.avg_cost:.4f}")
    print(f"  Cost per token: ${metrics.cost_per_token:.6f}")
    print(f"  Token efficiency: {metrics.token_efficiency:.2f}")
    print(f"  Value score: {metrics.value_score:.2f}")
```

## Cost Reports

### Generate Cost Reports

```python
from llm_dispatcher.benchmarks.reports import CostReporter

# Generate cost report
reporter = CostReporter(results)
report = reporter.generate_report("cost_report.html")

# Generate cost charts
charts = reporter.generate_charts("cost_charts.png")
```

### Custom Cost Reports

```python
# Generate custom cost report
custom_report = reporter.generate_custom_report(
    template="custom_cost_template.html",
    output_file="custom_cost_report.html",
    include_charts=True,
    include_raw_data=True,
    include_statistical_analysis=True
)
```

## Cost Optimization Best Practices

### 1. **Choose Cost-Effective Models**

```python
# Good: Use cost-effective models for simple tasks
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-3.5-turbo"],  # Cheaper model
    max_tokens=500  # Limit tokens
)
def simple_generation(prompt: str) -> str:
    return prompt

# Avoid: Using expensive models for simple tasks
@llm_dispatcher(
    providers=["openai"],
    models=["gpt-4"],  # Expensive model
    max_tokens=2000  # High token limit
)
def simple_generation(prompt: str) -> str:
    return prompt
```

### 2. **Optimize Token Usage**

```python
# Good: Optimize token usage
@llm_dispatcher(
    max_tokens=1000,  # Appropriate token limit
    temperature=0.7  # Standard temperature
)
def optimized_generation(prompt: str) -> str:
    return prompt

# Avoid: Excessive token usage
@llm_dispatcher(
    max_tokens=4000,  # High token limit
    temperature=0.9  # High temperature
)
def optimized_generation(prompt: str) -> str:
    return prompt
```

### 3. **Use Caching for Repeated Requests**

```python
# Good: Use caching for cost optimization
@llm_dispatcher(
    cache=SemanticCache(similarity_threshold=0.95)
)
def cached_generation(prompt: str) -> str:
    return prompt

# Avoid: No caching for repeated requests
@llm_dispatcher()
def cached_generation(prompt: str) -> str:
    return prompt
```

### 4. **Monitor Costs Continuously**

```python
# Good: Monitor costs continuously
monitor = RealtimeCostMonitor(
    test_prompts=["Write a short story"],
    duration=300,
    check_interval=10,
    alerts={
        "cost_threshold": 0.10,
        "daily_budget": 10.0
    }
)

# Avoid: No cost monitoring
# No monitoring setup
```

### 5. **Analyze Cost vs Quality Trade-offs**

```python
# Good: Analyze cost vs quality trade-offs
benchmark = CostQualityBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=["Write a short story"],
    quality_metrics=["accuracy", "relevance", "creativity"],
    iterations=20
)

# Avoid: Only looking at cost without considering quality
benchmark = CostBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=["Write a short story"],
    iterations=20
)
```

## Next Steps

- [:octicons-chart-line-24: Benchmark Overview](overview.md) - Comprehensive benchmarking guide
- [:octicons-chart-line-24: Performance Benchmarks](performance.md) - Performance testing and optimization
- [:octicons-star-24: Quality Benchmarks](quality.md) - Quality assessment and evaluation
- [:octicons-gear-24: Custom Benchmarks](custom.md) - Creating custom benchmark criteria
