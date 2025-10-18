# Quality Benchmarks

Quality benchmarks evaluate the accuracy, relevance, and overall quality of responses from different LLM providers and models.

## Overview

Quality benchmarks assess:

- **Accuracy** - Correctness of factual information
- **Relevance** - How well responses address the prompt
- **Coherence** - Logical flow and structure of responses
- **Creativity** - Originality and innovation in responses
- **Completeness** - Thoroughness of responses
- **Consistency** - Reliability across multiple requests

## Basic Quality Benchmarking

### Simple Quality Test

```python
from llm_dispatcher.benchmarks import QualityBenchmark

# Create quality benchmark
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
        },
        {
            "prompt": "Explain photosynthesis",
            "expected": "Process by which plants convert light to energy",
            "type": "explanatory"
        }
    ],
    iterations=5
)

# Run benchmark
results = await benchmark.run()

# Analyze results
print(f"Overall accuracy: {results.accuracy:.2%}")
print(f"Factual accuracy: {results.factual_accuracy:.2%}")
print(f"Creative quality: {results.creative_quality:.2f}")
print(f"Average quality score: {results.avg_quality_score:.2f}")
```

### Provider Quality Comparison

```python
# Compare quality across providers
benchmark = QualityBenchmark(
    providers=["openai", "anthropic", "google"],
    models=["gpt-4", "claude-3-sonnet", "gemini-2.5-pro"],
    test_cases=[
        {
            "prompt": "What is the capital of Japan?",
            "expected": "Tokyo",
            "type": "factual"
        },
        {
            "prompt": "Write a short story about a robot",
            "expected": "creative narrative",
            "type": "creative"
        },
        {
            "prompt": "Explain quantum computing",
            "expected": "technical explanation",
            "type": "explanatory"
        }
    ],
    iterations=10
)

results = await benchmark.run()

# Compare provider quality
for provider, metrics in results.provider_metrics.items():
    print(f"{provider}:")
    print(f"  Overall accuracy: {metrics.accuracy:.2%}")
    print(f"  Quality score: {metrics.quality_score:.2f}")
    print(f"  Factual accuracy: {metrics.factual_accuracy:.2%}")
    print(f"  Creative quality: {metrics.creative_quality:.2f}")
```

## Advanced Quality Testing

### Multi-Dimensional Quality Assessment

```python
from llm_dispatcher.benchmarks import MultiDimensionalQualityBenchmark

# Create multi-dimensional quality benchmark
benchmark = MultiDimensionalQualityBenchmark(
    test_cases=[
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "type": "factual",
            "dimensions": ["accuracy", "precision", "completeness"]
        },
        {
            "prompt": "Write a haiku about spring",
            "expected": "5-7-5 syllable structure",
            "type": "creative",
            "dimensions": ["creativity", "structure", "aesthetics"]
        },
        {
            "prompt": "Explain machine learning",
            "expected": "technical explanation",
            "type": "explanatory",
            "dimensions": ["accuracy", "clarity", "completeness"]
        }
    ],
    iterations=10
)

results = await benchmark.run()

# Analyze multi-dimensional quality
for dimension, score in results.dimension_scores.items():
    print(f"{dimension}: {score:.2f}")
```

### Task-Specific Quality Testing

```python
from llm_dispatcher.benchmarks import TaskSpecificQualityBenchmark

# Create task-specific quality benchmark
benchmark = TaskSpecificQualityBenchmark(
    task_types=["factual", "creative", "explanatory", "analytical"],
    test_cases={
        "factual": [
            {
                "prompt": "What is the population of Tokyo?",
                "expected": "Approximately 14 million",
                "type": "factual"
            }
        ],
        "creative": [
            {
                "prompt": "Write a poem about the ocean",
                "expected": "creative poetry",
                "type": "creative"
            }
        ],
        "explanatory": [
            {
                "prompt": "Explain how a computer works",
                "expected": "technical explanation",
                "type": "explanatory"
            }
        ],
        "analytical": [
            {
                "prompt": "Analyze the pros and cons of renewable energy",
                "expected": "balanced analysis",
                "type": "analytical"
            }
        ]
    },
    iterations=10
)

results = await benchmark.run()

# Analyze task-specific quality
for task_type, metrics in results.task_metrics.items():
    print(f"{task_type}:")
    print(f"  Quality score: {metrics.quality_score:.2f}")
    print(f"  Accuracy: {metrics.accuracy:.2%}")
    print(f"  Relevance: {metrics.relevance:.2f}")
```

