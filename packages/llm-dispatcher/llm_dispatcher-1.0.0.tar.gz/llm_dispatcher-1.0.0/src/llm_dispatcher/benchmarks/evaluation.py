"""
Evaluation methods for quality assessment.

This module provides automated, human, and hybrid evaluation methods
for assessing LLM response quality.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import statistics
import json

# Optional dependencies for advanced evaluation
try:
    from ragas import evaluate
    from ragas.metrics import (
        Faithfulness,
        ResponseRelevancy,
        AnswerCorrectness,
        AnswerRelevancy,
        AnswerSimilarity,
        ResponseCompleteness,
        ResponseConsistency,
        ResponseConciseness,
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


@dataclass
class EvaluationResult:
    """Result from an evaluation method."""

    accuracy: float
    relevance: float
    coherence: float
    completeness: float
    creativity: Optional[float] = None
    aesthetics: Optional[float] = None
    overall_score: float = 0.0
    evaluation_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Calculate overall score if not provided."""
        if self.overall_score == 0.0:
            scores = [self.accuracy, self.relevance, self.coherence, self.completeness]
            if self.creativity is not None:
                scores.append(self.creativity)
            if self.aesthetics is not None:
                scores.append(self.aesthetics)
            self.overall_score = statistics.mean(scores)


@dataclass
class HumanEvaluationResult(EvaluationResult):
    """Result from human evaluation."""

    inter_rater_reliability: float = 0.0
    avg_human_score: float = 0.0
    evaluator_scores: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class HybridEvaluationResult(EvaluationResult):
    """Result from hybrid evaluation."""

    automated_score: float = 0.0
    human_score: float = 0.0
    hybrid_score: float = 0.0
    weight_automated: float = 0.7
    weight_human: float = 0.3


