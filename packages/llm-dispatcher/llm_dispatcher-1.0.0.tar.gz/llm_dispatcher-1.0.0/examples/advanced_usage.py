"""
Advanced usage examples for LLM-Dispatcher.

This module demonstrates advanced features and use cases
for the LLM-Dispatcher package.
"""

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

import llm_dispatcher
from llm_dispatcher import (
    LLMSwitch,
    TaskType,
    OptimizationStrategy,
    llm_dispatcher,
    llm_stream,
    llm_stream_with_metadata,
)
from llm_dispatcher.multimodal import MultimodalAnalyzer, MediaValidator
from llm_dispatcher.monitoring import AnalyticsEngine, MonitoringDashboard
from llm_dispatcher.caching import CacheManager, SemanticCache


# Initialize the dispatcher
llm_dispatcher.init(
    openai_api_key="your-openai-key",
    anthropic_api_key="your-anthropic-key",
    google_api_key="your-google-key",
)


class AdvancedUsageExamples:
    """Advanced usage examples for LLM-Dispatcher."""

    def __init__(self):
        self.analytics = AnalyticsEngine()
        self.cache_manager = CacheManager(max_size_mb=200)
        self.semantic_cache = SemanticCache()
        self.dashboard = None

    async def setup_monitoring(self):
        """Setup comprehensive monitoring."""
        print("Setting up monitoring...")

        # Start cache manager
        self.cache_manager.start()

        # Initialize dashboard
        from llm_dispatcher.monitoring import MetricsCollector

        metrics_collector = MetricsCollector()
        self.dashboard = MonitoringDashboard(self.analytics, metrics_collector)
        await self.dashboard.start()

        print("Monitoring setup complete!")

    async def cleanup(self):
        """Cleanup resources."""
        if self.dashboard:
            await self.dashboard.stop()
        self.cache_manager.stop()

    # Example 1: Advanced Streaming with Callbacks
    async def streaming_with_callbacks_example(self):
        """Example of streaming with custom callbacks."""
        print("\n=== Streaming with Callbacks Example ===")

        @llm_stream(
            task_type=TaskType.TEXT_GENERATION,
            chunk_callback=self.process_chunk,
            metadata_callback=self.process_metadata,
        )
        async def stream_with_processing(prompt: str):
            async for chunk in _stream_generator():
                yield chunk

        # Custom chunk processing
        processed_chunks = []

        async for chunk in stream_with_processing("Write a short story about AI"):
            processed_chunks.append(chunk)
            print(chunk, end="", flush=True)

        print(f"\nProcessed {len(processed_chunks)} chunks")

    def process_chunk(self, chunk: str, chunk_index: int) -> str:
        """Process individual chunks."""
        # Example: Add chunk index for debugging
        return f"[{chunk_index}] {chunk}"

    def process_metadata(self, metadata: Dict[str, Any]):
        """Process metadata updates."""
        print(f"\nMetadata update: {metadata}")

    # Example 2: Multimodal Content Analysis
    async def multimodal_analysis_example(self):
        """Example of multimodal content analysis."""
        print("\n=== Multimodal Analysis Example ===")

        # Initialize multimodal components
        analyzer = MultimodalAnalyzer()
        validator = MediaValidator()

        # Simulate media data (in real usage, load actual files)
        media_data = {"image": b"fake_image_data", "audio": b"fake_audio_data"}

        # Validate media
        validation_results = {}
        for media_id, media_content in media_data.items():
            validation_results[media_id] = validator.validate_media(media_content)
            print(f"{media_id} validation: {validation_results[media_id].is_valid}")

        # Analyze multimodal content
        analysis = analyzer.analyze_multimodal_content(
            media_data,
            task_description="Analyze this multimodal content for objects, scenes, and audio features",
        )

        print(f"Analysis type: {analysis.analysis_type}")
        print(
            f"Recommended providers: {analysis.task_recommendation.recommended_providers}"
        )
        print(f"Optimal model: {analysis.task_recommendation.optimal_model}")
        print(f"Estimated cost: ${analysis.task_recommendation.estimated_cost:.4f}")
        print(f"Complexity level: {analysis.task_recommendation.complexity_level}")

    # Example 3: Performance Monitoring and Analytics
    async def performance_monitoring_example(self):
        """Example of comprehensive performance monitoring."""
        print("\n=== Performance Monitoring Example ===")

        # Record some sample requests
        providers = ["openai", "anthropic", "google"]
        models = ["gpt-4", "claude-3-opus", "gemini-2.5-pro"]

        for i in range(20):
            provider = providers[i % len(providers)]
            model = models[i % len(models)]

            await self.analytics.record_request(
                provider=provider,
                model=model,
                task_type="text_generation",
                success=True,
                latency_ms=1000 + (i * 50),
                cost=0.003 + (i * 0.001),
                tokens_used=100 + (i * 10),
                user_id=f"user_{i % 5}",
                session_id=f"session_{i // 5}",
            )

        # Generate performance report
        report = self.analytics.generate_performance_report()
        print(f"Total requests: {report.total_requests}")
        print(f"Success rate: {report.success_rate:.1%}")
        print(f"Average latency: {report.average_latency_ms:.0f}ms")
        print(f"Total cost: ${report.total_cost:.4f}")

        # Analyze usage patterns
        patterns = self.analytics.analyze_usage_patterns(days=1)
        print(f"Peak hours: {patterns.peak_hours}")
        print(f"Provider preferences: {patterns.provider_preferences}")

        # Assess system health
        health = self.analytics.assess_system_health()
        print(f"System health score: {health.overall_health_score:.2f}")
        print(f"Status: {health.status}")
        if health.issues:
            print(f"Issues: {health.issues}")
        if health.recommendations:
            print(f"Recommendations: {health.recommendations}")

    # Example 4: Advanced Caching Strategies
    async def advanced_caching_example(self):
        """Example of advanced caching strategies."""
        print("\n=== Advanced Caching Example ===")

        # Test regular caching
        @llm_dispatcher.llm_dispatcher()
        def cached_generation(prompt: str) -> str:
            return prompt

        # First call (cache miss)
        start_time = datetime.now()
        result1 = cached_generation("Explain quantum computing")
        first_call_time = (datetime.now() - start_time).total_seconds()

        # Second call (cache hit)
        start_time = datetime.now()
        result2 = cached_generation("Explain quantum computing")
        second_call_time = (datetime.now() - start_time).total_seconds()

        print(f"First call time: {first_call_time:.3f}s")
        print(f"Second call time: {second_call_time:.3f}s")
        print(f"Cache speedup: {first_call_time / second_call_time:.1f}x")

        # Test semantic caching
        similar_prompts = [
            "What is quantum computing?",
            "Can you explain quantum computing?",
            "How does quantum computing work?",
            "Tell me about quantum computers",
        ]

        for prompt in similar_prompts:
            # Check semantic cache
            similar_response = self.semantic_cache.find_best_similar_response(prompt)
            if similar_response:
                print(f"Found similar response for: {prompt[:30]}...")
            else:
                # Generate new response and cache it
                response = cached_generation(prompt)
                self.semantic_cache.add_to_semantic_cache(prompt, response)
                print(f"Generated and cached: {prompt[:30]}...")

        # Get cache statistics
        cache_stats = self.cache_manager.get_cache_stats()
        print(f"Cache hits: {cache_stats['hits']}")
        print(f"Cache misses: {cache_stats['misses']}")
        print(f"Cache hit rate: {cache_stats['hit_rate']:.1%}")

    # Example 5: Custom Provider Integration
    async def custom_provider_example(self):
        """Example of custom provider integration."""
        print("\n=== Custom Provider Example ===")

        from llm_dispatcher import LLMProvider, TaskRequest, TaskResponse

        class MockProvider(LLMProvider):
            def __init__(self, name: str, latency_ms: int = 100):
                super().__init__(name)
                self.latency_ms = latency_ms
                self.models = [f"{name}-model"]

            async def _make_api_call(self, request: TaskRequest) -> TaskResponse:
                # Simulate latency
                await asyncio.sleep(self.latency_ms / 1000.0)

                return TaskResponse(
                    content=f"Mock response from {self.name}",
                    model_used=f"{self.name}-model",
                    provider=self.name,
                    tokens_used=100,
                    cost=0.001,
                    latency_ms=self.latency_ms,
                    finish_reason="stop",
                )

            async def _make_streaming_api_call(self, request: TaskRequest):
                for i in range(3):
                    await asyncio.sleep(0.1)
                    yield f"chunk_{i}_from_{self.name}"

            async def _make_embeddings_call(self, text: str) -> List[float]:
                return [0.1, 0.2, 0.3] * 10  # 30-dimensional embedding

            def _initialize_models(self):
                pass

            def _initialize_performance_metrics(self):
                pass

        # Create custom providers
        fast_provider = MockProvider("fast", latency_ms=50)
        slow_provider = MockProvider("slow", latency_ms=500)

        # Create switch with custom providers
        switch = LLMSwitch(providers=[fast_provider, slow_provider])

        # Test provider selection
        request = TaskRequest(prompt="Test prompt", task_type=TaskType.TEXT_GENERATION)

        decision = switch.select_llm(request)
        print(f"Selected provider: {decision.provider}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Reasoning: {decision.reasoning}")

        # Execute request
        response = await switch.execute_with_fallback(request)
        print(f"Response: {response.content}")
        print(f"Latency: {response.latency_ms}ms")

    # Example 6: Batch Processing with Analytics
    async def batch_processing_example(self):
        """Example of batch processing with analytics."""
        print("\n=== Batch Processing Example ===")

        prompts = [
            "Explain machine learning",
            "Write a Python function to sort a list",
            "Summarize the benefits of renewable energy",
            "Translate 'Hello world' to Spanish",
            "Solve this math problem: 2x + 5 = 13",
        ]

        @llm_dispatcher.llm_dispatcher()
        def process_prompt(prompt: str) -> str:
            return prompt

        # Process prompts in parallel
        start_time = datetime.now()
        tasks = [process_prompt(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        total_time = (datetime.now() - start_time).total_seconds()

        print(f"Processed {len(prompts)} prompts in {total_time:.2f}s")
        print(f"Average time per prompt: {total_time / len(prompts):.2f}s")

        # Record batch metrics
        await self.analytics.record_system_event(
            event_type="batch_processing",
            severity="info",
            message=f"Processed {len(prompts)} prompts in {total_time:.2f}s",
            metadata={
                "prompt_count": len(prompts),
                "total_time": total_time,
                "average_time": total_time / len(prompts),
            },
        )

    # Example 7: Real-time Dashboard
    async def dashboard_example(self):
        """Example of real-time dashboard usage."""
        print("\n=== Dashboard Example ===")

        if not self.dashboard:
            print("Dashboard not initialized. Run setup_monitoring() first.")
            return

        # Get dashboard data
        dashboard_data = self.dashboard.get_dashboard_data()
        print(f"Dashboard running: {dashboard_data.get('is_running', False)}")

        # Generate summary report
        summary = await self.dashboard.generate_summary_report()
        print(f"System health: {summary['system_health']['status']}")
        print(f"Health score: {summary['system_health']['overall_score']:.2f}")

        # Export dashboard data
        export_data = await self.dashboard.export_dashboard_data()
        print(f"Exported dashboard data with {len(export_data)} sections")

    # Example 8: Error Handling and Recovery
    async def error_handling_example(self):
        """Example of error handling and recovery."""
        print("\n=== Error Handling Example ===")

        from llm_dispatcher import LLMProvider, TaskRequest, TaskResponse

        class UnreliableProvider(LLMProvider):
            def __init__(self, name: str, failure_rate: float = 0.3):
                super().__init__(name)
                self.failure_rate = failure_rate
                self.models = [f"{name}-model"]

            async def _make_api_call(self, request: TaskRequest) -> TaskResponse:
                import random

                if random.random() < self.failure_rate:
                    raise Exception(f"Simulated failure in {self.name}")

                return TaskResponse(
                    content=f"Success from {self.name}",
                    model_used=f"{name}-model",
                    provider=self.name,
                    tokens_used=100,
                    cost=0.001,
                    latency_ms=100,
                    finish_reason="stop",
                )

            async def _make_streaming_api_call(self, request: TaskRequest):
                if random.random() < self.failure_rate:
                    raise Exception(f"Streaming failure in {self.name}")

                for i in range(3):
                    yield f"chunk_{i}_from_{self.name}"

            async def _make_embeddings_call(self, text: str) -> List[float]:
                return [0.1] * 10

            def _initialize_models(self):
                pass

            def _initialize_performance_metrics(self):
                pass

        # Create unreliable providers
        unreliable1 = UnreliableProvider("unreliable1", failure_rate=0.5)
        unreliable2 = UnreliableProvider("unreliable2", failure_rate=0.3)
        reliable = UnreliableProvider("reliable", failure_rate=0.0)

        # Test with fallback
        switch = LLMSwitch(providers=[unreliable1, unreliable2, reliable])

        request = TaskRequest(
            prompt="Test reliability", task_type=TaskType.TEXT_GENERATION
        )

        # Try multiple requests to test fallback
        for i in range(5):
            try:
                response = await switch.execute_with_fallback(request)
                print(f"Request {i+1}: Success with {response.provider}")
            except Exception as e:
                print(f"Request {i+1}: Failed - {e}")

        # Test streaming with fallback
        try:
            async for chunk in switch.execute_stream(request):
                print(f"Streaming chunk: {chunk}")
        except Exception as e:
            print(f"Streaming failed: {e}")


async def main():
    """Run all advanced examples."""
    examples = AdvancedUsageExamples()

    try:
        await examples.setup_monitoring()

        # Run examples
        await examples.streaming_with_callbacks_example()
        await examples.multimodal_analysis_example()
        await examples.performance_monitoring_example()
        await examples.advanced_caching_example()
        await examples.custom_provider_example()
        await examples.batch_processing_example()
        await examples.dashboard_example()
        await examples.error_handling_example()

        print("\n=== All Examples Completed Successfully! ===")

    finally:
        await examples.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