### Consistency Testing

```python
from llm_dispatcher.benchmarks import ConsistencyBenchmark

# Create consistency benchmark
benchmark = ConsistencyBenchmark(
    test_prompts=[
        "What is the capital of France?",
        "Write a haiku about nature",
        "Explain photosynthesis"
    ],
    iterations=10  # Test same prompt multiple times
)

results = await benchmark.run()

# Analyze consistency
print(f"Overall consistency: {results.consistency_score:.2f}")
print(f"Factual consistency: {results.factual_consistency:.2f}")
print(f"Creative consistency: {results.creative_consistency:.2f}")
print(f"Response variance: {results.response_variance:.2f}")
```

## Quality Metrics

### Detailed Quality Analysis

```python
# Detailed quality metrics
quality_metrics = results.get_quality_metrics()
print(f"Overall accuracy: {quality_metrics.accuracy:.2%}")
print(f"Factual accuracy: {quality_metrics.factual_accuracy:.2%}")
print(f"Creative quality: {quality_metrics.creative_quality:.2f}")
print(f"Explanatory quality: {quality_metrics.explanatory_quality:.2f}")
print(f"Analytical quality: {quality_metrics.analytical_quality:.2f}")
print(f"Average quality score: {quality_metrics.avg_quality_score:.2f}")
print(f"Quality variance: {quality_metrics.quality_variance:.2f}")
```

### Response Analysis

```python
# Response analysis
response_metrics = results.get_response_metrics()
print(f"Average response length: {response_metrics.avg_length} characters")
print(f"Response completeness: {response_metrics.completeness:.2f}")
print(f"Response coherence: {response_metrics.coherence:.2f}")
print(f"Response relevance: {response_metrics.relevance:.2f}")
print(f"Response originality: {response_metrics.originality:.2f}")
```

### Error Analysis

```python
# Error analysis
error_metrics = results.get_error_metrics()
print(f"Total errors: {error_metrics.total_errors}")
print(f"Factual errors: {error_metrics.factual_errors}")
print(f"Logical errors: {error_metrics.logical_errors}")
print(f"Format errors: {error_metrics.format_errors}")
print(f"Error rate: {error_metrics.error_rate:.2%}")
```

## Quality Evaluation Methods

### Automated Evaluation

```python
from llm_dispatcher.benchmarks.evaluation import AutomatedEvaluator

# Create automated evaluator
evaluator = AutomatedEvaluator(
    evaluation_metrics=["accuracy", "relevance", "coherence", "completeness"]
)

# Evaluate responses
evaluation_results = evaluator.evaluate(
    prompts=["What is the capital of France?"],
    responses=["Paris is the capital of France."],
    expected=["Paris"]
)

print(f"Accuracy: {evaluation_results.accuracy:.2f}")
print(f"Relevance: {evaluation_results.relevance:.2f}")
print(f"Coherence: {evaluation_results.coherence:.2f}")
print(f"Completeness: {evaluation_results.completeness:.2f}")
```

### Human Evaluation

```python
from llm_dispatcher.benchmarks.evaluation import HumanEvaluator

# Create human evaluator
evaluator = HumanEvaluator(
    evaluators=["expert1", "expert2", "expert3"],
    evaluation_criteria=["accuracy", "relevance", "coherence", "creativity"]
)

# Evaluate responses
evaluation_results = evaluator.evaluate(
    prompts=["Write a story about a robot"],
    responses=["Once upon a time, there was a robot..."],
    expected=["creative narrative"]
)

print(f"Inter-rater reliability: {evaluation_results.inter_rater_reliability:.2f}")
print(f"Average human score: {evaluation_results.avg_human_score:.2f}")
```

### Hybrid Evaluation

