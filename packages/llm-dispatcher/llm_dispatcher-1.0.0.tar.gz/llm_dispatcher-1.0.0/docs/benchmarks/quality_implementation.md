# Quality Benchmarks Implementation Guide

This guide explains how to implement and use the quality benchmarks described in the documentation using RAGAS and other evaluation libraries.

## Overview

The quality benchmarking system provides comprehensive evaluation of LLM responses across multiple dimensions:

- **Accuracy** - Correctness of factual information
- **Relevance** - How well responses address the prompt
- **Coherence** - Logical flow and structure of responses
- **Creativity** - Originality and innovation in responses
- **Completeness** - Thoroughness of responses
- **Consistency** - Reliability across multiple requests

## Installation

First, install the required dependencies:

```bash
# Core quality evaluation dependencies
pip install ragas>=0.1.0
pip install langchain>=0.1.0
pip install langchain-openai>=0.1.0
pip install langchain-anthropic>=0.1.0
pip install langchain-google-genai>=0.1.0

# Additional evaluation libraries
pip install sentence-transformers>=2.2.0
pip install scikit-learn>=1.3.0

# Visualization and reporting
pip install matplotlib>=3.7.0
pip install seaborn>=0.12.0
pip install plotly>=5.15.0
```

## Basic Usage

### 1. Simple Quality Benchmark

```python
import asyncio
from llm_dispatcher.benchmarks import QualityBenchmark
from llm_dispatcher.benchmarks.quality_benchmark import TestCase

async def basic_quality_test():
    # Define test cases
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris", "The capital of France is Paris"]
        ),
        TestCase(
            prompt="Write a haiku about nature",
            expected="5-7-5 syllable structure",
            type="creative",
            ground_truths=["A haiku with 5-7-5 syllable structure about nature"]
        )
    ]
    
    # Create and run benchmark
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=["openai", "anthropic"],
        models=["gpt-4", "claude-3-sonnet"],
        iterations=5,
        use_ragas=True  # Enable RAGAS evaluation
    )
    
    results = await benchmark.run()
    
    # Print results
    print(f"Overall accuracy: {results.overall_accuracy:.2%}")
    print(f"Factual accuracy: {results.factual_accuracy:.2%}")
    print(f"Creative quality: {results.creative_quality:.2f}")
    print(f"Average quality score: {results.avg_quality_score:.2f}")

# Run the benchmark
asyncio.run(basic_quality_test())
```

### 2. Multi-Dimensional Quality Assessment

```python
from llm_dispatcher.benchmarks import MultiDimensionalQualityBenchmark

async def multi_dimensional_test():
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            dimensions=["accuracy", "precision", "completeness"],
            ground_truths=["Paris"]
        ),
        TestCase(
            prompt="Write a haiku about spring",
            expected="5-7-5 syllable structure",
            type="creative",
            dimensions=["creativity", "structure", "aesthetics"],
            ground_truths=["A haiku with 5-7-5 syllable structure about spring"]
        )
    ]
    
    benchmark = MultiDimensionalQualityBenchmark(
        test_cases=test_cases,
        providers=["openai"],
        iterations=3,
        dimensions=["accuracy", "relevance", "coherence", "completeness", "creativity"]
    )
    
    results = await benchmark.run()
    
    # Print dimension scores
    for dimension, score in results.dimension_scores.items():
        print(f"{dimension}: {score:.2f}")

asyncio.run(multi_dimensional_test())
```

### 3. Task-Specific Quality Testing

```python
from llm_dispatcher.benchmarks import TaskSpecificQualityBenchmark

async def task_specific_test():
    test_cases = {
        "factual": [
            TestCase(
                prompt="What is the population of Tokyo?",
                expected="Approximately 14 million",
                type="factual",
                ground_truths=["About 14 million people", "14 million inhabitants"]
            )
        ],
        "creative": [
            TestCase(
                prompt="Write a poem about the ocean",
                expected="creative poetry",
                type="creative",
                ground_truths=["A creative poem about the ocean"]
            )
        ],
        "explanatory": [
            TestCase(
                prompt="Explain how a computer works",
                expected="technical explanation",
                type="explanatory",
                ground_truths=["A technical explanation of computer operation"]
            )
        ]
    }
    
    benchmark = TaskSpecificQualityBenchmark(
        task_types=["factual", "creative", "explanatory"],
        test_cases=test_cases,
        providers=["openai"],
        iterations=3
    )
    
    results = await benchmark.run()
    
    # Print task-specific metrics
    for task_type, metrics in results.task_metrics.items():
        print(f"{task_type}:")
        print(f"  Quality score: {metrics.quality_score:.2f}")
        print(f"  Accuracy: {metrics.accuracy:.2%}")

asyncio.run(task_specific_test())
```

