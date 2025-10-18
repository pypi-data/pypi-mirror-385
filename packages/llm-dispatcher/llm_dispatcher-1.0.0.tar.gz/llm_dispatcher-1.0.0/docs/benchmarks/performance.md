# Performance Benchmarks

Performance benchmarks measure the speed, efficiency, and scalability of different LLM providers and models.

## Overview

Performance benchmarks evaluate:

- **Latency** - Response time for individual requests
- **Throughput** - Requests processed per second
- **Concurrency** - Performance under concurrent load
- **Scalability** - Performance as load increases
- **Resource usage** - Memory and CPU utilization

## Basic Performance Benchmarking

### Simple Latency Test

```python
from llm_dispatcher.benchmarks import PerformanceBenchmark

# Create performance benchmark
benchmark = PerformanceBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=10,
    concurrent_requests=1
)

# Run benchmark
results = await benchmark.run()

# Analyze results
print(f"Average latency: {results.avg_latency}ms")
print(f"Min latency: {results.min_latency}ms")
print(f"Max latency: {results.max_latency}ms")
print(f"Standard deviation: {results.std_latency}ms")
```

### Throughput Test

```python
# Test throughput with concurrent requests
benchmark = PerformanceBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=100,
    concurrent_requests=10  # 10 concurrent requests
)

results = await benchmark.run()
print(f"Throughput: {results.throughput} requests/second")
print(f"Average latency: {results.avg_latency}ms")
```

## Advanced Performance Testing

### Load Testing

```python
from llm_dispatcher.benchmarks import LoadTestBenchmark

# Create load test benchmark
load_test = LoadTestBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    concurrent_users=[1, 5, 10, 20, 50],  # Test different load levels
    duration_per_level=60,  # 60 seconds per load level
    ramp_up_time=10  # 10 seconds ramp up
)

# Run load test
results = await load_test.run()

# Analyze results
for load_level, metrics in results.load_levels.items():
    print(f"Load Level {load_level} users:")
    print(f"  Average latency: {metrics.avg_latency}ms")
    print(f"  Throughput: {metrics.throughput} requests/second")
    print(f"  Error rate: {metrics.error_rate:.2%}")
    print(f"  Success rate: {metrics.success_rate:.2%}")
```

### Stress Testing

```python
from llm_dispatcher.benchmarks import StressTestBenchmark

# Create stress test benchmark
stress_test = StressTestBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    max_concurrent_users=100,
    duration=300,  # 5 minutes
    ramp_up_time=60  # 1 minute ramp up
)

# Run stress test
results = await stress_test.run()

# Analyze results
print(f"Maximum concurrent users: {results.max_concurrent_users}")
print(f"Breakdown point: {results.breakdown_point}")
print(f"Peak throughput: {results.peak_throughput} requests/second")
print(f"Average latency at peak: {results.avg_latency_at_peak}ms")
```

### Endurance Testing

```python
from llm_dispatcher.benchmarks import EnduranceTestBenchmark

# Create endurance test benchmark
endurance_test = EnduranceTestBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    concurrent_users=10,
    duration=3600,  # 1 hour
    check_interval=300  # Check every 5 minutes
)

# Run endurance test
results = await endurance_test.run()

# Analyze results
print(f"Test duration: {results.duration} seconds")
print(f"Total requests: {results.total_requests}")
print(f"Average latency: {results.avg_latency}ms")
print(f"Latency degradation: {results.latency_degradation:.2%}")
print(f"Error rate: {results.error_rate:.2%}")
```

## Provider Comparison

### Multi-Provider Performance Test

```python
from llm_dispatcher.benchmarks import MultiProviderBenchmark

# Create multi-provider benchmark
multi_provider_test = MultiProviderBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=20,
    concurrent_requests=5
)

# Run benchmark
results = await multi_provider_test.run()

# Compare providers
for provider, metrics in results.provider_metrics.items():
    print(f"{provider}:")
    print(f"  Average latency: {metrics.avg_latency}ms")
    print(f"  Min latency: {metrics.min_latency}ms")
    print(f"  Max latency: {metrics.max_latency}ms")
    print(f"  Throughput: {metrics.throughput} requests/second")
    print(f"  Success rate: {metrics.success_rate:.2%}")
```

### Model Comparison

```python
# Compare different models from the same provider
model_comparison = MultiProviderBenchmark(
    providers=["openai"],
    models=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=20,
    concurrent_requests=5
)

results = await model_comparison.run()

# Compare models
for model, metrics in results.model_metrics.items():
    print(f"{model}:")
    print(f"  Average latency: {metrics.avg_latency}ms")
    print(f"  Throughput: {metrics.throughput} requests/second")
    print(f"  Success rate: {metrics.success_rate:.2%}")
```