```python
from llm_dispatcher.benchmarks.evaluation import HybridEvaluator

# Create hybrid evaluator
evaluator = HybridEvaluator(
    automated_metrics=["accuracy", "relevance"],
    human_metrics=["creativity", "aesthetics"],
    weight_automated=0.7,
    weight_human=0.3
)

# Evaluate responses
evaluation_results = evaluator.evaluate(
    prompts=["Write a poem about spring"],
    responses=["Spring brings new life..."],
    expected=["creative poetry"]
)

print(f"Hybrid score: {evaluation_results.hybrid_score:.2f}")
print(f"Automated score: {evaluation_results.automated_score:.2f}")
print(f"Human score: {evaluation_results.human_score:.2f}")
```

## Quality Optimization

### Model Selection for Quality

```python
# Test different models for quality
models = ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku", "gemini-2.5-pro", "gemini-2.5-flash"]

for model in models:
    benchmark = QualityBenchmark(
        providers=["openai" if "gpt" in model else "anthropic" if "claude" in model else "google"],
        models=[model],
        test_cases=[
            {
                "prompt": "What is the capital of France?",
                "expected": "Paris",
                "type": "factual"
            }
        ],
        iterations=10
    )

    results = await benchmark.run()
    print(f"{model}: {results.accuracy:.2%} accuracy")
```

### Parameter Optimization for Quality

```python
# Test different parameters for quality
temperatures = [0.1, 0.3, 0.5, 0.7, 0.9]

for temp in temperatures:
    benchmark = QualityBenchmark(
        test_cases=[
            {
                "prompt": "Write a creative story",
                "expected": "creative narrative",
                "type": "creative"
            }
        ],
        iterations=10,
        temperature=temp
    )

    results = await benchmark.run()
    print(f"Temperature {temp}: {results.creative_quality:.2f} creative quality")
```

### Prompt Engineering for Quality

```python
# Test different prompt engineering techniques
prompt_variations = [
    "What is the capital of France?",
    "Please tell me the capital city of France.",
    "I need to know the capital of France for my geography homework.",
    "Can you help me identify the capital city of France?"
]

for prompt in prompt_variations:
    benchmark = QualityBenchmark(
        test_cases=[
            {
                "prompt": prompt,
                "expected": "Paris",
                "type": "factual"
            }
        ],
        iterations=10
    )

    results = await benchmark.run()
    print(f"Prompt: {prompt[:30]}... - Accuracy: {results.accuracy:.2%}")
```

## Quality Monitoring

### Real-time Quality Monitoring

```python
from llm_dispatcher.benchmarks import RealtimeQualityMonitor

# Monitor quality in real-time
monitor = RealtimeQualityMonitor(
    test_cases=[
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "type": "factual"
        }
    ],
    duration=300,  # 5 minutes
    check_interval=10  # Check every 10 seconds
)

# Start monitoring
await monitor.start()

# Get real-time quality metrics
while monitor.is_running():
    metrics = monitor.get_current_metrics()
    print(f"Current accuracy: {metrics.accuracy:.2%}")
    print(f"Quality trend: {metrics.quality_trend}")
    print(f"Error rate: {metrics.error_rate:.2%}")
    await asyncio.sleep(10)

# Stop monitoring
await monitor.stop()
```

### Quality Alerts

```python
# Set up quality alerts
monitor = RealtimeQualityMonitor(
    test_cases=[
        {
            "prompt": "What is the capital of France?",
            "expected": "Paris",
            "type": "factual"
        }
    ],
    duration=300,
    check_interval=10,
    alerts={
        "accuracy_threshold": 0.95,  # Alert if accuracy < 95%
        "error_rate_threshold": 0.05,  # Alert if error rate > 5%
        "quality_degradation_threshold": 0.1  # Alert if quality drops > 10%
    }
)

# Start monitoring with alerts
await monitor.start()
```

## Quality Analysis

### Statistical Analysis

```python
from llm_dispatcher.benchmarks.analysis import QualityAnalyzer

# Analyze quality results
analyzer = QualityAnalyzer(results)

# Statistical analysis
stats = analyzer.get_statistical_analysis()
print(f"Mean quality score: {stats.quality.mean:.2f}")
print(f"Standard deviation: {stats.quality.std:.2f}")
print(f"95th percentile: {stats.quality.p95:.2f}")
print(f"99th percentile: {stats.quality.p99:.2f}")

# Distribution analysis
distribution = analyzer.get_distribution_analysis()
print(f"Quality distribution: {distribution.quality}")
print(f"Accuracy distribution: {distribution.accuracy}")
```