class AutomatedEvaluator:
    """
    Automated evaluation using various metrics and models.

    This class provides automated evaluation using RAGAS metrics,
    semantic similarity, and other automated methods.
    """

    def __init__(
        self,
        evaluation_metrics: List[str] = None,
        evaluator_llm: str = "gpt-4o",
        use_ragas: bool = True,
        use_semantic_similarity: bool = True,
    ):
        """
        Initialize automated evaluator.

        Args:
            evaluation_metrics: List of metrics to evaluate
            evaluator_llm: LLM to use for evaluation
            use_ragas: Whether to use RAGAS metrics
            use_semantic_similarity: Whether to use semantic similarity
        """
        self.evaluation_metrics = evaluation_metrics or [
            "accuracy",
            "relevance",
            "coherence",
            "completeness",
        ]
        self.evaluator_llm = evaluator_llm
        self.use_ragas = use_ragas and RAGAS_AVAILABLE
        self.use_semantic_similarity = use_semantic_similarity and SEMANTIC_AVAILABLE

        # Initialize components
        self._evaluator_llm = self._initialize_evaluator()
        self._ragas_metrics = self._initialize_ragas_metrics()
        self._sentence_model = self._initialize_sentence_model()

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

        metric_map = {
            "accuracy": AnswerCorrectness(),
            "relevance": ResponseRelevancy(),
            "coherence": ResponseConsistency(),
            "completeness": ResponseCompleteness(),
        }

        return [
            metric_map.get(metric)
            for metric in self.evaluation_metrics
            if metric in metric_map
        ]

    def _initialize_sentence_model(self):
        """Initialize sentence transformer model."""
        if not self.use_semantic_similarity:
            return None

        try:
            return SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            print(
                "Warning: sentence-transformers not available for semantic similarity"
            )
            return None

    async def evaluate(
        self,
        prompts: List[str],
        responses: List[str],
        expected: List[str],
        contexts: Optional[List[List[str]]] = None,
    ) -> EvaluationResult:
        """
        Evaluate responses using automated methods.

        Args:
            prompts: List of input prompts
            responses: List of generated responses
            expected: List of expected responses
            contexts: Optional list of context for each prompt

        Returns:
            EvaluationResult with automated scores
        """
        start_time = time.time()

        # Prepare data
        if contexts is None:
            contexts = [[] for _ in prompts]

        # Evaluate using RAGAS if available
        ragas_scores = {}
        if self.use_ragas and self._ragas_metrics:
            ragas_scores = await self._evaluate_with_ragas(
                prompts, responses, expected, contexts
            )

        # Evaluate using semantic similarity
        semantic_scores = {}
        if self.use_semantic_similarity and self._sentence_model:
            semantic_scores = self._evaluate_semantic_similarity(responses, expected)

        # Evaluate using LLM-based scoring
        llm_scores = {}
        if self._evaluator_llm:
            llm_scores = await self._evaluate_with_llm(prompts, responses, expected)

        # Combine scores
        final_scores = self._combine_scores(ragas_scores, semantic_scores, llm_scores)

        evaluation_time = time.time() - start_time

        return EvaluationResult(
            accuracy=final_scores.get("accuracy", 0.0),
            relevance=final_scores.get("relevance", 0.0),
            coherence=final_scores.get("coherence", 0.0),
            completeness=final_scores.get("completeness", 0.0),
            creativity=final_scores.get("creativity"),
            aesthetics=final_scores.get("aesthetics"),
            evaluation_time=evaluation_time,
        )

    async def _evaluate_with_ragas(
        self,
        prompts: List[str],
        responses: List[str],
        expected: List[str],
        contexts: List[List[str]],
    ) -> Dict[str, float]:
        """Evaluate using RAGAS metrics."""
        try:
            # Prepare dataset
            dataset_data = []
            for i, prompt in enumerate(prompts):
                dataset_data.append(
                    {
                        "question": prompt,
                        "contexts": contexts[i],
                        "answer": responses[i],
                        "ground_truths": [expected[i]],
                    }
                )

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

            # Extract scores
            scores = {}
            for metric in self._ragas_metrics:
                metric_name = metric.__class__.__name__.lower()
                if hasattr(results, metric_name):
                    scores[metric_name] = getattr(results, metric_name)

            return scores

        except Exception as e:
            print(f"Error in RAGAS evaluation: {e}")
            return {}

    def _evaluate_semantic_similarity(
        self, responses: List[str], expected: List[str]
    ) -> Dict[str, float]:
        """Evaluate using semantic similarity."""
        try:
            # Encode responses and expected
            response_embeddings = self._sentence_model.encode(responses)
            expected_embeddings = self._sentence_model.encode(expected)

            # Calculate cosine similarity
            similarities = []
            for i in range(len(responses)):
                similarity = cosine_similarity(
                    response_embeddings[i].reshape(1, -1),
                    expected_embeddings[i].reshape(1, -1),
                )[0][0]
                similarities.append(similarity)

            return {
                "semantic_similarity": statistics.mean(similarities),
                "relevance": statistics.mean(similarities),  # Use as relevance proxy
            }

        except Exception as e:
            print(f"Error in semantic similarity evaluation: {e}")
            return {}

    async def _evaluate_with_llm(
        self, prompts: List[str], responses: List[str], expected: List[str]
    ) -> Dict[str, float]:
        """Evaluate using LLM-based scoring."""
        try:
            scores = {
                "accuracy": [],
                "relevance": [],
                "coherence": [],
                "completeness": [],
            }

            for i, (prompt, response, expected_resp) in enumerate(
                zip(prompts, responses, expected)
            ):
                # Create evaluation prompt
                eval_prompt = f"""
                Please evaluate the following response on a scale of 0-1 for each metric:

                Prompt: {prompt}
                Response: {response}
                Expected: {expected_resp}

                Rate each metric (0-1):
                - Accuracy: How correct is the response?
                - Relevance: How well does it address the prompt?
                - Coherence: How well-structured and logical is it?
                - Completeness: How thorough is the response?

                Respond in JSON format:
                {{"accuracy": 0.8, "relevance": 0.9, "coherence": 0.7, "completeness": 0.8}}
                """

                # Get evaluation from LLM
                eval_response = await self._evaluator_llm.ainvoke(eval_prompt)

                try:
                    eval_scores = json.loads(eval_response.content)
                    for metric in scores:
                        if metric in eval_scores:
                            scores[metric].append(eval_scores[metric])
                except json.JSONDecodeError:
                    continue

            # Calculate averages
            return {
                metric: statistics.mean(values) if values else 0.0
                for metric, values in scores.items()
            }

        except Exception as e:
            print(f"Error in LLM evaluation: {e}")
            return {}

    def _combine_scores(
        self,
        ragas_scores: Dict[str, float],
        semantic_scores: Dict[str, float],
        llm_scores: Dict[str, float],
    ) -> Dict[str, float]:
        """Combine scores from different evaluation methods."""
        combined = {}

        # Combine all available scores
        all_scores = [ragas_scores, semantic_scores, llm_scores]

        for score_dict in all_scores:
            for metric, score in score_dict.items():
                if metric not in combined:
                    combined[metric] = []
                combined[metric].append(score)

        # Calculate weighted averages
        final_scores = {}
        for metric, scores in combined.items():
            if scores:
                # Simple average (could be weighted based on method reliability)
                final_scores[metric] = statistics.mean(scores)

        return final_scores