## Performance Metrics

### Latency Metrics

```python
# Detailed latency analysis
latency_metrics = results.get_latency_metrics()
print(f"Average latency: {latency_metrics.avg}ms")
print(f"Median latency: {latency_metrics.median}ms")
print(f"95th percentile: {latency_metrics.p95}ms")
print(f"99th percentile: {latency_metrics.p99}ms")
print(f"Standard deviation: {latency_metrics.std}ms")
print(f"Min latency: {latency_metrics.min}ms")
print(f"Max latency: {latency_metrics.max}ms")
```

### Throughput Metrics

```python
# Detailed throughput analysis
throughput_metrics = results.get_throughput_metrics()
print(f"Average throughput: {throughput_metrics.avg} requests/second")
print(f"Peak throughput: {throughput_metrics.peak} requests/second")
print(f"Sustained throughput: {throughput_metrics.sustained} requests/second")
print(f"Throughput variance: {throughput_metrics.variance}")
```

### Error Metrics

```python
# Error analysis
error_metrics = results.get_error_metrics()
print(f"Total errors: {error_metrics.total_errors}")
print(f"Error rate: {error_metrics.error_rate:.2%}")
print(f"Success rate: {error_metrics.success_rate:.2%}")
print(f"Timeout rate: {error_metrics.timeout_rate:.2%}")
print(f"Rate limit rate: {error_metrics.rate_limit_rate:.2%}")
```

## Performance Optimization

### Latency Optimization

```python
# Test different configurations for latency optimization
configurations = [
    {"max_tokens": 100, "temperature": 0.1},
    {"max_tokens": 500, "temperature": 0.1},
    {"max_tokens": 1000, "temperature": 0.1},
    {"max_tokens": 2000, "temperature": 0.1}
]

for config in configurations:
    benchmark = PerformanceBenchmark(
        test_prompts=["Write a short story"],
        iterations=10,
        concurrent_requests=1,
        **config
    )

    results = await benchmark.run()
    print(f"Config {config}: {results.avg_latency}ms avg latency")
```

### Throughput Optimization

```python
# Test different concurrency levels
concurrency_levels = [1, 2, 5, 10, 20, 50]

for concurrency in concurrency_levels:
    benchmark = PerformanceBenchmark(
        test_prompts=["Write a short story"],
        iterations=100,
        concurrent_requests=concurrency
    )

    results = await benchmark.run()
    print(f"Concurrency {concurrency}: {results.throughput} requests/second")
```

### Resource Optimization

```python
from llm_dispatcher.benchmarks import ResourceBenchmark

# Monitor resource usage during benchmarks
resource_benchmark = ResourceBenchmark(
    test_prompts=["Write a short story"],
    iterations=100,
    concurrent_requests=10,
    monitor_resources=True
)

results = await resource_benchmark.run()

# Analyze resource usage
print(f"Average CPU usage: {results.avg_cpu_usage:.2f}%")
print(f"Peak CPU usage: {results.peak_cpu_usage:.2f}%")
print(f"Average memory usage: {results.avg_memory_usage:.2f} MB")
print(f"Peak memory usage: {results.peak_memory_usage:.2f} MB")
```

## Performance Monitoring

### Real-time Monitoring

```python
from llm_dispatcher.benchmarks import RealtimePerformanceMonitor

# Monitor performance in real-time
monitor = RealtimePerformanceMonitor(
    test_prompts=["Write a short story"],
    duration=300,  # 5 minutes
    check_interval=10  # Check every 10 seconds
)

# Start monitoring
await monitor.start()

# Get real-time metrics
while monitor.is_running():
    metrics = monitor.get_current_metrics()
    print(f"Current latency: {metrics.latency}ms")
    print(f"Current throughput: {metrics.throughput} requests/second")
    print(f"Current error rate: {metrics.error_rate:.2%}")
    await asyncio.sleep(10)

# Stop monitoring
await monitor.stop()
```

### Performance Alerts

```python
# Set up performance alerts
monitor = RealtimePerformanceMonitor(
    test_prompts=["Write a short story"],
    duration=300,
    check_interval=10,
    alerts={
        "latency_threshold": 5000,  # Alert if latency > 5s
        "error_rate_threshold": 0.05,  # Alert if error rate > 5%
        "throughput_threshold": 1  # Alert if throughput < 1 req/s
    }
)

# Start monitoring with alerts
await monitor.start()
```