## Evaluation Methods

### 1. Automated Evaluation with RAGAS

```python
from llm_dispatcher.benchmarks import AutomatedEvaluator

async def automated_evaluation():
    evaluator = AutomatedEvaluator(
        evaluation_metrics=["accuracy", "relevance", "coherence", "completeness"],
        evaluator_llm="gpt-4o",
        use_ragas=True,
        use_semantic_similarity=True
    )
    
    prompts = ["What is the capital of France?", "Write a haiku about spring"]
    responses = ["Paris is the capital of France.", "Spring brings new life..."]
    expected = ["Paris", "5-7-5 syllable structure"]
    
    result = await evaluator.evaluate(prompts, responses, expected)
    
    print(f"Accuracy: {result.accuracy:.2f}")
    print(f"Relevance: {result.relevance:.2f}")
    print(f"Coherence: {result.coherence:.2f}")
    print(f"Completeness: {result.completeness:.2f}")
    print(f"Overall score: {result.overall_score:.2f}")

asyncio.run(automated_evaluation())
```

### 2. Human Evaluation

```python
from llm_dispatcher.benchmarks import HumanEvaluator

async def human_evaluation():
    evaluator = HumanEvaluator(
        evaluators=["expert1", "expert2", "expert3"],
        evaluation_criteria=["accuracy", "relevance", "coherence", "creativity"],
        rating_scale=5
    )
    
    prompts = ["Write a story about a robot"]
    responses = ["Once upon a time, there was a robot..."]
    expected = ["creative narrative"]
    
    result = await evaluator.evaluate(prompts, responses, expected)
    
    print(f"Inter-rater reliability: {result.inter_rater_reliability:.2f}")
    print(f"Average human score: {result.avg_human_score:.2f}")
    print(f"Accuracy: {result.accuracy:.2f}")
    print(f"Creativity: {result.creativity:.2f}")

asyncio.run(human_evaluation())
```

### 3. Hybrid Evaluation

```python
from llm_dispatcher.benchmarks import HybridEvaluator

async def hybrid_evaluation():
    evaluator = HybridEvaluator(
        automated_metrics=["accuracy", "relevance"],
        human_metrics=["creativity", "aesthetics"],
        weight_automated=0.7,
        weight_human=0.3,
        evaluators=["expert1", "expert2"]
    )
    
    prompts = ["Write a poem about spring"]
    responses = ["Spring brings new life..."]
    expected = ["creative poetry"]
    
    result = await evaluator.evaluate(prompts, responses, expected)
    
    print(f"Hybrid score: {result.hybrid_score:.2f}")
    print(f"Automated score: {result.automated_score:.2f}")
    print(f"Human score: {result.human_score:.2f}")
    print(f"Overall score: {result.overall_score:.2f}")

asyncio.run(hybrid_evaluation())
```

## Consistency Testing

```python
from llm_dispatcher.benchmarks import ConsistencyBenchmark

async def consistency_test():
    test_prompts = [
        "What is the capital of France?",
        "Write a haiku about nature",
        "Explain photosynthesis"
    ]
    
    benchmark = ConsistencyBenchmark(
        test_prompts=test_prompts,
        providers=["openai"],
        iterations=10  # Test same prompt multiple times
    )
    
    results = await benchmark.run()
    
    print(f"Overall consistency: {results.consistency_score:.2f}")
    print(f"Factual consistency: {results.factual_consistency:.2f}")
    print(f"Creative consistency: {results.creative_consistency:.2f}")
    print(f"Response variance: {results.response_variance:.2f}")

asyncio.run(consistency_test())
```

## Real-time Quality Monitoring