class HumanEvaluator:
    """
    Human evaluation for subjective quality assessment.

    This class manages human evaluation workflows and calculates
    inter-rater reliability metrics.
    """

    def __init__(
        self,
        evaluators: List[str],
        evaluation_criteria: List[str] = None,
        rating_scale: int = 5,
    ):
        """
        Initialize human evaluator.

        Args:
            evaluators: List of evaluator names
            evaluation_criteria: List of criteria to evaluate
            rating_scale: Rating scale (1-5, 1-10, etc.)
        """
        self.evaluators = evaluators
        self.evaluation_criteria = evaluation_criteria or [
            "accuracy",
            "relevance",
            "coherence",
            "creativity",
        ]
        self.rating_scale = rating_scale
        self.evaluation_data = {}

    async def evaluate(
        self,
        prompts: List[str],
        responses: List[str],
        expected: List[str],
    ) -> HumanEvaluationResult:
        """
        Evaluate responses using human evaluators.

        Args:
            prompts: List of input prompts
            responses: List of generated responses
            expected: List of expected responses

        Returns:
            HumanEvaluationResult with human scores
        """
        start_time = time.time()

        # This would typically interface with a human evaluation platform
        # For now, we'll simulate human evaluation

        evaluator_scores = {}
        all_scores = []

        for evaluator in self.evaluators:
            evaluator_scores[evaluator] = {}

            for i, (prompt, response, expected_resp) in enumerate(
                zip(prompts, responses, expected)
            ):
                # Simulate human evaluation (in practice, this would be done by humans)
                scores = self._simulate_human_evaluation(
                    prompt, response, expected_resp
                )
                evaluator_scores[evaluator][f"item_{i}"] = scores
                all_scores.append(scores)

        # Calculate inter-rater reliability
        inter_rater_reliability = self._calculate_inter_rater_reliability(
            evaluator_scores
        )

        # Calculate average scores
        avg_scores = self._calculate_average_scores(all_scores)

        evaluation_time = time.time() - start_time

        return HumanEvaluationResult(
            accuracy=avg_scores.get("accuracy", 0.0),
            relevance=avg_scores.get("relevance", 0.0),
            coherence=avg_scores.get("coherence", 0.0),
            completeness=avg_scores.get("completeness", 0.0),
            creativity=avg_scores.get("creativity", 0.0),
            aesthetics=avg_scores.get("aesthetics", 0.0),
            inter_rater_reliability=inter_rater_reliability,
            avg_human_score=statistics.mean(list(avg_scores.values())),
            evaluator_scores=evaluator_scores,
            evaluation_time=evaluation_time,
        )

    def _simulate_human_evaluation(
        self, prompt: str, response: str, expected: str
    ) -> Dict[str, float]:
        """Simulate human evaluation (replace with actual human evaluation)."""
        # This is a placeholder - in practice, this would be done by human evaluators
        import random

        scores = {}
        for criterion in self.evaluation_criteria:
            # Simulate realistic human scores with some variance
            base_score = random.uniform(0.6, 0.9)
            scores[criterion] = round(base_score, 2)

        return scores

    def _calculate_inter_rater_reliability(
        self, evaluator_scores: Dict[str, Dict[str, Dict[str, float]]]
    ) -> float:
        """Calculate inter-rater reliability (Cronbach's alpha)."""
        # Simplified calculation - in practice, use proper statistical methods
        all_scores = []

        for evaluator, items in evaluator_scores.items():
            evaluator_scores_list = []
            for item, scores in items.items():
                evaluator_scores_list.append(statistics.mean(list(scores.values())))
            all_scores.append(evaluator_scores_list)

        if len(all_scores) < 2:
            return 0.0

        # Calculate correlation between evaluators
        correlations = []
        for i in range(len(all_scores)):
            for j in range(i + 1, len(all_scores)):
                if len(all_scores[i]) == len(all_scores[j]):
                    if SEMANTIC_AVAILABLE:
                        correlation = np.corrcoef(all_scores[i], all_scores[j])[0, 1]
                        if not np.isnan(correlation):
                            correlations.append(correlation)
                    else:
                        # Simple correlation calculation without numpy
                        correlation = self._simple_correlation(
                            all_scores[i], all_scores[j]
                        )
                        correlations.append(correlation)

        return statistics.mean(correlations) if correlations else 0.0

    def _simple_correlation(self, x: List[float], y: List[float]) -> float:
        """Simple correlation calculation without numpy."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0

        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        sum_y2 = sum(y[i] ** 2 for i in range(n))

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x**2) * (n * sum_y2 - sum_y**2)) ** 0.5

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _calculate_average_scores(
        self, all_scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate average scores across all evaluations."""
        if not all_scores:
            return {}

        avg_scores = {}
        for criterion in self.evaluation_criteria:
            scores = [score_dict.get(criterion, 0.0) for score_dict in all_scores]
            avg_scores[criterion] = statistics.mean(scores)

        return avg_scores