## Performance Analysis

### Statistical Analysis

```python
from llm_dispatcher.benchmarks.analysis import PerformanceAnalyzer

# Analyze performance results
analyzer = PerformanceAnalyzer(results)

# Statistical analysis
stats = analyzer.get_statistical_analysis()
print(f"Mean latency: {stats.latency.mean:.2f}ms")
print(f"Standard deviation: {stats.latency.std:.2f}ms")
print(f"95th percentile: {stats.latency.p95:.2f}ms")
print(f"99th percentile: {stats.latency.p99:.2f}ms")

# Distribution analysis
distribution = analyzer.get_distribution_analysis()
print(f"Latency distribution: {distribution.latency}")
print(f"Throughput distribution: {distribution.throughput}")
```

### Trend Analysis

```python
# Analyze performance trends
trends = analyzer.get_trend_analysis()
print(f"Latency trend: {trends.latency.direction}")
print(f"Throughput trend: {trends.throughput.direction}")
print(f"Error rate trend: {trends.error_rate.direction}")
```

### Comparative Analysis

```python
# Compare performance across providers
comparison = analyzer.compare_providers()
for provider, metrics in comparison.items():
    print(f"{provider}:")
    print(f"  Latency: {metrics.latency:.2f}ms")
    print(f"  Throughput: {metrics.throughput:.2f} requests/second")
    print(f"  Error rate: {metrics.error_rate:.2%}")
    print(f"  Performance score: {metrics.performance_score:.2f}")
```

## Performance Reports

### Generate Performance Reports

```python
from llm_dispatcher.benchmarks.reports import PerformanceReporter

# Generate performance report
reporter = PerformanceReporter(results)
report = reporter.generate_report("performance_report.html")

# Generate performance charts
charts = reporter.generate_charts("performance_charts.png")
```

### Custom Performance Reports

```python
# Generate custom performance report
custom_report = reporter.generate_custom_report(
    template="custom_performance_template.html",
    output_file="custom_performance_report.html",
    include_charts=True,
    include_raw_data=True,
    include_statistical_analysis=True
)
```

## Best Practices

### 1. **Use Representative Test Data**

```python
# Good: Use diverse, representative test prompts
test_prompts = [
    "Write a short story",  # Creative task
    "Explain quantum computing",  # Technical task
    "Generate Python code",  # Code generation
    "Summarize this text",  # Summarization
    "Translate to Spanish"  # Translation
]

# Avoid: Using only one type of prompt
test_prompts = [
    "Write a story",
    "Write another story",
    "Write a third story"
]
```

### 2. **Test Under Realistic Conditions**

```python
# Good: Test under realistic conditions
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    concurrent_requests=10,  # Realistic concurrency
    timeout=30000  # Realistic timeout
)

# Avoid: Testing under unrealistic conditions
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    concurrent_requests=1000,  # Unrealistic concurrency
    timeout=1000  # Unrealistic timeout
)
```

### 3. **Include Warmup and Cooldown**

```python
# Good: Include warmup and cooldown periods
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    warmup_requests=5,  # Warmup requests
    cooldown_time=2000  # Cooldown period
)

# Avoid: No warmup or cooldown
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    warmup_requests=0,  # No warmup
    cooldown_time=0  # No cooldown
)
```

### 4. **Monitor Resource Usage**

```python
# Good: Monitor resource usage
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    concurrent_requests=10,
    monitor_resources=True  # Monitor resources
)

# Avoid: Not monitoring resources
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=100,
    concurrent_requests=10,
    monitor_resources=False  # No resource monitoring
)
```

### 5. **Analyze Results Thoroughly**

```python
# Good: Analyze results thoroughly
analyzer = PerformanceAnalyzer(results)
stats = analyzer.get_statistical_analysis()
trends = analyzer.get_trend_analysis()
comparison = analyzer.compare_providers()

# Avoid: Only looking at average values
print(f"Average latency: {results.avg_latency}ms")  # Too simplistic
```

## Next Steps

- [:octicons-chart-line-24: Benchmark Overview](overview.md) - Comprehensive benchmarking guide
- [:octicons-dollar-sign-24: Cost Benchmarks](cost.md) - Cost analysis and optimization
- [:octicons-star-24: Quality Benchmarks](quality.md) - Quality assessment and evaluation
- [:octicons-gear-24: Custom Benchmarks](custom.md) - Creating custom benchmark criteria