```python
from llm_dispatcher.benchmarks import RealtimeQualityMonitor

async def realtime_monitoring():
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris"]
        )
    ]
    
    monitor = RealtimeQualityMonitor(
        test_cases=test_cases,
        duration=300,  # 5 minutes
        check_interval=10,  # Check every 10 seconds
        alerts={
            "accuracy_threshold": 0.95,  # Alert if accuracy < 95%
            "error_rate_threshold": 0.05,  # Alert if error rate > 5%
            "quality_degradation_threshold": 0.1  # Alert if quality drops > 10%
        }
    )
    
    # Start monitoring
    await monitor.start()
    
    # Get real-time quality metrics
    while monitor.is_running():
        metrics = monitor.get_current_metrics()
        print(f"Current accuracy: {metrics['accuracy']:.2%}")
        print(f"Quality trend: {metrics['quality_trend']}")
        print(f"Error rate: {metrics['error_rate']:.2%}")
        await asyncio.sleep(10)
    
    # Stop monitoring
    await monitor.stop()

asyncio.run(realtime_monitoring())
```

## Analysis and Reporting

### 1. Statistical Analysis

```python
from llm_dispatcher.benchmarks import QualityAnalyzer

# After running a benchmark
analyzer = QualityAnalyzer(results)

# Statistical analysis
stats = analyzer.get_statistical_analysis()
for metric, analysis in stats.items():
    print(f"{metric}:")
    print(f"  Mean: {analysis.mean:.3f}")
    print(f"  Standard deviation: {analysis.std:.3f}")
    print(f"  95th percentile: {analysis.p95:.3f}")

# Distribution analysis
distribution = analyzer.get_distribution_analysis()
print(f"Quality distribution: {distribution.quality}")
print(f"Accuracy distribution: {distribution.accuracy}")

# Trend analysis
trends = analyzer.get_trend_analysis()
print(f"Quality trend: {trends.quality.direction}")
print(f"Accuracy trend: {trends.accuracy.direction}")

# Provider comparison
comparison = analyzer.compare_providers()
for provider, metrics in comparison.items():
    print(f"{provider}: Quality={metrics.quality_score:.2f}, Accuracy={metrics.accuracy:.2%}")
```

### 2. Generate Reports

```python
from llm_dispatcher.benchmarks import QualityReporter

# Generate comprehensive HTML report
reporter = QualityReporter(results)
report_file = reporter.generate_report("quality_report.html")
print(f"HTML report generated: {report_file}")

# Generate charts
try:
    chart_file = reporter.generate_charts("quality_charts.png")
    print(f"Charts generated: {chart_file}")
except ImportError:
    print("Matplotlib not available, skipping chart generation")

# Generate interactive charts
try:
    interactive_file = reporter.generate_interactive_charts("quality_interactive.html")
    print(f"Interactive charts generated: {interactive_file}")
except ImportError:
    print("Plotly not available, skipping interactive chart generation")
```

## RAGAS Integration Details

The quality benchmarks use RAGAS (RAG Assessment) for comprehensive evaluation. RAGAS provides several metrics:

### Available RAGAS Metrics

- **ResponseRelevancy** - How relevant is the response to the question
- **AnswerCorrectness** - How correct is the answer compared to ground truth
- **AnswerRelevancy** - How relevant is the answer to the question
- **AnswerSimilarity** - Semantic similarity between answer and ground truth
- **ResponseCompleteness** - How complete is the response
- **ResponseConsistency** - How consistent is the response
- **ResponseConciseness** - How concise is the response

### RAGAS Configuration

```python
# The system automatically configures RAGAS with:
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o", temperature=0))
run_config = RunConfig(
    timeout=300,          # 5 minutes max for operations
    max_concurrent=5,     # Limit concurrent API calls
    max_retries=3         # Retry up to 3 times on failure
)
```

## Best Practices

### 1. Use Diverse Test Cases

```python
# Good: Use diverse test cases
test_cases = [
    TestCase(prompt="What is 2+2?", expected="4", type="factual"),
    TestCase(prompt="Write a haiku", expected="5-7-5 structure", type="creative"),
    TestCase(prompt="Explain AI", expected="technical explanation", type="explanatory"),
    TestCase(prompt="Analyze climate change", expected="balanced analysis", type="analytical")
]

# Avoid: Using only one type of test case
test_cases = [
    TestCase(prompt="What is 2+2?", expected="4", type="factual"),
    TestCase(prompt="What is 3+3?", expected="6", type="factual"),
    TestCase(prompt="What is 4+4?", expected="8", type="factual")
]
```

