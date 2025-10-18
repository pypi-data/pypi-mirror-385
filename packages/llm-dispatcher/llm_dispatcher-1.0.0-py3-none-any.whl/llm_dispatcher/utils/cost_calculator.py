"""
Cost calculator for LLM usage optimization.

This module provides cost calculation and optimization utilities for
intelligent LLM switching based on economic efficiency.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os


@dataclass
class CostBreakdown:
    """Detailed cost breakdown for an LLM request."""

    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    cost_per_token: float
    model: str
    provider: str
    timestamp: datetime


class CostCalculator:
    """
    Calculates and optimizes costs for LLM usage.

    This class provides cost calculation, optimization suggestions,
    and budget tracking for intelligent LLM switching.
    """

    def __init__(self):
        self.cost_history: List[CostBreakdown] = []
        self.daily_budgets: Dict[str, float] = {}
        self.monthly_budgets: Dict[str, float] = {}

        # Current pricing data (as of 2025)
        self.pricing_data = {
            "openai": {
                "gpt-4": {"input": 0.03, "output": 0.06},
                "gpt-4-turbo": {"input": 0.01, "output": 0.03},
                "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
                "gpt-4o": {"input": 0.005, "output": 0.015},
                "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            },
            "anthropic": {
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015},
                "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            },
            "google": {
                "gemini-2.5-pro": {"input": 0.00125, "output": 0.005},
                "gemini-2.5-flash": {"input": 0.000075, "output": 0.0003},
                "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
                "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            },
            "xai": {"grok-3-beta": {"input": 0.02, "output": 0.04}},
        }

    def calculate_cost(
        self, provider: str, model: str, input_tokens: int, output_tokens: int
    ) -> CostBreakdown:
        """Calculate detailed cost breakdown for a request."""

        pricing = self.pricing_data.get(provider, {}).get(model, {})
        if not pricing:
            # Default to zero cost if pricing not found
            pricing = {"input": 0.0, "output": 0.0}

        input_cost = (input_tokens / 1000) * pricing.get("input", 0.0)
        output_cost = (output_tokens / 1000) * pricing.get("output", 0.0)
        total_cost = input_cost + output_cost

        total_tokens = input_tokens + output_tokens
        cost_per_token = total_cost / total_tokens if total_tokens > 0 else 0.0

        breakdown = CostBreakdown(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            cost_per_token=cost_per_token,
            model=model,
            provider=provider,
            timestamp=datetime.now(),
        )

        self.cost_history.append(breakdown)
        return breakdown

    def get_cost_efficiency_score(
        self, provider: str, model: str, performance_score: float
    ) -> float:
        """
        Calculate cost efficiency score (performance per dollar).

        Args:
            provider: LLM provider name
            model: Model name
            performance_score: Performance score (0-1)

        Returns:
            Cost efficiency score (higher is better)
        """
        # Get average cost per token for the model
        pricing = self.pricing_data.get(provider, {}).get(model, {})
        if not pricing:
            return 0.0

        avg_cost_per_token = (
            pricing.get("input", 0.0) + pricing.get("output", 0.0)
        ) / 2

        if avg_cost_per_token == 0:
            return performance_score  # Free model

        # Cost efficiency = performance / cost
        cost_efficiency = performance_score / (avg_cost_per_token * 1000)  # Normalize
        return min(cost_efficiency, 10.0)  # Cap at 10 for normalization

    def get_optimal_model_for_budget(
        self,
        available_models: List[Tuple[str, str]],  # (provider, model)
        performance_scores: Dict[str, float],  # model -> score
        max_cost: float,
        estimated_tokens: int,
    ) -> Optional[Tuple[str, str]]:
        """
        Find the best model within budget constraints.

        Args:
            available_models: List of (provider, model) tuples
            performance_scores: Performance scores for each model
            max_cost: Maximum cost allowed
            estimated_tokens: Estimated token usage

        Returns:
            Best (provider, model) tuple within budget, or None
        """
        candidates = []

        for provider, model in available_models:
            # Calculate estimated cost
            pricing = self.pricing_data.get(provider, {}).get(model, {})
            if not pricing:
                continue

            # Estimate 70% input, 30% output tokens
            input_tokens = int(estimated_tokens * 0.7)
            output_tokens = int(estimated_tokens * 0.3)

            estimated_cost = (input_tokens / 1000) * pricing.get("input", 0.0) + (
                output_tokens / 1000
            ) * pricing.get("output", 0.0)

            if estimated_cost <= max_cost:
                performance = performance_scores.get(model, 0.0)
                cost_efficiency = self.get_cost_efficiency_score(
                    provider, model, performance
                )
                candidates.append((provider, model, cost_efficiency, estimated_cost))

        if not candidates:
            return None

        # Sort by cost efficiency (descending)
        candidates.sort(key=lambda x: x[2], reverse=True)
        return (candidates[0][0], candidates[0][1])

    def get_daily_spending(self, date: Optional[datetime] = None) -> float:
        """Get total spending for a specific day."""
        if date is None:
            date = datetime.now()

        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        daily_costs = [
            cost.total_cost
            for cost in self.cost_history
            if start_of_day <= cost.timestamp < end_of_day
        ]

        return sum(daily_costs)

    def get_monthly_spending(self, date: Optional[datetime] = None) -> float:
        """Get total spending for a specific month."""
        if date is None:
            date = datetime.now()

        start_of_month = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end_of_month = start_of_month.replace(year=date.year + 1, month=1)
        else:
            end_of_month = start_of_month.replace(month=date.month + 1)

        monthly_costs = [
            cost.total_cost
            for cost in self.cost_history
            if start_of_month <= cost.timestamp < end_of_month
        ]

        return sum(monthly_costs)

    def set_daily_budget(self, budget: float) -> None:
        """Set daily budget limit."""
        today = datetime.now().strftime("%Y-%m-%d")
        self.daily_budgets[today] = budget

    def set_monthly_budget(self, budget: float) -> None:
        """Set monthly budget limit."""
        month = datetime.now().strftime("%Y-%m")
        self.monthly_budgets[month] = budget

    def is_over_budget(self, cost: float) -> Tuple[bool, str]:
        """
        Check if adding this cost would exceed budget limits.

        Returns:
            (is_over_budget, reason)
        """
        current_daily = self.get_daily_spending()
        current_monthly = self.get_monthly_spending()

        today = datetime.now().strftime("%Y-%m-%d")
        month = datetime.now().strftime("%Y-%m")

        daily_budget = self.daily_budgets.get(today)
        monthly_budget = self.monthly_budgets.get(month)

        if daily_budget and (current_daily + cost) > daily_budget:
            return True, f"Would exceed daily budget of ${daily_budget:.2f}"

        if monthly_budget and (current_monthly + cost) > monthly_budget:
            return True, f"Would exceed monthly budget of ${monthly_budget:.2f}"

        return False, ""

    def get_cost_summary(self) -> Dict[str, any]:
        """Get comprehensive cost summary."""
        if not self.cost_history:
            return {"total_cost": 0.0, "total_requests": 0}

        total_cost = sum(cost.total_cost for cost in self.cost_history)
        total_requests = len(self.cost_history)

        # Cost by provider
        provider_costs = {}
        for cost in self.cost_history:
            provider_costs[cost.provider] = (
                provider_costs.get(cost.provider, 0.0) + cost.total_cost
            )

        # Cost by model
        model_costs = {}
        for cost in self.cost_history:
            model_key = f"{cost.provider}:{cost.model}"
            model_costs[model_key] = model_costs.get(model_key, 0.0) + cost.total_cost

        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "average_cost_per_request": total_cost / total_requests,
            "daily_spending": self.get_daily_spending(),
            "monthly_spending": self.get_monthly_spending(),
            "provider_costs": provider_costs,
            "model_costs": model_costs,
            "cost_history_count": len(self.cost_history),
        }

    def export_cost_data(self, filepath: str) -> None:
        """Export cost history to JSON file."""
        data = {
            "cost_history": [
                {
                    "input_tokens": cost.input_tokens,
                    "output_tokens": cost.output_tokens,
                    "input_cost": cost.input_cost,
                    "output_cost": cost.output_cost,
                    "total_cost": cost.total_cost,
                    "cost_per_token": cost.cost_per_token,
                    "model": cost.model,
                    "provider": cost.provider,
                    "timestamp": cost.timestamp.isoformat(),
                }
                for cost in self.cost_history
            ],
            "daily_budgets": self.daily_budgets,
            "monthly_budgets": self.monthly_budgets,
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def import_cost_data(self, filepath: str) -> None:
        """Import cost history from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.cost_history = [
            CostBreakdown(
                input_tokens=item["input_tokens"],
                output_tokens=item["output_tokens"],
                input_cost=item["input_cost"],
                output_cost=item["output_cost"],
                total_cost=item["total_cost"],
                cost_per_token=item["cost_per_token"],
                model=item["model"],
                provider=item["provider"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
            )
            for item in data.get("cost_history", [])
        ]

        self.daily_budgets = data.get("daily_budgets", {})
        self.monthly_budgets = data.get("monthly_budgets", {})
