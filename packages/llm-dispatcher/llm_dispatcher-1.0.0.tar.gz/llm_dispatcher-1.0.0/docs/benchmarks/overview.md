# Benchmark Overview

LLM-Dispatcher includes comprehensive benchmarking capabilities to help you evaluate and compare different providers, models, and configurations.

## Overview

The benchmarking system provides:

- **Performance metrics** - Latency, throughput, and response times
- **Cost analysis** - Cost per request, cost per token, and total costs
- **Quality assessment** - Response quality and accuracy metrics
- **Comparative analysis** - Side-by-side provider comparisons
- **Custom benchmarks** - Create your own evaluation criteria

## Benchmark Types

### Performance Benchmarks

Measure the speed and efficiency of different providers and models.

```python
from llm_dispatcher.benchmarks import PerformanceBenchmark

benchmark = PerformanceBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=10,
    concurrent_requests=5
)

results = await benchmark.run()
print(f"Average latency: {results.avg_latency}ms")
print(f"Throughput: {results.throughput} requests/second")
```

### Cost Benchmarks

Analyze the cost-effectiveness of different providers and models.

```python
from llm_dispatcher.benchmarks import CostBenchmark

benchmark = CostBenchmark(
    test_prompts=[
        "Write a short story",
        "Explain quantum computing",
        "Generate Python code for sorting"
    ],
    iterations=10
)

results = await benchmark.run()
print(f"Average cost per request: ${results.avg_cost:.4f}")
print(f"Total cost: ${results.total_cost:.4f}")
```

### Quality Benchmarks

Evaluate the quality and accuracy of responses.

```python
from llm_dispatcher.benchmarks import QualityBenchmark

benchmark = QualityBenchmark(
    test_cases=[
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "type": "factual"
        },
        {
            "prompt": "Write a haiku about nature",
            "expected": "5-7-5 syllable structure",
            "type": "creative"
        }
    ],
    iterations=5
)

results = await benchmark.run()
print(f"Accuracy: {results.accuracy:.2%}")
print(f"Quality score: {results.quality_score:.2f}")
```

### Custom Benchmarks

Create your own benchmark criteria and evaluation metrics.

```python
from llm_dispatcher.benchmarks import CustomBenchmark

def custom_evaluator(response: str, expected: str) -> float:
    """Custom evaluation function."""
    # Implement your evaluation logic
    return 0.8  # Return score between 0 and 1

benchmark = CustomBenchmark(
    test_cases=[
        {
            "prompt": "Your test prompt",
            "expected": "Expected response",
            "evaluator": custom_evaluator
        }
    ],
    iterations=10
)

results = await benchmark.run()
print(f"Custom score: {results.custom_score:.2f}")
```

## Running Benchmarks

### Basic Benchmark Execution

```python
from llm_dispatcher.benchmarks import BenchmarkRunner

# Create benchmark runner
runner = BenchmarkRunner()

# Run performance benchmark
performance_results = await runner.run_performance_benchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=["Write a story", "Explain AI", "Generate code"]
)

# Run cost benchmark
cost_results = await runner.run_cost_benchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=["Write a story", "Explain AI", "Generate code"]
)

# Run quality benchmark
quality_results = await runner.run_quality_benchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_cases=[
        {"prompt": "What is 2+2?", "expected": "4", "type": "factual"},
        {"prompt": "Write a poem", "expected": "creative", "type": "creative"}
    ]
)
```

### Comprehensive Benchmark Suite

```python
# Run all benchmarks
comprehensive_results = await runner.run_comprehensive_benchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_prompts=["Write a story", "Explain AI", "Generate code"],
    test_cases=[
        {"prompt": "What is 2+2?", "expected": "4", "type": "factual"},
        {"prompt": "Write a poem", "expected": "creative", "type": "creative"}
    ],
    iterations=10,
    concurrent_requests=5
)
```

## Benchmark Results

### Performance Results

```python
# Access performance metrics
performance = comprehensive_results.performance
print(f"Average latency: {performance.avg_latency}ms")
print(f"Min latency: {performance.min_latency}ms")
print(f"Max latency: {performance.max_latency}ms")
print(f"Throughput: {performance.throughput} requests/second")
print(f"Success rate: {performance.success_rate:.2%}")

# Provider-specific performance
for provider, metrics in performance.provider_metrics.items():
    print(f"{provider}: {metrics.avg_latency}ms avg latency")
```

### Cost Results

```python
# Access cost metrics
cost = comprehensive_results.cost
print(f"Average cost per request: ${cost.avg_cost:.4f}")
print(f"Total cost: ${cost.total_cost:.4f}")
print(f"Cost per token: ${cost.cost_per_token:.6f}")

# Provider-specific costs
for provider, metrics in cost.provider_metrics.items():
    print(f"{provider}: ${metrics.avg_cost:.4f} avg cost")
```

### Quality Results

```python
# Access quality metrics
quality = comprehensive_results.quality
print(f"Overall accuracy: {quality.accuracy:.2%}")
print(f"Quality score: {quality.quality_score:.2f}")
print(f"Factual accuracy: {quality.factual_accuracy:.2%}")
print(f"Creative quality: {quality.creative_quality:.2f}")

# Provider-specific quality
for provider, metrics in quality.provider_metrics.items():
    print(f"{provider}: {metrics.accuracy:.2%} accuracy")
```