### Trend Analysis

```python
# Analyze quality trends
trends = analyzer.get_trend_analysis()
print(f"Quality trend: {trends.quality.direction}")
print(f"Accuracy trend: {trends.accuracy.direction}")
print(f"Error rate trend: {trends.error_rate.direction}")
```

### Comparative Analysis

```python
# Compare quality across providers
comparison = analyzer.compare_providers()
for provider, metrics in comparison.items():
    print(f"{provider}:")
    print(f"  Quality score: {metrics.quality_score:.2f}")
    print(f"  Accuracy: {metrics.accuracy:.2%}")
    print(f"  Creative quality: {metrics.creative_quality:.2f}")
    print(f"  Overall score: {metrics.overall_score:.2f}")
```

## Quality Reports

### Generate Quality Reports

```python
from llm_dispatcher.benchmarks.reports import QualityReporter

# Generate quality report
reporter = QualityReporter(results)
report = reporter.generate_report("quality_report.html")

# Generate quality charts
charts = reporter.generate_charts("quality_charts.png")
```

### Custom Quality Reports

```python
# Generate custom quality report
custom_report = reporter.generate_custom_report(
    template="custom_quality_template.html",
    output_file="custom_quality_report.html",
    include_charts=True,
    include_raw_data=True,
    include_statistical_analysis=True
)
```

## Best Practices

### 1. **Use Diverse Test Cases**

```python
# Good: Use diverse test cases
test_cases = [
    {"prompt": "What is 2+2?", "expected": "4", "type": "factual"},
    {"prompt": "Write a haiku", "expected": "5-7-5 structure", "type": "creative"},
    {"prompt": "Explain AI", "expected": "technical explanation", "type": "explanatory"},
    {"prompt": "Analyze climate change", "expected": "balanced analysis", "type": "analytical"}
]

# Avoid: Using only one type of test case
test_cases = [
    {"prompt": "What is 2+2?", "expected": "4", "type": "factual"},
    {"prompt": "What is 3+3?", "expected": "6", "type": "factual"},
    {"prompt": "What is 4+4?", "expected": "8", "type": "factual"}
]
```

### 2. **Use Multiple Evaluation Methods**

```python
# Good: Use multiple evaluation methods
evaluator = HybridEvaluator(
    automated_metrics=["accuracy", "relevance"],
    human_metrics=["creativity", "aesthetics"],
    weight_automated=0.7,
    weight_human=0.3
)

# Avoid: Using only one evaluation method
evaluator = AutomatedEvaluator(["accuracy"])
```

### 3. **Test Consistency**

```python
# Good: Test consistency across multiple iterations
benchmark = ConsistencyBenchmark(
    test_prompts=["What is the capital of France?"],
    iterations=10  # Multiple iterations
)

# Avoid: Testing only once
benchmark = QualityBenchmark(
    test_cases=[{"prompt": "What is the capital of France?", "expected": "Paris", "type": "factual"}],
    iterations=1  # Only one iteration
)
```

### 4. **Monitor Quality Continuously**

```python
# Good: Monitor quality continuously
monitor = RealtimeQualityMonitor(
    test_cases=[{"prompt": "What is the capital of France?", "expected": "Paris", "type": "factual"}],
    duration=300,
    check_interval=10,
    alerts={"accuracy_threshold": 0.95}
)

# Avoid: No quality monitoring
# No monitoring setup
```

### 5. **Analyze Quality Trends**

```python
# Good: Analyze quality trends
analyzer = QualityAnalyzer(results)
trends = analyzer.get_trend_analysis()
comparison = analyzer.compare_providers()

# Avoid: Only looking at average values
print(f"Average quality: {results.avg_quality_score:.2f}")  # Too simplistic
```

## Next Steps

- [:octicons-chart-line-24: Benchmark Overview](overview.md) - Comprehensive benchmarking guide
- [:octicons-chart-line-24: Performance Benchmarks](performance.md) - Performance testing and optimization
- [:octicons-dollar-sign-24: Cost Benchmarks](cost.md) - Cost analysis and optimization
- [:octicons-gear-24: Custom Benchmarks](custom.md) - Creating custom benchmark criteria
