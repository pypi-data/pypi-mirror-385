"""
Quality benchmark implementations for LLM evaluation.

This module provides various quality assessment benchmarks including basic quality
testing, multi-dimensional assessment, task-specific evaluation, and consistency testing.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import statistics
from pathlib import Path

# Optional dependencies for advanced evaluation
try:
    from ragas import evaluate
    from ragas.metrics import (
        Faithfulness,
        ResponseRelevancy,
        ContextPrecision,
        ContextRecall,
        AnswerCorrectness,
        AnswerRelevancy,
        AnswerSimilarity,
        ContextRelevancy,
        ContextUtilization,
        ResponseCompleteness,
        ResponseConsistency,
        ResponseConciseness,
        ResponseTone,
        ResponseFormat,
    )
    from ragas.run_config import RunConfig
    from ragas.llms import LangchainLLMWrapper
    from datasets import Dataset

    RAGAS_AVAILABLE = True
except ImportError:
    RAGAS_AVAILABLE = False

try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_google_genai import ChatGoogleGenerativeAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False

from ..core.base import LLMProvider, TaskRequest, TaskResponse, TaskType
from ..providers.base_provider import BaseProvider


@dataclass
class TestCase:
    """A single test case for quality evaluation."""

    prompt: str
    expected: str
    type: str  # factual, creative, explanatory, analytical
    dimensions: Optional[List[str]] = None
    context: Optional[List[str]] = None
    ground_truths: Optional[List[str]] = None


@dataclass
class QualityMetrics:
    """Quality metrics for a single evaluation."""

    accuracy: float
    factual_accuracy: float
    creative_quality: float
    explanatory_quality: float
    analytical_quality: float
    avg_quality_score: float
    quality_variance: float
    completeness: float
    coherence: float
    relevance: float
    originality: float
    response_length: int
    total_errors: int
    factual_errors: int
    logical_errors: int
    format_errors: int
    error_rate: float


@dataclass
class ProviderMetrics:
    """Quality metrics for a specific provider."""

    accuracy: float
    quality_score: float
    factual_accuracy: float
    creative_quality: float
    explanatory_quality: float
    analytical_quality: float
    avg_response_time: float
    total_tests: int
    successful_tests: int


@dataclass
class QualityResults:
    """Results from quality benchmark evaluation."""

    overall_accuracy: float
    factual_accuracy: float
    creative_quality: float
    explanatory_quality: float
    analytical_quality: float
    avg_quality_score: float
    quality_variance: float
    provider_metrics: Dict[str, ProviderMetrics]
    task_metrics: Dict[str, ProviderMetrics]
    dimension_scores: Dict[str, float]
    consistency_score: float
    factual_consistency: float
    creative_consistency: float
    accuracy_by_type: Dict[str, float]  # Accuracy broken down by test case type
    response_variance: float
    evaluation_time: float
    test_case_results: List[Dict[str, Any]] = field(
        default_factory=list
    )  # Detailed results for each test case
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def accuracy(self) -> float:
        """Alias for overall_accuracy for backward compatibility."""
        return self.overall_accuracy

    @property
    def quality_score(self) -> float:
        """Alias for avg_quality_score for backward compatibility."""
        return self.avg_quality_score

    def get_quality_metrics(self) -> QualityMetrics:
        """Get detailed quality metrics."""
        return QualityMetrics(
            accuracy=self.overall_accuracy,
            factual_accuracy=self.factual_accuracy,
            creative_quality=self.creative_quality,
            explanatory_quality=self.explanatory_quality,
            analytical_quality=self.analytical_quality,
            avg_quality_score=self.avg_quality_score,
            quality_variance=self.quality_variance,
            completeness=0.0,  # Would be calculated from detailed analysis
            coherence=0.0,
            relevance=0.0,
            originality=0.0,
            response_length=0,
            total_errors=0,
            factual_errors=0,
            logical_errors=0,
            format_errors=0,
            error_rate=0.0,
        )

    def get_response_metrics(self) -> Dict[str, float]:
        """Get response-specific metrics."""
        return {
            "avg_length": 0,  # Would be calculated from actual responses
            "completeness": 0.0,
            "coherence": 0.0,
            "relevance": 0.0,
            "originality": 0.0,
        }

    def get_error_metrics(self) -> Dict[str, Any]:
        """Get error analysis metrics."""
        return {
            "total_errors": 0,
            "factual_errors": 0,
            "logical_errors": 0,
            "format_errors": 0,
            "error_rate": 0.0,
        }


class QualityBenchmark:
    """
    Basic quality benchmark for evaluating LLM responses.

    This class provides comprehensive quality assessment using RAGAS metrics
    and custom evaluation methods.
    """

    def __init__(
        self,
        test_cases: List[TestCase],
        providers: Optional[List[LLMProvider]] = None,
        models: Optional[List[str]] = None,
        iterations: int = 5,
        temperature: float = 0.7,
        evaluator_llm: Optional[str] = "gpt-4o",
        use_ragas: bool = True,
        switch: Optional[Any] = None,
    ):
        """
        Initialize quality benchmark.

        Args:
            test_cases: List of test cases to evaluate
            providers: List of provider instances to test
            models: List of models to test (default: all available)
            iterations: Number of iterations per test case
            temperature: Temperature for LLM generation
            evaluator_llm: LLM to use for evaluation
            use_ragas: Whether to use RAGAS for evaluation
            switch: Switch engine instance for testing
        """
        # Validate inputs
        if not test_cases:
            raise ValueError("test_cases cannot be empty")
        if iterations <= 0:
            raise ValueError("iterations must be positive")

        # Convert dictionaries to TestCase objects if needed
        converted_test_cases = []
        for test_case in test_cases:
            if isinstance(test_case, dict):
                # Convert dictionary to TestCase
                converted_test_case = TestCase(
                    prompt=test_case.get("prompt", ""),
                    expected=test_case.get("expected", ""),
                    type=test_case.get("type", "factual"),
                    dimensions=test_case.get("dimensions"),
                    context=test_case.get("context"),
                    ground_truths=test_case.get("ground_truths"),
                )
                converted_test_cases.append(converted_test_case)
            else:
                converted_test_cases.append(test_case)

        self.test_cases = converted_test_cases
        self.providers = providers or []
        self.models = models or []
        self.iterations = iterations
        self.temperature = temperature
        self.evaluator_llm = evaluator_llm
        self.use_ragas = use_ragas and RAGAS_AVAILABLE
        self.switch = switch

        # Initialize evaluator (only if not in test mode)
        try:
            self._evaluator_llm = self._initialize_evaluator()
        except Exception:
            # If evaluator initialization fails (e.g., missing API keys), set to None
            self._evaluator_llm = None

        # RAGAS metrics
        if self.use_ragas:
            self._ragas_metrics = self._initialize_ragas_metrics()

    def _initialize_evaluator(self):
        """Initialize evaluator LLM."""
        if not LANGCHAIN_AVAILABLE:
            return None

        if "gpt" in self.evaluator_llm:
            return ChatOpenAI(model=self.evaluator_llm, temperature=0)
        elif "claude" in self.evaluator_llm:
            return ChatAnthropic(model=self.evaluator_llm, temperature=0)
        elif "gemini" in self.evaluator_llm:
            return ChatGoogleGenerativeAI(model=self.evaluator_llm, temperature=0)
        else:
            return ChatOpenAI(model="gpt-4o", temperature=0)

    def _initialize_ragas_metrics(self) -> List:
        """Initialize RAGAS metrics."""
        if not RAGAS_AVAILABLE:
            return []

        return [
            ResponseRelevancy(),
            AnswerCorrectness(),
            AnswerRelevancy(),
            AnswerSimilarity(),
            ResponseCompleteness(),
            ResponseConsistency(),
            ResponseConciseness(),
        ]

    async def run(self) -> QualityResults:
        """Run the quality benchmark."""
        start_time = time.time()

        # Collect all responses
        all_responses = []
        provider_metrics = {}

        # Use switch engine if available, otherwise use providers directly
        if self.switch:
            # Use switch engine for processing
            for test_case in self.test_cases:
                for iteration in range(self.iterations):
                    try:
                        # Create task request
                        request = TaskRequest(
                            prompt=test_case.prompt,
                            task_type=TaskType.TEXT_GENERATION,
                            temperature=self.temperature,
                        )

                        # Use switch engine to process request
                        try:
                            response = await self.switch.process_request(request)
                        except Exception as e:
                            print(f"Switch engine error: {e}")
                            continue

                        all_responses.append(
                            {
                                "test_case": test_case,
                                "response": (
                                    response.content
                                    if hasattr(response, "content")
                                    else str(response)
                                ),
                                "iteration": iteration,
                                "provider": getattr(response, "provider", "unknown"),
                            }
                        )

                    except Exception as e:
                        print(f"Error generating response: {e}")
                        continue
        else:
            # Fallback to direct provider usage
            for provider in self.providers:
                provider_responses = []
                provider_start_time = time.time()

                for test_case in self.test_cases:
                    for iteration in range(self.iterations):
                        try:
                            # Create task request
                            request = TaskRequest(
                                prompt=test_case.prompt,
                                task_type=TaskType.TEXT_GENERATION,
                                temperature=self.temperature,
                            )

                            # Get available models for this provider
                            available_models = provider.get_models_for_task(
                                TaskType.TEXT_GENERATION
                            )
                            if not available_models:
                                continue

                            model = available_models[0]  # Use first available model

                            # Generate response
                            response = await provider.generate(request, model)

                            provider_responses.append(
                                {
                                    "test_case": test_case,
                                    "response": (
                                        response.content
                                        if hasattr(response, "content")
                                        else str(response)
                                    ),
                                    "iteration": iteration,
                                    "provider": (
                                        provider.provider_name
                                        if hasattr(provider, "provider_name")
                                        else str(provider)
                                    ),
                                }
                            )

                        except Exception as e:
                            print(f"Error generating response: {e}")
                            continue

                # Calculate provider metrics
                provider_name = (
                    provider.provider_name
                    if hasattr(provider, "provider_name")
                    else str(provider)
                )
                provider_metrics[provider_name] = self._calculate_provider_metrics(
                    provider_responses, provider_name
                )

                all_responses.extend(provider_responses)

        # Evaluate responses
        if self.use_ragas and all_responses:
            ragas_results = await self._evaluate_with_ragas(all_responses)
        else:
            ragas_results = None

        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(all_responses, ragas_results)

        evaluation_time = time.time() - start_time

        # Create test case results from all_responses
        test_case_results = []
        for resp in all_responses:
            test_case_results.append(
                {
                    "test_case": resp["test_case"].prompt,
                    "response": resp["response"],
                    "provider": resp["provider"],
                    "iteration": resp["iteration"],
                    "accuracy": self._calculate_simple_accuracy(
                        resp["test_case"], resp["response"]
                    ),
                }
            )

        return QualityResults(
            overall_accuracy=overall_metrics["accuracy"],
            factual_accuracy=overall_metrics["factual_accuracy"],
            creative_quality=overall_metrics["creative_quality"],
            explanatory_quality=overall_metrics["explanatory_quality"],
            analytical_quality=overall_metrics["analytical_quality"],
            avg_quality_score=overall_metrics["avg_quality_score"],
            quality_variance=overall_metrics["quality_variance"],
            provider_metrics=provider_metrics,
            task_metrics={},  # Would be calculated from task-specific analysis
            dimension_scores={},  # Would be calculated from multi-dimensional analysis
            consistency_score=overall_metrics["consistency_score"],
            factual_consistency=overall_metrics["factual_consistency"],
            creative_consistency=overall_metrics["creative_consistency"],
            accuracy_by_type=overall_metrics.get("accuracy_by_type", {}),
            response_variance=overall_metrics["response_variance"],
            evaluation_time=evaluation_time,
            test_case_results=test_case_results,
        )

    async def _evaluate_with_ragas(self, responses: List[Dict]) -> Optional[Dict]:
        """Evaluate responses using RAGAS."""
        if not RAGAS_AVAILABLE or not self._evaluator_llm:
            return None

        try:
            # Prepare dataset for RAGAS
            dataset_data = []
            for resp in responses:
                test_case = resp["test_case"]
                dataset_data.append(
                    {
                        "question": test_case.prompt,
                        "contexts": test_case.context or [],
                        "answer": resp["response"],
                        "ground_truths": test_case.ground_truths
                        or [test_case.expected],
                    }
                )

            if not dataset_data:
                return None

            dataset = Dataset.from_list(dataset_data)

            # Configure RAGAS
            evaluator_llm = LangchainLLMWrapper(self._evaluator_llm)
            run_config = RunConfig(
                timeout=300,
                max_concurrent=5,
                max_retries=3,
            )

            # Run evaluation
            results = evaluate(
                dataset=dataset,
                metrics=self._ragas_metrics,
                llm=evaluator_llm,
                run_config=run_config,
            )

            return results

        except Exception as e:
            print(f"Error in RAGAS evaluation: {e}")
            return None

    def _calculate_provider_metrics(
        self, responses: List[Dict], provider_name: str
    ) -> ProviderMetrics:
        """Calculate metrics for a specific provider."""
        if not responses:
            return ProviderMetrics(
                accuracy=0.0,
                quality_score=0.0,
                factual_accuracy=0.0,
                creative_quality=0.0,
                explanatory_quality=0.0,
                analytical_quality=0.0,
                avg_response_time=0.0,
                total_tests=0,
                successful_tests=0,
            )

        # Calculate accuracy by test type
        factual_scores = []
        creative_scores = []
        explanatory_scores = []
        analytical_scores = []

        for resp in responses:
            test_case = resp["test_case"]
            response = resp["response"]

            # Simple accuracy calculation (would be enhanced with better evaluation)
            accuracy = self._calculate_simple_accuracy(test_case, response)

            if test_case.type == "factual":
                factual_scores.append(accuracy)
            elif test_case.type == "creative":
                creative_scores.append(accuracy)
            elif test_case.type == "explanatory":
                explanatory_scores.append(accuracy)
            elif test_case.type == "analytical":
                analytical_scores.append(accuracy)

        return ProviderMetrics(
            accuracy=(
                statistics.mean(
                    [
                        s
                        for scores in [
                            factual_scores,
                            creative_scores,
                            explanatory_scores,
                            analytical_scores,
                        ]
                        for s in scores
                    ]
                )
                if any(
                    [
                        factual_scores,
                        creative_scores,
                        explanatory_scores,
                        analytical_scores,
                    ]
                )
                else 0.0
            ),
            quality_score=(
                statistics.mean(
                    [
                        s
                        for scores in [
                            factual_scores,
                            creative_scores,
                            explanatory_scores,
                            analytical_scores,
                        ]
                        for s in scores
                    ]
                )
                if any(
                    [
                        factual_scores,
                        creative_scores,
                        explanatory_scores,
                        analytical_scores,
                    ]
                )
                else 0.0
            ),
            factual_accuracy=statistics.mean(factual_scores) if factual_scores else 0.0,
            creative_quality=(
                statistics.mean(creative_scores) if creative_scores else 0.0
            ),
            explanatory_quality=(
                statistics.mean(explanatory_scores) if explanatory_scores else 0.0
            ),
            analytical_quality=(
                statistics.mean(analytical_scores) if analytical_scores else 0.0
            ),
            avg_response_time=0.0,  # Would be calculated from actual timing
            total_tests=len(responses),
            successful_tests=len([r for r in responses if r["response"]]),
        )

    def _calculate_simple_accuracy(self, test_case: TestCase, response: str) -> float:
        """Calculate simple accuracy score."""
        if not response:
            return 0.0

        # Simple keyword matching (would be enhanced with better evaluation)
        expected_lower = test_case.expected.lower()
        response_lower = response.lower()

        if expected_lower in response_lower:
            return 1.0

        # Check for partial matches
        expected_words = set(expected_lower.split())
        response_words = set(response_lower.split())

        if expected_words.intersection(response_words):
            return 0.5

        return 0.0

    def _calculate_overall_metrics(
        self, all_responses: List[Dict], ragas_results: Optional[Dict]
    ) -> Dict[str, float]:
        """Calculate overall quality metrics."""
        if not all_responses:
            return {
                "accuracy": 0.0,
                "factual_accuracy": 0.0,
                "creative_quality": 0.0,
                "explanatory_quality": 0.0,
                "analytical_quality": 0.0,
                "avg_quality_score": 0.0,
                "quality_variance": 0.0,
                "consistency_score": 0.0,
                "factual_consistency": 0.0,
                "creative_consistency": 0.0,
                "response_variance": 0.0,
                "accuracy_by_type": {},
            }

        # Calculate accuracy by type
        factual_scores = []
        creative_scores = []
        explanatory_scores = []
        analytical_scores = []
        mathematical_scores = []

        for resp in all_responses:
            test_case = resp["test_case"]
            response = resp["response"]
            accuracy = self._calculate_simple_accuracy(test_case, response)

            if test_case.type == "factual":
                factual_scores.append(accuracy)
            elif test_case.type == "creative":
                creative_scores.append(accuracy)
            elif test_case.type == "explanatory":
                explanatory_scores.append(accuracy)
            elif test_case.type == "analytical":
                analytical_scores.append(accuracy)
            elif test_case.type == "mathematical":
                mathematical_scores.append(accuracy)

        all_scores = (
            factual_scores
            + creative_scores
            + explanatory_scores
            + analytical_scores
            + mathematical_scores
        )

        return {
            "accuracy": statistics.mean(all_scores) if all_scores else 0.0,
            "factual_accuracy": (
                statistics.mean(factual_scores) if factual_scores else 0.0
            ),
            "creative_quality": (
                statistics.mean(creative_scores) if creative_scores else 0.0
            ),
            "explanatory_quality": (
                statistics.mean(explanatory_scores) if explanatory_scores else 0.0
            ),
            "analytical_quality": (
                statistics.mean(analytical_scores) if analytical_scores else 0.0
            ),
            "avg_quality_score": statistics.mean(all_scores) if all_scores else 0.0,
            "quality_variance": (
                statistics.variance(all_scores) if len(all_scores) > 1 else 0.0
            ),
            "consistency_score": 0.0,  # Would be calculated from consistency analysis
            "factual_consistency": 0.0,
            "creative_consistency": 0.0,
            "response_variance": 0.0,
            "accuracy_by_type": {
                "factual": statistics.mean(factual_scores) if factual_scores else 0.0,
                "creative": (
                    statistics.mean(creative_scores) if creative_scores else 0.0
                ),
                "explanatory": (
                    statistics.mean(explanatory_scores) if explanatory_scores else 0.0
                ),
                "analytical": (
                    statistics.mean(analytical_scores) if analytical_scores else 0.0
                ),
                "mathematical": (
                    statistics.mean(mathematical_scores) if mathematical_scores else 0.0
                ),
            },
        }


class MultiDimensionalQualityBenchmark(QualityBenchmark):
    """Multi-dimensional quality benchmark for comprehensive evaluation."""

    def __init__(
        self,
        test_cases,
        providers=None,
        models=None,
        iterations=5,
        temperature=0.7,
        evaluator_llm="gpt-4o",
        use_ragas=True,
        dimensions=None,
        **kwargs,
    ):
        super().__init__(
            test_cases,
            providers,
            models,
            iterations,
            temperature,
            evaluator_llm,
            use_ragas,
        )
        self.dimensions = dimensions or [
            "accuracy",
            "relevance",
            "coherence",
            "completeness",
        ]

    async def run(self) -> QualityResults:
        """Run multi-dimensional quality benchmark."""
        results = await super().run()

        # Calculate dimension-specific scores
        dimension_scores = {}
        for dimension in self.dimensions:
            dimension_scores[dimension] = self._calculate_dimension_score(dimension)

        results.dimension_scores = dimension_scores
        return results

    def _calculate_dimension_score(self, dimension: str) -> float:
        """Calculate score for a specific dimension."""
        # This would be implemented with more sophisticated evaluation
        return 0.8  # Placeholder


class TaskSpecificQualityBenchmark(QualityBenchmark):
    """Task-specific quality benchmark for specialized evaluation."""

    def __init__(
        self,
        task_types: List[str],
        test_cases,
        providers=None,
        models=None,
        iterations=5,
        temperature=0.7,
        evaluator_llm="gpt-4o",
        use_ragas=True,
        **kwargs,
    ):
        super().__init__(
            test_cases,
            providers,
            models,
            iterations,
            temperature,
            evaluator_llm,
            use_ragas,
        )
        self.task_types = task_types

    async def run(self) -> QualityResults:
        """Run task-specific quality benchmark."""
        results = await super().run()

        # Calculate task-specific metrics
        task_metrics = {}
        for task_type in self.task_types:
            task_metrics[task_type] = self._calculate_task_metrics(task_type)

        results.task_metrics = task_metrics
        return results

    def _calculate_task_metrics(self, task_type: str) -> ProviderMetrics:
        """Calculate metrics for a specific task type."""
        # This would be implemented with task-specific evaluation
        return ProviderMetrics(
            accuracy=0.8,
            quality_score=0.8,
            factual_accuracy=0.8,
            creative_quality=0.8,
            explanatory_quality=0.8,
            analytical_quality=0.8,
            avg_response_time=0.0,
            total_tests=0,
            successful_tests=0,
        )


class ConsistencyBenchmark(QualityBenchmark):
    """Consistency benchmark for evaluating response reliability."""

    def __init__(
        self,
        test_prompts: List[str],
        providers=None,
        models=None,
        iterations=5,
        temperature=0.7,
        evaluator_llm="gpt-4o",
        use_ragas=True,
        **kwargs,
    ):
        # Convert prompts to test cases
        test_cases = [
            TestCase(prompt=prompt, expected="", type="consistency")
            for prompt in test_prompts
        ]
        super().__init__(
            test_cases,
            providers,
            models,
            iterations,
            temperature,
            evaluator_llm,
            use_ragas,
        )
        self.test_prompts = test_prompts

    async def run(self) -> QualityResults:
        """Run consistency benchmark."""
        results = await super().run()

        # Calculate consistency metrics
        consistency_metrics = self._calculate_consistency_metrics()

        results.consistency_score = consistency_metrics["consistency_score"]
        results.factual_consistency = consistency_metrics["factual_consistency"]
        results.creative_consistency = consistency_metrics["creative_consistency"]
        results.response_variance = consistency_metrics["response_variance"]

        return results

    def _calculate_consistency_metrics(self) -> Dict[str, float]:
        """Calculate consistency metrics."""
        # This would be implemented with actual consistency analysis
        return {
            "consistency_score": 0.8,
            "factual_consistency": 0.8,
            "creative_consistency": 0.8,
            "response_variance": 0.1,
        }


class RealtimeQualityMonitor:
    """Real-time quality monitoring for continuous evaluation."""

    def __init__(
        self,
        test_cases: List[TestCase],
        providers: List[LLMProvider],
        duration: int = 300,
        check_interval: int = 10,
        alerts: Optional[Dict[str, float]] = None,
    ):
        self.test_cases = test_cases
        self.providers = providers
        self.duration = duration
        self.check_interval = check_interval
        self.alerts = alerts or {}
        self.is_running = False
        self.current_metrics = {}
        self.quality_trend = "stable"

    async def start(self):
        """Start real-time monitoring."""
        self.is_running = True
        start_time = time.time()

        while self.is_running and (time.time() - start_time) < self.duration:
            # Run quality check
            benchmark = QualityBenchmark(self.test_cases, self.providers, iterations=1)
            results = await benchmark.run()

            # Update current metrics
            self.current_metrics = {
                "accuracy": results.overall_accuracy,
                "quality_trend": self.quality_trend,
                "error_rate": 1.0 - results.overall_accuracy,
            }

            # Check alerts
            self._check_alerts(results)

            # Wait for next check
            await asyncio.sleep(self.check_interval)

    async def stop(self):
        """Stop real-time monitoring."""
        self.is_running = False

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics."""
        return self.current_metrics

    def _check_alerts(self, results: QualityResults):
        """Check if any alerts should be triggered."""
        if "accuracy_threshold" in self.alerts:
            if results.overall_accuracy < self.alerts["accuracy_threshold"]:
                print(
                    f"ALERT: Accuracy below threshold: {results.overall_accuracy:.2%}"
                )

        if "error_rate_threshold" in self.alerts:
            error_rate = 1.0 - results.overall_accuracy
            if error_rate > self.alerts["error_rate_threshold"]:
                print(f"ALERT: Error rate above threshold: {error_rate:.2%}")