## Benchmark Configuration

### Custom Test Prompts

```python
# Define custom test prompts
custom_prompts = [
    "Write a short story about a robot learning to paint",
    "Explain the concept of machine learning in simple terms",
    "Generate Python code to implement a binary search algorithm",
    "Create a marketing slogan for a new AI product",
    "Summarize the key points of quantum computing"
]

benchmark = PerformanceBenchmark(
    test_prompts=custom_prompts,
    iterations=5,
    concurrent_requests=3
)
```

### Custom Test Cases

```python
# Define custom test cases
custom_test_cases = [
    {
        "prompt": "What is the capital of Japan?",
        "expected": "Tokyo",
        "type": "factual",
        "weight": 1.0
    },
    {
        "prompt": "Write a haiku about spring",
        "expected": "5-7-5 syllable structure",
        "type": "creative",
        "weight": 0.8
    },
    {
        "prompt": "Solve: 15 * 23 = ?",
        "expected": "345",
        "type": "mathematical",
        "weight": 1.0
    }
]

benchmark = QualityBenchmark(
    test_cases=custom_test_cases,
    iterations=5
)
```

### Benchmark Parameters

```python
# Configure benchmark parameters
benchmark_config = {
    "iterations": 10,
    "concurrent_requests": 5,
    "timeout": 30000,
    "max_retries": 3,
    "warmup_requests": 2,
    "cooldown_time": 1000
}

benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    **benchmark_config
)
```

## Benchmark Analysis

### Statistical Analysis

```python
from llm_dispatcher.benchmarks.analysis import BenchmarkAnalyzer

analyzer = BenchmarkAnalyzer(comprehensive_results)

# Statistical analysis
stats = analyzer.get_statistical_analysis()
print(f"Mean latency: {stats.latency.mean:.2f}ms")
print(f"Standard deviation: {stats.latency.std:.2f}ms")
print(f"95th percentile: {stats.latency.p95:.2f}ms")
print(f"99th percentile: {stats.latency.p99:.2f}ms")
```

### Comparative Analysis

```python
# Compare providers
comparison = analyzer.compare_providers()
print("Provider Comparison:")
for provider, metrics in comparison.items():
    print(f"{provider}:")
    print(f"  Latency: {metrics.latency:.2f}ms")
    print(f"  Cost: ${metrics.cost:.4f}")
    print(f"  Quality: {metrics.quality:.2f}")
    print(f"  Overall Score: {metrics.overall_score:.2f}")
```

### Trend Analysis

```python
# Analyze trends over time
trends = analyzer.get_trend_analysis()
print("Performance Trends:")
for provider, trend in trends.items():
    print(f"{provider}: {trend.direction} ({trend.percentage:.1f}% change)")
```

## Benchmark Reports

### Generate Reports

```python
from llm_dispatcher.benchmarks.reports import BenchmarkReporter

reporter = BenchmarkReporter(comprehensive_results)

# Generate HTML report
html_report = reporter.generate_html_report("benchmark_report.html")

# Generate JSON report
json_report = reporter.generate_json_report("benchmark_results.json")

# Generate CSV report
csv_report = reporter.generate_csv_report("benchmark_data.csv")
```

### Custom Report Formats

```python
# Generate custom report
custom_report = reporter.generate_custom_report(
    template="custom_template.html",
    output_file="custom_report.html",
    include_charts=True,
    include_raw_data=True
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

### 2. **Run Multiple Iterations**

```python
# Good: Run multiple iterations for statistical significance
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=10,  # Multiple iterations
    concurrent_requests=5
)

# Avoid: Running only one iteration
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=1,  # Not statistically significant
    concurrent_requests=1
)
```

### 3. **Include Warmup and Cooldown**

```python
# Good: Include warmup and cooldown periods
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=10,
    warmup_requests=2,  # Warmup requests
    cooldown_time=1000  # Cooldown period
)

# Avoid: No warmup or cooldown
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=10,
    warmup_requests=0,  # No warmup
    cooldown_time=0  # No cooldown
)
```

### 4. **Test Under Realistic Conditions**

```python
# Good: Test under realistic conditions
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=10,
    concurrent_requests=5,  # Realistic concurrency
    timeout=30000  # Realistic timeout
)

# Avoid: Testing under unrealistic conditions
benchmark = PerformanceBenchmark(
    test_prompts=test_prompts,
    iterations=10,
    concurrent_requests=100,  # Unrealistic concurrency
    timeout=1000  # Unrealistic timeout
)
```

### 5. **Analyze Results Thoroughly**

```python
# Good: Analyze results thoroughly
analyzer = BenchmarkAnalyzer(results)
stats = analyzer.get_statistical_analysis()
comparison = analyzer.compare_providers()
trends = analyzer.get_trend_analysis()

# Avoid: Only looking at average values
print(f"Average latency: {results.avg_latency}ms")  # Too simplistic
```

## Next Steps

- [:octicons-chart-line-24: Performance Benchmarks](performance.md) - Detailed performance testing
- [:octicons-dollar-sign-24: Cost Benchmarks](cost.md) - Cost analysis and optimization
- [:octicons-star-24: Quality Benchmarks](quality.md) - Quality assessment and evaluation
- [:octicons-gear-24: Custom Benchmarks](custom.md) - Creating custom benchmark criteria
