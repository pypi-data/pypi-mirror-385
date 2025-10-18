"""
Example usage of quality benchmarks with RAGAS integration.

This script demonstrates how to use the quality benchmarking system
with RAGAS and other evaluation libraries.
"""

import asyncio
import os
from typing import List

# Add the src directory to the path
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_dispatcher.benchmarks import (
    QualityBenchmark,
    MultiDimensionalQualityBenchmark,
    TaskSpecificQualityBenchmark,
    ConsistencyBenchmark,
    RealtimeQualityMonitor,
    AutomatedEvaluator,
    HumanEvaluator,
    HybridEvaluator,
    QualityAnalyzer,
    QualityReporter,
)
from llm_dispatcher.benchmarks.quality_benchmark import TestCase


async def basic_quality_benchmark_example():
    """Example of basic quality benchmarking."""
    print("=== Basic Quality Benchmark Example ===")

    # Define test cases
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris", "The capital of France is Paris"],
        ),
        TestCase(
            prompt="Write a haiku about nature",
            expected="5-7-5 syllable structure",
            type="creative",
            ground_truths=["A haiku with 5-7-5 syllable structure about nature"],
        ),
        TestCase(
            prompt="Explain photosynthesis",
            expected="Process by which plants convert light to energy",
            type="explanatory",
            ground_truths=[
                "Photosynthesis is the process by which plants convert light energy into chemical energy"
            ],
        ),
        TestCase(
            prompt="Analyze the pros and cons of renewable energy",
            expected="balanced analysis",
            type="analytical",
            ground_truths=[
                "A balanced analysis of renewable energy advantages and disadvantages"
            ],
        ),
    ]

    # Create quality benchmark
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=["openai", "anthropic"],  # Use available providers
        models=["gpt-4", "claude-3-sonnet"],
        iterations=3,
        temperature=0.7,
        use_ragas=True,  # Enable RAGAS evaluation
    )

    # Run benchmark
    print("Running quality benchmark...")
    results = await benchmark.run()

    # Print results
    print(f"Overall accuracy: {results.overall_accuracy:.2%}")
    print(f"Factual accuracy: {results.factual_accuracy:.2%}")
    print(f"Creative quality: {results.creative_quality:.2f}")
    print(f"Explanatory quality: {results.explanatory_quality:.2f}")
    print(f"Analytical quality: {results.analytical_quality:.2f}")
    print(f"Average quality score: {results.avg_quality_score:.2f}")
    print(f"Consistency score: {results.consistency_score:.2f}")
    print(f"Evaluation time: {results.evaluation_time:.1f}s")

    # Print provider metrics
    print("\nProvider Metrics:")
    for provider, metrics in results.provider_metrics.items():
        print(f"{provider}:")
        print(f"  Accuracy: {metrics.accuracy:.2%}")
        print(f"  Quality score: {metrics.quality_score:.2f}")
        print(f"  Factual accuracy: {metrics.factual_accuracy:.2%}")
        print(f"  Creative quality: {metrics.creative_quality:.2f}")
        print(f"  Total tests: {metrics.total_tests}")
        print(f"  Successful tests: {metrics.successful_tests}")

    return results


async def multi_dimensional_quality_example():
    """Example of multi-dimensional quality assessment."""
    print("\n=== Multi-Dimensional Quality Benchmark Example ===")

    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            dimensions=["accuracy", "precision", "completeness"],
            ground_truths=["Paris"],
        ),
        TestCase(
            prompt="Write a haiku about spring",
            expected="5-7-5 syllable structure",
            type="creative",
            dimensions=["creativity", "structure", "aesthetics"],
            ground_truths=["A haiku with 5-7-5 syllable structure about spring"],
        ),
        TestCase(
            prompt="Explain machine learning",
            expected="technical explanation",
            type="explanatory",
            dimensions=["accuracy", "clarity", "completeness"],
            ground_truths=["A technical explanation of machine learning concepts"],
        ),
    ]

    benchmark = MultiDimensionalQualityBenchmark(
        test_cases=test_cases,
        providers=["openai"],
        iterations=2,
        dimensions=["accuracy", "relevance", "coherence", "completeness", "creativity"],
    )

    results = await benchmark.run()

    print("Dimension Scores:")
    for dimension, score in results.dimension_scores.items():
        print(f"  {dimension}: {score:.2f}")

    return results


