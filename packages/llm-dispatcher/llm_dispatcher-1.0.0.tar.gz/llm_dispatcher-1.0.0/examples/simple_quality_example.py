#!/usr/bin/env python3
"""
Simple quality benchmark example using the existing library structure.

This example shows how to use quality benchmarks with your existing
LLM dispatcher library without requiring external dependencies.
"""

import asyncio
import sys
import os
from typing import List

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from llm_dispatcher.benchmarks.quality_benchmark import (
    TestCase,
    QualityBenchmark,
    MultiDimensionalQualityBenchmark,
    ConsistencyBenchmark,
)
from llm_dispatcher.benchmarks.evaluation import (
    AutomatedEvaluator,
    HumanEvaluator,
    HybridEvaluator,
)
from llm_dispatcher.core.base import TaskRequest, TaskResponse, TaskType
from llm_dispatcher.providers.base_provider import BaseProvider


class MockProvider(BaseProvider):
    """Mock provider for testing without API calls."""

    def __init__(self, name: str = "mock"):
        # Initialize with dummy API key
        super().__init__("dummy_key", name)
        self.provider_name = name

    def _initialize_models(self) -> None:
        """Initialize mock models."""
        from llm_dispatcher.core.base import ModelInfo, Capability

        self.models = {
            "mock-model": ModelInfo(
                name="mock-model",
                provider=self.provider_name,
                capabilities=[Capability.TEXT],
                max_tokens=4096,
                context_window=4096,
                cost_per_1k_tokens={"input": 0.001, "output": 0.002},
            )
        }

    async def generate(self, request: TaskRequest, model: str) -> TaskResponse:
        """Generate a mock response."""
        from llm_dispatcher.core.base import TaskResponse

        # Generate mock response based on prompt
        if "capital" in request.prompt.lower():
            content = "Paris is the capital of France."
        elif "haiku" in request.prompt.lower():
            content = "Spring brings new life\nBirds sing in the morning light\nNature awakens"
        elif "explain" in request.prompt.lower():
            content = "This is a technical explanation of the requested topic."
        else:
            content = "This is a mock response for testing purposes."

        return TaskResponse(
            content=content,
            model_used=model,
            provider=self.provider_name,
            tokens_used=len(content.split()),
            cost=0.001,
            latency_ms=100,
            finish_reason="stop",
        )

    async def generate_stream(self, request: TaskRequest, model: str):
        """Generate a streaming response."""
        response = await self.generate(request, model)
        yield response.content

    async def get_embeddings(self, text: str, model: str) -> List[float]:
        """Get mock embeddings."""
        # Return mock embeddings
        return [0.1] * 384  # Typical embedding dimension


async def basic_quality_example():
    """Basic quality benchmark example."""
    print("=== Basic Quality Benchmark Example ===")

    # Create test cases
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
    ]

    # Create mock provider
    mock_provider = MockProvider("mock")

    # Create quality benchmark
    benchmark = QualityBenchmark(
        test_cases=test_cases,
        providers=[mock_provider],
        iterations=2,
        use_ragas=False,  # Disable RAGAS for this example
    )

    # Run benchmark
    print("Running quality benchmark...")
    results = await benchmark.run()

    # Print results
    print(f"Overall accuracy: {results.overall_accuracy:.2%}")
    print(f"Factual accuracy: {results.factual_accuracy:.2%}")
    print(f"Creative quality: {results.creative_quality:.2f}")
    print(f"Explanatory quality: {results.explanatory_quality:.2f}")
    print(f"Average quality score: {results.avg_quality_score:.2f}")
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


async def multi_dimensional_example():
    """Multi-dimensional quality benchmark example."""
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
    ]

    mock_provider = MockProvider("mock")

    benchmark = MultiDimensionalQualityBenchmark(
        test_cases=test_cases,
        providers=[mock_provider],
        iterations=2,
        dimensions=["accuracy", "relevance", "coherence", "completeness", "creativity"],
    )

    results = await benchmark.run()

    print("Dimension Scores:")
    for dimension, score in results.dimension_scores.items():
        print(f"  {dimension}: {score:.2f}")

    return results


async def consistency_example():
    """Consistency benchmark example."""
    print("\n=== Consistency Benchmark Example ===")

    test_prompts = [
        "What is the capital of France?",
        "Write a haiku about nature",
        "Explain photosynthesis",
    ]

    mock_provider = MockProvider("mock")

    benchmark = ConsistencyBenchmark(
        test_prompts=test_prompts, providers=[mock_provider], iterations=3
    )

    results = await benchmark.run()

    print(f"Overall consistency: {results.consistency_score:.2f}")
    print(f"Factual consistency: {results.factual_consistency:.2f}")
    print(f"Creative consistency: {results.creative_consistency:.2f}")
    print(f"Response variance: {results.response_variance:.2f}")

    return results


async def evaluation_methods_example():
    """Evaluation methods example."""
    print("\n=== Evaluation Methods Example ===")

    prompts = ["What is the capital of France?", "Write a haiku about spring"]
    responses = ["Paris is the capital of France.", "Spring brings new life..."]
    expected = ["Paris", "5-7-5 syllable structure"]

    # Automated evaluation
    print("Running automated evaluation...")
    automated_evaluator = AutomatedEvaluator(
        evaluation_metrics=["accuracy", "relevance", "coherence", "completeness"],
        use_ragas=False,  # Disable RAGAS for this example
        use_semantic_similarity=False,  # Disable for this example
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


async def main():
    """Main function to run all examples."""
    print("Simple Quality Benchmark Examples")
    print("=" * 50)

    try:
        # Run examples
        await basic_quality_example()
        await multi_dimensional_example()
        await consistency_example()
        await evaluation_methods_example()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")
        print("\nThis demonstrates the quality benchmarking system working")
        print("with your existing library structure. To use with real providers:")
        print("1. Set up your API keys")
        print("2. Use real provider instances instead of MockProvider")
        print("3. Optionally install RAGAS for advanced evaluation")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