### 2. Use Multiple Evaluation Methods

```python
# Good: Use hybrid evaluation
evaluator = HybridEvaluator(
    automated_metrics=["accuracy", "relevance"],
    human_metrics=["creativity", "aesthetics"],
    weight_automated=0.7,
    weight_human=0.3
)

# Avoid: Using only one evaluation method
evaluator = AutomatedEvaluator(["accuracy"])
```

### 3. Test Consistency

```python
# Good: Test consistency across multiple iterations
benchmark = ConsistencyBenchmark(
    test_prompts=["What is the capital of France?"],
    iterations=10  # Multiple iterations
)

# Avoid: Testing only once
benchmark = QualityBenchmark(
    test_cases=[TestCase(prompt="What is the capital of France?", expected="Paris", type="factual")],
    iterations=1  # Only one iteration
)
```

### 4. Monitor Quality Continuously

```python
# Good: Monitor quality continuously
monitor = RealtimeQualityMonitor(
    test_cases=[TestCase(prompt="What is the capital of France?", expected="Paris", type="factual")],
    duration=300,
    check_interval=10,
    alerts={"accuracy_threshold": 0.95}
)

# Avoid: No quality monitoring
# No monitoring setup
```

### 5. Analyze Quality Trends

```python
# Good: Analyze quality trends
analyzer = QualityAnalyzer(results)
trends = analyzer.get_trend_analysis()
comparison = analyzer.compare_providers()

# Avoid: Only looking at average values
print(f"Average quality: {results.avg_quality_score:.2f}")  # Too simplistic
```

## Environment Setup

Set up your API keys for the evaluation:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

Or set them in your Python code:

```python
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"
os.environ["GOOGLE_API_KEY"] = "your-google-api-key"
```

## Troubleshooting

### Common Issues

1. **RAGAS Import Error**
   ```bash
   pip install ragas>=0.1.0
   ```

2. **LangChain Import Error**
   ```bash
   pip install langchain>=0.1.0 langchain-openai>=0.1.0
   ```

3. **Sentence Transformers Error**
   ```bash
   pip install sentence-transformers>=2.2.0
   ```

4. **API Key Issues**
   - Ensure your API keys are set correctly
   - Check that you have sufficient API credits
   - Verify the API keys have the necessary permissions

### Performance Optimization

1. **Batch Processing**: For large datasets, process evaluations in batches
2. **Rate Limiting**: Use appropriate delays between API calls
3. **Caching**: Cache evaluation results to avoid redundant computations
4. **Parallel Processing**: Use async/await for concurrent evaluations

## Example Complete Workflow

```python
import asyncio
from llm_dispatcher.benchmarks import (
    QualityBenchmark, 
    QualityAnalyzer, 
    QualityReporter
)
from llm_dispatcher.benchmarks.quality_benchmark import TestCase

async def complete_quality_workflow():
    # 1. Define test cases
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris", "The capital of France is Paris"]
        ),
        TestCase(
            prompt="Write a haiku about nature",
            expected="5-7-5 syllable structure",
            type="creative",
            ground_truths=["A haiku with 5-7-5 syllable structure about nature"]
        )
    ]
    
    # 2. Run quality benchmark
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=["openai"],
        iterations=3,
        use_ragas=True
    )
    
    results = await benchmark.run()
    
    # 3. Analyze results
    analyzer = QualityAnalyzer(results)
    stats = analyzer.get_statistical_analysis()
    trends = analyzer.get_trend_analysis()
    
    # 4. Generate reports
    reporter = QualityReporter(results)
    report_file = reporter.generate_report("quality_report.html")
    
    # 5. Print summary
    print(f"Quality benchmark completed!")
    print(f"Overall accuracy: {results.overall_accuracy:.2%}")
    print(f"Average quality score: {results.avg_quality_score:.2f}")
    print(f"Report generated: {report_file}")

# Run the complete workflow
asyncio.run(complete_quality_workflow())
```

This implementation provides a comprehensive quality benchmarking system that integrates RAGAS and other evaluation libraries to assess LLM response quality across multiple dimensions. The system is designed to be flexible, extensible, and easy to use for both research and production environments.