async def task_specific_quality_example():
    """Example of task-specific quality testing."""
    print("\n=== Task-Specific Quality Benchmark Example ===")

    test_cases = {
        "factual": [
            TestCase(
                prompt="What is the population of Tokyo?",
                expected="Approximately 14 million",
                type="factual",
                ground_truths=["About 14 million people", "14 million inhabitants"],
            )
        ],
        "creative": [
            TestCase(
                prompt="Write a poem about the ocean",
                expected="creative poetry",
                type="creative",
                ground_truths=["A creative poem about the ocean"],
            )
        ],
        "explanatory": [
            TestCase(
                prompt="Explain how a computer works",
                expected="technical explanation",
                type="explanatory",
                ground_truths=["A technical explanation of computer operation"],
            )
        ],
        "analytical": [
            TestCase(
                prompt="Analyze the pros and cons of renewable energy",
                expected="balanced analysis",
                type="analytical",
                ground_truths=["A balanced analysis of renewable energy"],
            )
        ],
    }

    benchmark = TaskSpecificQualityBenchmark(
        task_types=["factual", "creative", "explanatory", "analytical"],
        test_cases=test_cases,
        providers=["openai"],
        iterations=2,
    )

    results = await benchmark.run()

    print("Task-Specific Metrics:")
    for task_type, metrics in results.task_metrics.items():
        print(f"{task_type}:")
        print(f"  Quality score: {metrics.quality_score:.2f}")
        print(f"  Accuracy: {metrics.accuracy:.2%}")
        print(f"  Creative quality: {metrics.creative_quality:.2f}")
        print(f"  Explanatory quality: {metrics.explanatory_quality:.2f}")
        print(f"  Analytical quality: {metrics.analytical_quality:.2f}")

    return results


async def consistency_benchmark_example():
    """Example of consistency testing."""
    print("\n=== Consistency Benchmark Example ===")

    test_prompts = [
        "What is the capital of France?",
        "Write a haiku about nature",
        "Explain photosynthesis",
    ]

    benchmark = ConsistencyBenchmark(
        test_prompts=test_prompts,
        providers=["openai"],
        iterations=5,  # Test same prompt multiple times
    )

    results = await benchmark.run()

    print(f"Overall consistency: {results.consistency_score:.2f}")
    print(f"Factual consistency: {results.factual_consistency:.2f}")
    print(f"Creative consistency: {results.creative_consistency:.2f}")
    print(f"Response variance: {results.response_variance:.2f}")

    return results


async def evaluation_methods_example():
    """Example of different evaluation methods."""
    print("\n=== Evaluation Methods Example ===")

    prompts = ["What is the capital of France?", "Write a haiku about spring"]
    responses = ["Paris is the capital of France.", "Spring brings new life..."]
    expected = ["Paris", "5-7-5 syllable structure"]

    # Automated evaluation
    print("Running automated evaluation...")
    automated_evaluator = AutomatedEvaluator(
        evaluation_metrics=["accuracy", "relevance", "coherence", "completeness"],
        use_ragas=True,
    )

    automated_result = await automated_evaluator.evaluate(prompts, responses, expected)
    print(f"Automated evaluation:")
    print(f"  Accuracy: {automated_result.accuracy:.2f}")
    print(f"  Relevance: {automated_result.relevance:.2f}")
    print(f"  Coherence: {automated_result.coherence:.2f}")
    print(f"  Completeness: {automated_result.completeness:.2f}")
    print(f"  Overall score: {automated_result.overall_score:.2f}")

    # Human evaluation (simulated)
    print("\nRunning human evaluation...")
    human_evaluator = HumanEvaluator(
        evaluators=["expert1", "expert2"],
        evaluation_criteria=["accuracy", "relevance", "coherence", "creativity"],
    )

    human_result = await human_evaluator.evaluate(prompts, responses, expected)
    print(f"Human evaluation:")
    print(f"  Accuracy: {human_result.accuracy:.2f}")
    print(f"  Relevance: {human_result.relevance:.2f}")
    print(f"  Coherence: {human_result.coherence:.2f}")
    print(f"  Creativity: {human_result.creativity:.2f}")
    print(f"  Inter-rater reliability: {human_result.inter_rater_reliability:.2f}")
    print(f"  Average human score: {human_result.avg_human_score:.2f}")

    # Hybrid evaluation
    print("\nRunning hybrid evaluation...")
    hybrid_evaluator = HybridEvaluator(
        automated_metrics=["accuracy", "relevance"],
        human_metrics=["creativity", "aesthetics"],
        weight_automated=0.7,
        weight_human=0.3,
    )

    hybrid_result = await hybrid_evaluator.evaluate(prompts, responses, expected)
    print(f"Hybrid evaluation:")
    print(f"  Hybrid score: {hybrid_result.hybrid_score:.2f}")
    print(f"  Automated score: {hybrid_result.automated_score:.2f}")
    print(f"  Human score: {hybrid_result.human_score:.2f}")
    print(f"  Overall score: {hybrid_result.overall_score:.2f}")


