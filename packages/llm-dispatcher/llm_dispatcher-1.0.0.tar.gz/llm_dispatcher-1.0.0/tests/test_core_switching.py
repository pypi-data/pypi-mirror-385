"""
Tests for core switching engine functionality.

This module contains comprehensive tests for the LLM switching engine,
including decision making, fallback chains, and performance optimization.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from llm_dispatcher.core.base import (
    TaskType, Capability, TaskRequest, TaskResponse, ModelInfo, PerformanceMetrics
)
from llm_dispatcher.core.switch_engine import LLMSwitch, SwitchDecision
from llm_dispatcher.config.settings import SwitchConfig, OptimizationStrategy, FallbackStrategy
from llm_dispatcher.providers.base_provider import BaseProvider


class MockProvider(BaseProvider):
    """Mock provider for testing."""
    
    def __init__(self, provider_name: str, models: dict):
        super().__init__("mock_key", provider_name)
        self.models = models
        self.performance_metrics = {}
        
    def _initialize_models(self):
        pass  # Models set in constructor
        
    async def _make_api_call(self, request: TaskRequest, model: str) -> str:
        return f"Mock response from {self.provider_name}:{model}"
        
    async def _make_streaming_api_call(self, request: TaskRequest, model: str):
        yield f"Mock streaming response from {self.provider_name}:{model}"
        
    async def _make_embeddings_call(self, text: str, model: str) -> list:
        return [0.1] * 384  # Mock embedding


class TestLLMSwitch:
    """Test the LLM switching engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create mock providers
        self.openai_provider = MockProvider("openai", {
            "gpt-4": ModelInfo(
                name="gpt-4",
                provider="openai",
                capabilities=[Capability.TEXT, Capability.VISION],
                max_tokens=8192,
                cost_per_1k_tokens={"input": 0.03, "output": 0.06},
                context_window=128000,
                latency_ms=2000,
                benchmark_scores={"mmlu": 0.863, "human_eval": 0.674}
            )
        })
        
        self.anthropic_provider = MockProvider("anthropic", {
            "claude-3-sonnet": ModelInfo(
                name="claude-3-sonnet",
                provider="anthropic",
                capabilities=[Capability.TEXT, Capability.REASONING],
                max_tokens=4096,
                cost_per_1k_tokens={"input": 0.003, "output": 0.015},
                context_window=200000,
                latency_ms=1500,
                benchmark_scores={"mmlu": 0.812, "human_eval": 0.601}
            )
        })
        
        self.providers = {
            "openai": self.openai_provider,
            "anthropic": self.anthropic_provider
        }
        
        self.config = SwitchConfig()
        self.switch = LLMSwitch(self.providers, self.config)
    
    def test_switch_initialization(self):
        """Test switch engine initialization."""
        assert self.switch is not None
        assert len(self.switch.providers) == 2
        assert "openai" in self.switch.providers
        assert "anthropic" in self.switch.providers
    
    @pytest.mark.asyncio
    async def test_select_llm_basic(self):
        """Test basic LLM selection."""
        request = TaskRequest(
            prompt="Write a story about a robot",
            task_type=TaskType.TEXT_GENERATION
        )
        
        decision = await self.switch.select_llm(request)
        
        assert isinstance(decision, SwitchDecision)
        assert decision.provider in ["openai", "anthropic"]
        assert decision.model is not None
        assert 0 <= decision.confidence <= 1
        assert decision.reasoning is not None
        assert len(decision.fallback_options) > 0
    
    @pytest.mark.asyncio
    async def test_select_llm_with_constraints(self):
        """Test LLM selection with constraints."""
        request = TaskRequest(
            prompt="Write a story about a robot",
            task_type=TaskType.TEXT_GENERATION
        )
        
        constraints = {
            "max_cost": 0.01,
            "max_latency": 2000
        }
        
        decision = await self.switch.select_llm(request, constraints)
        
        assert decision.estimated_cost <= constraints["max_cost"]
        assert decision.estimated_latency <= constraints["max_latency"]
    
    @pytest.mark.asyncio
    async def test_task_specific_routing(self):
        """Test task-specific routing."""
        # Test reasoning task (should prefer Claude)
        reasoning_request = TaskRequest(
            prompt="Solve this complex logic problem",
            task_type=TaskType.REASONING
        )
        
        decision = await self.switch.select_llm(reasoning_request)
        
        # Should prefer providers with reasoning capability
        assert decision.provider in self.providers
    
    @pytest.mark.asyncio
    async def test_optimization_strategies(self):
        """Test different optimization strategies."""
        request = TaskRequest(
            prompt="Generate text",
            task_type=TaskType.TEXT_GENERATION
        )
        
        # Test cost optimization
        cost_config = SwitchConfig()
        cost_config.switching_rules.optimization_strategy = OptimizationStrategy.COST
        cost_switch = LLMSwitch(self.providers, cost_config)
        
        cost_decision = await cost_switch.select_llm(request)
        
        # Test performance optimization
        perf_config = SwitchConfig()
        perf_config.switching_rules.optimization_strategy = OptimizationStrategy.PERFORMANCE
        perf_switch = LLMSwitch(self.providers, perf_config)
        
        perf_decision = await perf_switch.select_llm(request)
        
        # Decisions should be different based on strategy
        assert cost_decision is not None
        assert perf_decision is not None
    
    @pytest.mark.asyncio
    async def test_execute_with_fallback(self):
        """Test execution with fallback."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )
        
        # Mock successful response
        with patch.object(self.openai_provider, 'generate') as mock_generate:
            mock_response = TaskResponse(
                content="Test response",
                model_used="gpt-4",
                provider="openai",
                tokens_used=100,
                cost=0.01,
                latency_ms=1500,
                finish_reason="stop"
            )
            mock_generate.return_value = mock_response
            
            response = await self.switch.execute_with_fallback(request)
            
            assert response is not None
            assert response.content == "Test response"
            assert response.provider == "openai"
    
    @pytest.mark.asyncio
    async def test_fallback_on_failure(self):
        """Test fallback when primary provider fails."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )
        
        # Mock primary provider failure and fallback success
        with patch.object(self.openai_provider, 'generate') as mock_openai, \
             patch.object(self.anthropic_provider, 'generate') as mock_anthropic:
            
            # Primary fails
            mock_openai.side_effect = Exception("API Error")
            
            # Fallback succeeds
            mock_response = TaskResponse(
                content="Fallback response",
                model_used="claude-3-sonnet",
                provider="anthropic",
                tokens_used=100,
                cost=0.005,
                latency_ms=1200,
                finish_reason="stop"
            )
            mock_anthropic.return_value = mock_response
            
            response = await self.switch.execute_with_fallback(request)
            
            assert response is not None
            assert response.provider == "anthropic"
            assert response.content == "Fallback response"
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test behavior when all providers fail."""
        request = TaskRequest(
            prompt="Test prompt",
            task_type=TaskType.TEXT_GENERATION
        )
        
        # Mock all providers to fail
        with patch.object(self.openai_provider, 'generate') as mock_openai, \
             patch.object(self.anthropic_provider, 'generate') as mock_anthropic:
            
            mock_openai.side_effect = Exception("OpenAI API Error")
            mock_anthropic.side_effect = Exception("Anthropic API Error")
            
            with pytest.raises(RuntimeError, match="All LLM options failed"):
                await self.switch.execute_with_fallback(request)
    
    def test_get_system_status(self):
        """Test system status reporting."""
        status = self.switch.get_system_status()
        
        assert "total_providers" in status
        assert "enabled_providers" in status
        assert "total_models" in status
        assert "optimization_strategy" in status
        assert "provider_health" in status
        
        assert status["total_providers"] == 2
        assert status["total_models"] == 2
    
    def test_update_config(self):
        """Test configuration updates."""
        new_config = SwitchConfig()
        new_config.switching_rules.optimization_strategy = OptimizationStrategy.SPEED
        
        self.switch.update_config(new_config)
        
        assert self.switch.config.switching_rules.optimization_strategy == OptimizationStrategy.SPEED
    
    def test_decision_weights(self):
        """Test decision weight management."""
        # Get default weights
        default_weights = self.switch.get_decision_weights()
        assert "performance" in default_weights
        assert "cost" in default_weights
        assert "latency" in default_weights
        
        # Set custom weights
        custom_weights = {
            "performance": 0.6,
            "cost": 0.3,
            "latency": 0.1
        }
        self.switch.set_decision_weights(custom_weights)
        
        updated_weights = self.switch.get_decision_weights()
        assert updated_weights["performance"] == 0.6
        assert updated_weights["cost"] == 0.3
        assert updated_weights["latency"] == 0.1


class TestSwitchDecision:
    """Test the SwitchDecision data structure."""
    
    def test_switch_decision_creation(self):
        """Test creating a switch decision."""
        decision = SwitchDecision(
            provider="openai",
            model="gpt-4",
            confidence=0.95,
            reasoning="Best performance for this task",
            estimated_cost=0.02,
            estimated_latency=1500,
            fallback_options=[("anthropic", "claude-3-sonnet")],
            decision_factors={"performance": 0.9, "cost": 0.8}
        )
        
        assert decision.provider == "openai"
        assert decision.model == "gpt-4"
        assert decision.confidence == 0.95
        assert decision.reasoning is not None
        assert decision.estimated_cost > 0
        assert decision.estimated_latency > 0
        assert len(decision.fallback_options) == 1


class TestPerformanceScoring:
    """Test performance scoring mechanisms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = MockProvider("test", {
            "test-model": ModelInfo(
                name="test-model",
                provider="test",
                capabilities=[Capability.TEXT],
                max_tokens=4096,
                cost_per_1k_tokens={"input": 0.01, "output": 0.02},
                context_window=8192,
                latency_ms=1000,
                benchmark_scores={"mmlu": 0.8, "human_eval": 0.7}
            )
        })
        
        # Add performance metrics
        self.provider.performance_metrics["test-model"] = PerformanceMetrics(
            mmlu_score=0.8,
            human_eval_score=0.7,
            latency_ms=1000,
            cost_efficiency=0.85
        )
    
    def test_get_performance_score(self):
        """Test performance score calculation."""
        score = self.provider.get_performance_score("test-model", TaskType.TEXT_GENERATION)
        assert 0 <= score <= 1
        assert score > 0
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        cost = self.provider.estimate_cost("test-model", 1000, 500)
        assert cost > 0
        assert cost == (1000/1000 * 0.01) + (500/1000 * 0.02)
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        tokens = self.provider.estimate_tokens("This is a test prompt with multiple words")
        assert tokens > 0
        assert isinstance(tokens, int)


if __name__ == "__main__":
    pytest.main([__file__])
