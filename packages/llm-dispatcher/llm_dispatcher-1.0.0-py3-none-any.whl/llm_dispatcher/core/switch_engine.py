"""
Core switching engine for intelligent LLM selection.

This module implements the main switching logic that makes intelligent decisions
about which LLM to use based on performance metrics, cost optimization, and other factors.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any, AsyncGenerator
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .base import (
    LLMProvider,
    TaskRequest,
    TaskResponse,
    TaskType,
    ModelInfo,
    PerformanceMetrics,
    Capability,
)
from ..utils.benchmark_manager import BenchmarkManager
from ..utils.cost_calculator import CostCalculator
from ..utils.performance_monitor import PerformanceMonitor
from ..config.settings import SwitchConfig, OptimizationStrategy, FallbackStrategy
from ..exceptions import (
    FallbackExhaustedError,
    NoAvailableProvidersError,
    CostLimitExceededError,
    ModelNotFoundError,
    ProviderError,
)

logger = logging.getLogger(__name__)


@dataclass
class SwitchDecision:
    """Represents a decision about which LLM to use."""

    provider: str
    model: str
    confidence: float
    reasoning: str
    estimated_cost: float
    estimated_latency: float
    fallback_options: List[Tuple[str, str]]  # (provider, model) pairs
    decision_factors: Dict[str, float]  # Individual factor scores


class LLMSwitch:
    """
    Main switching engine that intelligently selects LLMs based on various factors.

    This class provides the core intelligence for selecting the best LLM for each
    request based on performance metrics, cost optimization, and real-time factors.
    """

    def __init__(
        self, providers: Dict[str, LLMProvider], config: Optional[SwitchConfig] = None
    ):
        self.providers = providers
        self.config = config or SwitchConfig()
        self.benchmark_manager = BenchmarkManager()
        self.cost_calculator = CostCalculator()
        self.performance_monitor = PerformanceMonitor()

        # Decision weights based on optimization strategy
        self.weights = self._get_decision_weights()

        # Performance history
        self.performance_history: Dict[str, List[float]] = {}

        # Initialize fallback strategies
        self._initialize_fallback_strategies()

    def _get_decision_weights(self) -> Dict[str, float]:
        """Get decision weights based on optimization strategy."""
        strategy = self.config.switching_rules.optimization_strategy

        weight_configs = {
            OptimizationStrategy.PERFORMANCE: {
                "performance": 0.7,  # More aggressive performance focus
                "cost": 0.05,  # Minimize cost consideration
                "latency": 0.1,
                "availability": 0.1,
                "reliability": 0.05,
            },
            OptimizationStrategy.COST: {
                "performance": 0.05,  # Minimize performance consideration even more
                "cost": 0.8,  # Even more aggressive cost focus
                "latency": 0.1,
                "availability": 0.025,
                "reliability": 0.025,
            },
            OptimizationStrategy.SPEED: {
                "performance": 0.1,  # Minimize performance consideration
                "cost": 0.05,
                "latency": 0.7,  # Much more aggressive speed focus
                "availability": 0.1,
                "reliability": 0.05,
            },
            OptimizationStrategy.RELIABILITY: {
                "performance": 0.1,
                "cost": 0.05,
                "latency": 0.1,
                "availability": 0.3,
                "reliability": 0.45,  # More aggressive reliability focus
            },
            OptimizationStrategy.BALANCED: {
                "performance": 0.25,  # Slightly reduced to allow more differentiation
                "cost": 0.25,  # Increased cost weight
                "latency": 0.25,  # Increased latency weight
                "availability": 0.125,
                "reliability": 0.125,
            },
        }

        return weight_configs.get(
            strategy, weight_configs[OptimizationStrategy.BALANCED]
        )

    def _initialize_fallback_strategies(self) -> None:
        """Initialize fallback strategies based on configuration."""
        self.fallback_strategies = {
            FallbackStrategy.PERFORMANCE_PRIORITY: self._get_performance_fallback_chain,
            FallbackStrategy.COST_PRIORITY: self._get_cost_fallback_chain,
            FallbackStrategy.SPEED_PRIORITY: self._get_speed_fallback_chain,
            FallbackStrategy.RELIABILITY_PRIORITY: self._get_reliability_fallback_chain,
        }

    async def select_llm(
        self, request: TaskRequest, constraints: Optional[Dict[str, Any]] = None
    ) -> SwitchDecision:
        """
        Select the best LLM for the given request.

        Args:
            request: The task request
            constraints: Optional constraints (max_cost, max_latency, etc.)

        Returns:
            SwitchDecision with the selected LLM and reasoning
        """
        constraints = constraints or {}

        # Get candidate models
        candidates = await self._get_candidates(request, constraints)

        if not candidates:
            raise NoAvailableProvidersError("No suitable LLMs found for the request")

        # Score each candidate
        scored_candidates = []
        for provider_name, model_name in candidates:
            score, reasoning, factors = await self._score_candidate(
                provider_name, model_name, request, constraints
            )
            scored_candidates.append(
                (provider_name, model_name, score, reasoning, factors)
            )

        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[2], reverse=True)

        # Select the best option
        best_provider, best_model, best_score, best_reasoning, best_factors = (
            scored_candidates[0]
        )

        # Prepare fallback options
        fallback_options = [
            (provider, model) for provider, model, _, _, _ in scored_candidates[1:3]
        ]

        # Estimate cost and latency
        provider = self.providers[best_provider]
        estimated_cost = provider.estimate_cost(
            best_model,
            provider.estimate_tokens(request.prompt),
            provider.estimate_tokens(""),  # Rough estimate
        )

        estimated_latency = self._estimate_latency(best_provider, best_model, request)

        return SwitchDecision(
            provider=best_provider,
            model=best_model,
            confidence=best_score,
            reasoning=best_reasoning,
            estimated_cost=estimated_cost,
            estimated_latency=estimated_latency,
            fallback_options=fallback_options,
            decision_factors=best_factors,
        )

    async def _get_candidates(
        self, request: TaskRequest, constraints: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """Get candidate LLMs for the request."""
        candidates = []

        # Get preferred providers for this task type
        preferred_providers = self.config.switching_rules.task_routing.get(
            request.task_type.value, list(self.providers.keys())
        )

        for provider_name in preferred_providers:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]
            suitable_models = provider.get_models_for_task(request.task_type)

            for model_name in suitable_models:
                # Check constraints
                if self._meets_constraints(provider, model_name, constraints):
                    candidates.append((provider_name, model_name))

        return candidates

    def _meets_constraints(
        self, provider: LLMProvider, model: str, constraints: Dict[str, Any]
    ) -> bool:
        """Check if a model meets the given constraints."""
        # Check allowed providers constraint
        if "allowed_providers" in constraints:
            provider_name = getattr(
                provider,
                "provider_name",
                provider.__class__.__name__.lower().replace("provider", ""),
            )
            if provider_name not in constraints["allowed_providers"]:
                return False

        # Check preferred model constraint
        if "preferred_model" in constraints:
            if model != constraints["preferred_model"]:
                return False

        if "max_cost" in constraints:
            estimated_cost = provider.estimate_cost(
                model, provider.estimate_tokens(""), provider.estimate_tokens("")
            )
            if estimated_cost > constraints["max_cost"]:
                return False

        if "max_latency" in constraints:
            model_info = provider.get_model_info(model)
            if model_info and model_info.latency_ms:
                if model_info.latency_ms > constraints["max_latency"]:
                    return False

        if "required_capabilities" in constraints:
            model_info = provider.get_model_info(model)
            if model_info:
                required_caps = constraints["required_capabilities"]
                if not all(cap in model_info.capabilities for cap in required_caps):
                    return False

        # Check global constraints
        if self.config.switching_rules.max_latency_ms:
            model_info = provider.get_model_info(model)
            if model_info and model_info.latency_ms:
                if model_info.latency_ms > self.config.switching_rules.max_latency_ms:
                    return False

        if self.config.switching_rules.max_cost_per_request:
            estimated_cost = provider.estimate_cost(
                model, provider.estimate_tokens(""), provider.estimate_tokens("")
            )
            if estimated_cost > self.config.switching_rules.max_cost_per_request:
                return False

        return True

    async def _score_candidate(
        self,
        provider_name: str,
        model_name: str,
        request: TaskRequest,
        constraints: Dict[str, Any],
    ) -> Tuple[float, str, Dict[str, float]]:
        """Score a candidate LLM."""
        provider = self.providers[provider_name]
        model_info = provider.get_model_info(model_name)

        if not model_info:
            return 0.0, "Model not found", {}

        factors = {}
        reasoning_parts = []

        # Performance score
        perf_score = provider.get_performance_score(model_name, request.task_type)
        factors["performance"] = perf_score
        reasoning_parts.append(f"Performance: {perf_score:.2f}")

        # Cost score (lower is better, with better differentiation)
        estimated_cost = provider.estimate_cost(
            model_name,
            provider.estimate_tokens(request.prompt),
            provider.estimate_tokens(""),  # Rough estimate
        )
        # More aggressive cost scoring to differentiate models
        if estimated_cost == 0:
            cost_score = 1.0  # Free models get max score
        else:
            cost_score = max(0, 1 - (estimated_cost / 0.005))  # Normalize to 0.5¢ max
        factors["cost"] = cost_score
        reasoning_parts.append(f"Cost: ${estimated_cost:.4f}")

        # Latency score (lower is better, with better differentiation)
        latency = self._estimate_latency(provider_name, model_name, request)
        # More aggressive latency scoring
        if latency < 1000:  # Very fast
            latency_score = 1.0
        elif latency < 2000:  # Fast
            latency_score = 0.8
        elif latency < 3000:  # Medium
            latency_score = 0.6
        else:  # Slow
            latency_score = max(0, 1 - (latency / 10000))  # Normalize to 10s max
        factors["latency"] = latency_score
        reasoning_parts.append(f"Latency: {latency:.0f}ms")

        # Availability score (based on recent performance)
        availability_score = self._get_availability_score(provider_name, model_name)
        factors["availability"] = availability_score
        reasoning_parts.append(f"Availability: {availability_score:.2f}")

        # Reliability score (based on error rate)
        reliability_score = self._get_reliability_score(provider_name, model_name)
        factors["reliability"] = reliability_score
        reasoning_parts.append(f"Reliability: {reliability_score:.2f}")

        # Task-specific scoring bonus (reduced for cost optimization)
        task_bonus = self._get_task_specific_bonus(
            provider_name, model_name, request.task_type
        )

        # Reduce task bonus impact for cost optimization strategy
        if (
            self.config.switching_rules.optimization_strategy
            == OptimizationStrategy.COST
        ):
            task_bonus *= 0.3  # Reduce task bonus to 30% for cost optimization

        factors["task_bonus"] = task_bonus
        if task_bonus > 0:
            reasoning_parts.append(f"Task bonus: +{task_bonus:.2f}")

        # Calculate weighted score
        total_score = sum(
            factors[metric] * self.weights[metric] for metric in self.weights
        )

        # Add task bonus to total score
        total_score += task_bonus

        reasoning = f"Score: {total_score:.2f} ({', '.join(reasoning_parts)})"

        return total_score, reasoning, factors

    def _estimate_latency(
        self, provider_name: str, model_name: str, request: TaskRequest
    ) -> float:
        """Estimate latency for a request."""
        provider = self.providers[provider_name]
        model_info = provider.get_model_info(model_name)

        if not model_info or not model_info.latency_ms:
            return 1000  # Default estimate

        base_latency = model_info.latency_ms

        # Adjust based on input length
        input_tokens = provider.estimate_tokens(request.prompt)
        if input_tokens > 1000:
            base_latency *= 1.2
        if input_tokens > 5000:
            base_latency *= 1.5

        # Adjust based on task complexity
        if request.task_type in [
            TaskType.REASONING,
            TaskType.MATH,
            TaskType.CODE_GENERATION,
        ]:
            base_latency *= 1.3

        if request.images:
            base_latency *= 1.5  # Vision tasks take longer

        return base_latency

    def _get_availability_score(self, provider_name: str, model_name: str) -> float:
        """Get availability score based on recent performance."""
        key = f"{provider_name}:{model_name}"
        if key not in self.performance_history:
            return 0.8  # Default score

        recent_scores = self.performance_history[key][-10:]  # Last 10 requests
        if not recent_scores:
            return 0.8

        return sum(recent_scores) / len(recent_scores)

    def _get_reliability_score(self, provider_name: str, model_name: str) -> float:
        """Get reliability score based on error rate."""
        # Get from performance monitor if available
        try:
            stats = self.performance_monitor.get_performance_stats(
                provider_name, model_name
            )
            return stats.success_rate
        except:
            # Fallback to default scores
            reliability_scores = {"openai": 0.95, "anthropic": 0.93, "google": 0.90}
            return reliability_scores.get(provider_name, 0.85)

    async def execute_with_fallback(
        self, request: TaskRequest, constraints: Optional[Dict[str, Any]] = None
    ) -> TaskResponse:
        """
        Execute a request with automatic fallback if the primary LLM fails.
        """
        decision = await self.select_llm(request, constraints)
        fallback_decisions = [decision]  # Track all failed decisions

        # Try primary choice
        try:
            provider = self.providers[decision.provider]
            response = await provider.generate(request, decision.model)

            # Record performance
            self._record_performance(decision.provider, decision.model, 1.0)
            self.performance_monitor.record_request(
                decision.provider, decision.model, response.latency_ms, True
            )

            return response

        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}")

            # Try fallback options
            for fallback_provider, fallback_model in decision.fallback_options:
                try:
                    provider = self.providers[fallback_provider]
                    response = await provider.generate(request, fallback_model)

                    # Record performance
                    self._record_performance(fallback_provider, fallback_model, 0.8)
                    self.performance_monitor.record_request(
                        fallback_provider, fallback_model, response.latency_ms, True
                    )

                    logger.info(
                        f"Fallback successful: {fallback_provider}:{fallback_model}"
                    )
                    return response

                except Exception as fallback_error:
                    logger.warning(f"Fallback failed: {fallback_error}")
                    # Create a mock decision for tracking
                    from .base import LLMDecision

                    fallback_decision = LLMDecision(
                        provider=fallback_provider,
                        model=fallback_model,
                        confidence=0.0,
                        fallback_options=[],
                    )
                    fallback_decisions.append(fallback_decision)
                    continue

            # All options failed
            failed_providers = [decision.provider for decision in fallback_decisions]
            raise FallbackExhaustedError("All LLM options failed", failed_providers)

    async def execute_stream(
        self,
        request: TaskRequest,
        chunk_callback: Optional[callable] = None,
        metadata_callback: Optional[callable] = None,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Execute a request with streaming response.

        Args:
            request: The task request to execute
            chunk_callback: Optional callback for processing chunks
            metadata_callback: Optional callback for receiving metadata
            constraints: Optional constraints for LLM selection

        Yields:
            str: Streaming response chunks
        """
        decision = await self.select_llm(request, constraints)
        if not decision:
            raise NoAvailableProvidersError("No suitable LLM found for the request")

        fallback_decisions = [decision]  # Track all failed decisions
        provider = self._get_provider(decision.provider)
        if not provider:
            raise ModelNotFoundError(decision.model, decision.provider)

        start_time = time.time()
        total_tokens = 0
        chunk_count = 0

        try:
            async for chunk in provider.generate_stream(request, decision.model):
                chunk_count += 1

                # Process chunk through callback if provided
                if chunk_callback:
                    processed_chunk = chunk_callback(chunk, chunk_count)
                    if processed_chunk is not None:
                        chunk = processed_chunk

                yield chunk

                # Estimate tokens (rough approximation)
                if isinstance(chunk, str):
                    total_tokens += len(chunk.split())

                # Send metadata if callback provided
                if metadata_callback and chunk_count % 10 == 0:  # Every 10 chunks
                    metadata = {
                        "chunk_count": chunk_count,
                        "estimated_tokens": total_tokens,
                        "provider": decision.provider,
                        "model": decision.model,
                        "elapsed_time": time.time() - start_time,
                    }
                    metadata_callback(metadata)

            # Record final performance
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            input_tokens = provider.estimate_tokens(request.prompt)
            cost = provider.estimate_cost(
                decision.model, input_tokens, total_tokens - input_tokens
            )

            self._record_performance(
                decision.provider, decision.model, 1.0  # Success score
            )
            self.performance_monitor.record_request(
                decision.provider, decision.model, latency, True
            )

        except Exception as e:
            logger.error(f"Streaming execution failed: {e}")

            # Try fallback providers
            for fallback_provider, fallback_model in decision.fallback_options:
                try:
                    provider = self._get_provider(fallback_provider)
                    if provider:
                        logger.info(f"Trying fallback provider: {fallback_provider}")

                        # Reset counters for fallback
                        start_time = time.time()
                        total_tokens = 0
                        chunk_count = 0

                        async for chunk in provider.generate_stream(
                            request, decision.model
                        ):
                            chunk_count += 1

                            if chunk_callback:
                                processed_chunk = chunk_callback(chunk, chunk_count)
                                if processed_chunk is not None:
                                    chunk = processed_chunk

                            yield chunk

                            if isinstance(chunk, str):
                                total_tokens += len(chunk.split())

                        # Record fallback performance
                        end_time = time.time()
                        latency = (end_time - start_time) * 1000

                        self._record_performance(
                            fallback_provider,
                            fallback_model,
                            0.8,  # Fallback success score
                        )
                        self.performance_monitor.record_request(
                            fallback_provider, fallback_model, latency, True
                        )
                        return

                except Exception as fallback_error:
                    logger.warning(
                        f"Fallback provider {fallback_provider} also failed: {fallback_error}"
                    )
                    # Create a mock decision for tracking
                    from .base import LLMDecision

                    fallback_decision = LLMDecision(
                        provider=fallback_provider,
                        model=fallback_model,
                        confidence=0.0,
                        fallback_options=[],
                    )
                    fallback_decisions.append(fallback_decision)
                    continue

            failed_providers = [decision.provider] + [
                decision.provider for decision in fallback_decisions
            ]
            raise FallbackExhaustedError(
                f"All providers failed for streaming request: {e}", failed_providers
            )

    async def execute_stream_with_metadata(
        self,
        request: TaskRequest,
        include_timing: bool = True,
        include_tokens: bool = True,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute streaming request with detailed metadata.

        Args:
            request: The task request to execute
            include_timing: Whether to include timing information
            include_tokens: Whether to include token estimation
            constraints: Optional constraints for LLM selection

        Yields:
            Dict containing chunk data and metadata
        """
        decision = await self.select_llm(request, constraints)
        if not decision:
            raise NoAvailableProvidersError("No suitable LLM found for the request")

        fallback_decisions = [decision]  # Track all failed decisions
        provider = self._get_provider(decision.provider)
        if not provider:
            raise ModelNotFoundError(decision.model, decision.provider)

        start_time = time.time()
        total_tokens = 0
        chunk_count = 0

        try:
            async for chunk in provider.generate_stream(request, decision.model):
                chunk_count += 1

                metadata = {
                    "chunk": chunk,
                    "chunk_index": chunk_count,
                    "provider": decision.provider,
                    "model": decision.model,
                }

                if include_timing:
                    metadata["elapsed_time"] = time.time() - start_time

                if include_tokens and isinstance(chunk, str):
                    chunk_tokens = len(chunk.split())
                    total_tokens += chunk_tokens
                    metadata["chunk_tokens"] = chunk_tokens
                    metadata["total_tokens"] = total_tokens

                yield metadata

            # Final metadata
            end_time = time.time()
            final_metadata = {
                "chunk": None,  # Signal end of stream
                "chunk_index": chunk_count,
                "provider": decision.provider,
                "model": decision.model,
                "total_chunks": chunk_count,
                "total_tokens": total_tokens,
                "total_time": end_time - start_time,
                "finish_reason": "completed",
            }
            yield final_metadata

        except Exception as e:
            logger.error(f"Streaming execution failed: {e}")

            # Try fallback providers
            for fallback_provider, fallback_model in decision.fallback_options:
                try:
                    provider = self._get_provider(fallback_provider)
                    if provider:
                        logger.info(f"Trying fallback provider: {fallback_provider}")

                        # Reset for fallback
                        start_time = time.time()
                        total_tokens = 0
                        chunk_count = 0

                        async for chunk in provider.generate_stream(
                            request, decision.model
                        ):
                            chunk_count += 1

                            metadata = {
                                "chunk": chunk,
                                "chunk_index": chunk_count,
                                "provider": fallback_provider,
                                "model": fallback_model,
                            }

                            if include_timing:
                                metadata["elapsed_time"] = time.time() - start_time

                            if include_tokens and isinstance(chunk, str):
                                chunk_tokens = len(chunk.split())
                                total_tokens += chunk_tokens
                                metadata["chunk_tokens"] = chunk_tokens
                                metadata["total_tokens"] = total_tokens

                            yield metadata

                        # Final fallback metadata
                        end_time = time.time()
                        final_metadata = {
                            "chunk": None,
                            "chunk_index": chunk_count,
                            "provider": fallback_provider,
                            "model": fallback_model,
                            "total_chunks": chunk_count,
                            "total_tokens": total_tokens,
                            "total_time": end_time - start_time,
                            "finish_reason": "completed_fallback",
                        }
                        yield final_metadata
                        return

                except Exception as fallback_error:
                    logger.warning(
                        f"Fallback provider {fallback_provider} also failed: {fallback_error}"
                    )
                    # Create a mock decision for tracking
                    from .base import LLMDecision

                    fallback_decision = LLMDecision(
                        provider=fallback_provider,
                        model=fallback_model,
                        confidence=0.0,
                        fallback_options=[],
                    )
                    fallback_decisions.append(fallback_decision)
                    continue

            # Error metadata
            error_metadata = {
                "chunk": None,
                "chunk_index": chunk_count,
                "provider": decision.provider,
                "model": decision.model,
                "error": str(e),
                "finish_reason": "error",
            }
            yield error_metadata
            failed_providers = [decision.provider] + [
                decision.provider for decision in fallback_decisions
            ]
            raise FallbackExhaustedError(
                f"All providers failed for streaming request: {e}", failed_providers
            )

    def _record_performance(self, provider: str, model: str, score: float):
        """Record performance for a model."""
        key = f"{provider}:{model}"
        if key not in self.performance_history:
            self.performance_history[key] = []

        self.performance_history[key].append(score)

        # Keep only recent history
        if len(self.performance_history[key]) > 100:
            self.performance_history[key] = self.performance_history[key][-100:]

    def _get_performance_fallback_chain(
        self, task_type: TaskType
    ) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing performance."""
        rankings = self.benchmark_manager.get_task_performance_ranking(task_type)
        fallback_chain = []

        for model, score in rankings[:3]:
            # Find which provider has this model
            for provider_name, provider in self.providers.items():
                if model in provider.models:
                    fallback_chain.append((provider_name, model))
                    break

        return fallback_chain

    def _get_cost_fallback_chain(self, task_type: TaskType) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing cost efficiency."""
        cost_rankings = self.cost_calculator.get_cost_efficiency_ranking()
        fallback_chain = []

        for model, score in cost_rankings[:3]:
            # Find which provider has this model
            for provider_name, provider in self.providers.items():
                if model in provider.models:
                    fallback_chain.append((provider_name, model))
                    break

        return fallback_chain

    def _get_speed_fallback_chain(self, task_type: TaskType) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing speed."""
        speed_rankings = self.benchmark_manager.get_speed_ranking()
        fallback_chain = []

        for model, latency in speed_rankings[:3]:
            # Find which provider has this model
            for provider_name, provider in self.providers.items():
                if model in provider.models:
                    fallback_chain.append((provider_name, model))
                    break

        return fallback_chain

    def _get_reliability_fallback_chain(
        self, task_type: TaskType
    ) -> List[Tuple[str, str]]:
        """Get fallback chain prioritizing reliability."""
        reliability_rankings = self.benchmark_manager.get_reliability_ranking()
        fallback_chain = []

        for model, score in reliability_rankings[:3]:
            # Find which provider has this model
            for provider_name, provider in self.providers.items():
                if model in provider.models:
                    fallback_chain.append((provider_name, model))
                    break

        return fallback_chain

    def _get_provider(self, provider_name: str) -> Optional[LLMProvider]:
        """Get provider by name."""
        return self.providers.get(provider_name)

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and health."""
        status = {
            "total_providers": len(self.providers),
            "enabled_providers": len(
                [
                    p
                    for p in self.providers.values()
                    if hasattr(p, "enabled") and p.enabled
                ]
            ),
            "total_models": sum(len(p.models) for p in self.providers.values()),
            "optimization_strategy": self.config.switching_rules.optimization_strategy,
            "fallback_strategy": self.config.switching_rules.fallback_strategy,
            "provider_health": {},
            "performance_summary": self.performance_monitor.get_system_overview(),
        }

        # Get health status for each provider
        for provider_name, provider in self.providers.items():
            status["provider_health"][provider_name] = provider.get_health_status()

        return status

    def update_config(self, new_config: SwitchConfig) -> None:
        """Update the configuration."""
        self.config = new_config
        self.weights = self._get_decision_weights()
        self._initialize_fallback_strategies()

    def get_decision_weights(self) -> Dict[str, float]:
        """Get current decision weights."""
        return self.weights.copy()

    def set_decision_weights(self, weights: Dict[str, float]) -> None:
        """Set custom decision weights."""
        self.weights = weights.copy()

    def _get_task_specific_bonus(
        self, provider_name: str, model_name: str, task_type: TaskType
    ) -> float:
        """Get task-specific bonus score for a model."""
        provider = self.providers[provider_name]
        model_info = provider.get_model_info(model_name)

        if not model_info:
            return 0.0

        bonus = 0.0

        # Task-specific bonuses based on model capabilities and performance
        if task_type == TaskType.CODE_GENERATION:
            # Favor models with high code generation scores
            if "human_eval" in model_info.benchmark_scores:
                code_score = model_info.benchmark_scores["human_eval"]
                if code_score > 0.7:
                    bonus += 0.3
                elif code_score > 0.6:
                    bonus += 0.2
                elif code_score > 0.5:
                    bonus += 0.1

        elif task_type == TaskType.MATH:
            # Favor models with high math scores
            if "aime" in model_info.benchmark_scores:
                math_score = model_info.benchmark_scores["aime"]
                if math_score > 0.9:
                    bonus += 0.3
                elif math_score > 0.8:
                    bonus += 0.2
                elif math_score > 0.7:
                    bonus += 0.1

        elif task_type == TaskType.REASONING:
            # Favor models with high reasoning scores
            if "gpqa" in model_info.benchmark_scores:
                reasoning_score = model_info.benchmark_scores["gpqa"]
                if reasoning_score > 0.8:
                    bonus += 0.3
                elif reasoning_score > 0.7:
                    bonus += 0.2
                elif reasoning_score > 0.6:
                    bonus += 0.1

        elif task_type == TaskType.VISION_ANALYSIS:
            # Favor models with vision capabilities
            if Capability.VISION in model_info.capabilities:
                if "vqa" in model_info.benchmark_scores:
                    vision_score = model_info.benchmark_scores["vqa"]
                    if vision_score > 0.7:
                        bonus += 0.3
                    elif vision_score > 0.6:
                        bonus += 0.2
                else:
                    bonus += 0.1  # Has vision capability but no benchmark score

        elif task_type == TaskType.AUDIO_TRANSCRIPTION:
            # Favor models with audio capabilities
            if Capability.AUDIO in model_info.capabilities:
                if "speech_recognition" in model_info.benchmark_scores:
                    audio_score = model_info.benchmark_scores["speech_recognition"]
                    if audio_score > 0.9:
                        bonus += 0.3
                    elif audio_score > 0.8:
                        bonus += 0.2
                else:
                    bonus += 0.1  # Has audio capability but no benchmark score

        elif task_type == TaskType.TEXT_GENERATION:
            # Favor models with high general performance
            if "mmlu" in model_info.benchmark_scores:
                general_score = model_info.benchmark_scores["mmlu"]
                if general_score > 0.85:
                    bonus += 0.2
                elif general_score > 0.8:
                    bonus += 0.1

        # Provider-specific bonuses for certain tasks
        if provider_name == "openai" and task_type in [
            TaskType.CODE_GENERATION,
            TaskType.FUNCTION_CALLING,
        ]:
            bonus += 0.1  # OpenAI is generally good at code and function calling

        elif provider_name == "google" and task_type in [
            TaskType.REASONING,
            TaskType.MATH,
        ]:
            bonus += 0.1  # Google models are generally good at reasoning and math

        return min(
            bonus, 0.5
        )  # Cap the bonus at 0.5 to avoid overwhelming other factors