class HybridEvaluator:
    """
    Hybrid evaluation combining automated and human methods.

    This class combines automated evaluation with human evaluation
    to provide comprehensive quality assessment.
    """

    def __init__(
        self,
        automated_metrics: List[str] = None,
        human_metrics: List[str] = None,
        weight_automated: float = 0.7,
        weight_human: float = 0.3,
        evaluators: List[str] = None,
    ):
        """
        Initialize hybrid evaluator.

        Args:
            automated_metrics: Metrics to evaluate automatically
            human_metrics: Metrics to evaluate with humans
            weight_automated: Weight for automated scores
            weight_human: Weight for human scores
            evaluators: List of human evaluators
        """
        self.automated_metrics = automated_metrics or ["accuracy", "relevance"]
        self.human_metrics = human_metrics or ["creativity", "aesthetics"]
        self.weight_automated = weight_automated
        self.weight_human = weight_human

        # Initialize sub-evaluators
        self.automated_evaluator = AutomatedEvaluator(self.automated_metrics)
        self.human_evaluator = HumanEvaluator(
            evaluators or ["expert1", "expert2"], self.human_metrics
        )

    async def evaluate(
        self,
        prompts: List[str],
        responses: List[str],
        expected: List[str],
        contexts: Optional[List[List[str]]] = None,
    ) -> HybridEvaluationResult:
        """
        Evaluate responses using hybrid method.

        Args:
            prompts: List of input prompts
            responses: List of generated responses
            expected: List of expected responses
            contexts: Optional list of context for each prompt

        Returns:
            HybridEvaluationResult with hybrid scores
        """
        start_time = time.time()

        # Run automated evaluation
        automated_result = await self.automated_evaluator.evaluate(
            prompts, responses, expected, contexts
        )

        # Run human evaluation
        human_result = await self.human_evaluator.evaluate(prompts, responses, expected)

        # Combine results
        hybrid_scores = self._combine_evaluation_results(automated_result, human_result)

        evaluation_time = time.time() - start_time

        return HybridEvaluationResult(
            accuracy=hybrid_scores.get("accuracy", 0.0),
            relevance=hybrid_scores.get("relevance", 0.0),
            coherence=hybrid_scores.get("coherence", 0.0),
            completeness=hybrid_scores.get("completeness", 0.0),
            creativity=hybrid_scores.get("creativity", 0.0),
            aesthetics=hybrid_scores.get("aesthetics", 0.0),
            automated_score=automated_result.overall_score,
            human_score=human_result.overall_score,
            hybrid_score=hybrid_scores.get("overall", 0.0),
            weight_automated=self.weight_automated,
            weight_human=self.weight_human,
            evaluation_time=evaluation_time,
        )

    def _combine_evaluation_results(
        self, automated_result: EvaluationResult, human_result: HumanEvaluationResult
    ) -> Dict[str, float]:
        """Combine automated and human evaluation results."""
        combined = {}

        # Combine metrics that exist in both
        all_metrics = set(automated_result.__dict__.keys()) | set(
            human_result.__dict__.keys()
        )

        for metric in all_metrics:
            if metric in [
                "evaluation_time",
                "timestamp",
                "inter_rater_reliability",
                "avg_human_score",
                "evaluator_scores",
                "automated_score",
                "human_score",
                "hybrid_score",
                "weight_automated",
                "weight_human",
            ]:
                continue

            automated_score = getattr(automated_result, metric, None)
            human_score = getattr(human_result, metric, None)

            if automated_score is not None and human_score is not None:
                # Weighted combination
                combined[metric] = (
                    automated_score * self.weight_automated
                    + human_score * self.weight_human
                )
            elif automated_score is not None:
                combined[metric] = automated_score
            elif human_score is not None:
                combined[metric] = human_score

        # Calculate overall hybrid score
        if combined:
            combined["overall"] = statistics.mean(list(combined.values()))

        return combined