async def realtime_monitoring_example():
    """Example of real-time quality monitoring."""
    print("\n=== Real-time Quality Monitoring Example ===")

    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris"],
        )
    ]

    # Create monitor
    monitor = RealtimeQualityMonitor(
        test_cases=test_cases,
        duration=30,  # 30 seconds for demo
        check_interval=5,  # Check every 5 seconds
        alerts={"accuracy_threshold": 0.8, "error_rate_threshold": 0.2},
    )

    print("Starting real-time monitoring for 30 seconds...")

    # Start monitoring in background
    monitoring_task = asyncio.create_task(monitor.start())

    # Check metrics while monitoring
    for i in range(6):  # Check 6 times (30 seconds / 5 seconds)
        await asyncio.sleep(5)
        if monitor.is_running:
            metrics = monitor.get_current_metrics()
            print(
                f"Check {i+1}: Accuracy={metrics.get('accuracy', 0):.2%}, "
                f"Error rate={metrics.get('error_rate', 0):.2%}"
            )

    # Stop monitoring
    await monitor.stop()
    await monitoring_task

    print("Monitoring completed.")


async def analysis_and_reporting_example():
    """Example of analysis and reporting."""
    print("\n=== Analysis and Reporting Example ===")

    # First run a benchmark to get results
    test_cases = [
        TestCase(
            prompt="What is the capital of France?",
            expected="Paris",
            type="factual",
            ground_truths=["Paris"],
        ),
        TestCase(
            prompt="Write a haiku about nature",
            expected="5-7-5 syllable structure",
            type="creative",
            ground_truths=["A haiku with 5-7-5 syllable structure"],
        ),
    ]

    benchmark = QualityBenchmark(
        test_cases=test_cases, providers=["openai"], iterations=2
    )

    results = await benchmark.run()

    # Analyze results
    print("Analyzing results...")
    analyzer = QualityAnalyzer(results)

    # Statistical analysis
    stats = analyzer.get_statistical_analysis()
    print("Statistical Analysis:")
    for metric, analysis in stats.items():
        print(f"  {metric}:")
        print(f"    Mean: {analysis.mean:.3f}")
        print(f"    Std: {analysis.std:.3f}")
        print(f"    95th percentile: {analysis.p95:.3f}")

    # Distribution analysis
    distribution = analyzer.get_distribution_analysis()
    print(f"\nDistribution Analysis:")
    print(f"  Quality distribution: {distribution.quality}")
    print(f"  Accuracy distribution: {distribution.accuracy}")

    # Trend analysis
    trends = analyzer.get_trend_analysis()
    print(f"\nTrend Analysis:")
    print(f"  Quality trend: {trends.quality.direction}")
    print(f"  Accuracy trend: {trends.accuracy.direction}")

    # Provider comparison
    comparison = analyzer.compare_providers()
    print(f"\nProvider Comparison:")
    for provider, metrics in comparison.items():
        print(
            f"  {provider}: Quality={metrics.quality_score:.2f}, Accuracy={metrics.accuracy:.2%}"
        )

    # Generate reports
    print("\nGenerating reports...")
    reporter = QualityReporter(results)

    # Generate HTML report
    report_file = "quality_report.html"
    reporter.generate_report(report_file)
    print(f"HTML report generated: {report_file}")

    # Generate charts (if matplotlib is available)
    try:
        chart_file = "quality_charts.png"
        reporter.generate_charts(chart_file)
        print(f"Charts generated: {chart_file}")
    except ImportError:
        print("Matplotlib not available, skipping chart generation")

    # Generate interactive charts (if plotly is available)
    try:
        interactive_file = "quality_interactive.html"
        reporter.generate_interactive_charts(interactive_file)
        print(f"Interactive charts generated: {interactive_file}")
    except ImportError:
        print("Plotly not available, skipping interactive chart generation")


async def main():
    """Main function to run all examples."""
    print("Quality Benchmark Examples with RAGAS Integration")
    print("=" * 50)

    try:
        # Run examples
        await basic_quality_benchmark_example()
        await multi_dimensional_quality_example()
        await task_specific_quality_example()
        await consistency_benchmark_example()
        await evaluation_methods_example()
        await realtime_monitoring_example()
        await analysis_and_reporting_example()

        print("\n" + "=" * 50)
        print("All examples completed successfully!")

    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have the required dependencies installed:")
        print(
            "pip install ragas langchain-openai langchain-anthropic langchain-google-genai"
        )
        print("pip install sentence-transformers scikit-learn matplotlib plotly")


if __name__ == "__main__":
    # Set up environment variables for API keys (you'll need to set these)
    # os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
    # os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-api-key"
    # os.environ["GOOGLE_API_KEY"] = "your-google-api-key"

    asyncio.run(main())
