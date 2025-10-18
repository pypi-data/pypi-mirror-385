"""
Decorator system for intelligent LLM dispatching.

This module provides decorators that enable automatic LLM selection and dispatching
with minimal configuration and maximum ease of use.
"""

import asyncio
import functools
import inspect
from typing import Any, Callable, Dict, List, Optional, Union, TypeVar, cast
import logging

from ..core.base import TaskRequest, TaskType, TaskResponse
from ..core.switch_engine import LLMSwitch, SwitchDecision
from ..config.settings import SwitchConfig, OptimizationStrategy
from ..providers.openai_provider import OpenAIProvider
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.google_provider import GoogleProvider
from ..providers.grok_provider import GrokProvider

logger = logging.getLogger(__name__)

# Global switch instance
_global_switch: Optional[LLMSwitch] = None

F = TypeVar("F", bound=Callable[..., Any])


class LLMSwitchDecorator:
    """
    Decorator class for intelligent LLM switching.

    This class provides the core functionality for decorating functions
    to enable automatic LLM selection and switching.
    """

    def __init__(
        self,
        task_type: Optional[TaskType] = None,
        optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
        max_cost: Optional[float] = None,
        max_latency: Optional[int] = None,
        fallback_enabled: bool = True,
        providers: Optional[List[str]] = None,
        model: Optional[str] = None,
        **kwargs,
    ):
        self.task_type = task_type
        self.optimization_strategy = optimization_strategy
        self.max_cost = max_cost
        self.max_latency = max_latency
        self.fallback_enabled = fallback_enabled
        self.providers = providers
        self.model = model
        self.kwargs = kwargs

    def __call__(self, func: F) -> F:
        """Apply the decorator to a function."""

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await self._execute_with_llm_dispatcher(func, args, kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(self._execute_with_llm_dispatcher(func, args, kwargs))

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    async def _execute_with_llm_dispatcher(
        self, func: Callable, args: tuple, kwargs: dict
    ) -> Any:
        """Execute function with LLM switching."""
        # Get global switch instance
        switch = get_global_switch()
        if not switch:
            raise RuntimeError(
                "LLM-Dispatcher not initialized. Call llm_dispatcher.init() first."
            )

        # Detect task type if not specified
        task_type = self.task_type or self._detect_task_type(func, args, kwargs)

        # Prepare request
        request = self._prepare_request(func, args, kwargs, task_type)

        # Set constraints
        constraints = self._get_constraints()

        try:
            # Execute with LLM switching
            if self.fallback_enabled:
                response = await switch.execute_with_fallback(request, constraints)
            else:
                decision = await switch.select_llm(request, constraints)
                provider = switch.providers[decision.provider]
                response = await provider.generate(request, decision.model)

            # Extract content and return
            return self._extract_result(response, func)

        except Exception as e:
            logger.error(f"LLM-Dispatcher execution failed: {e}")
            raise

    def _detect_task_type(self, func: Callable, args: tuple, kwargs: dict) -> TaskType:
        """Detect task type from function name and parameters."""
        func_name = func.__name__.lower()

        # Simple task type detection based on function name
        if any(
            keyword in func_name
            for keyword in ["generate", "write", "create", "compose"]
        ):
            return TaskType.TEXT_GENERATION
        elif any(
            keyword in func_name
            for keyword in ["code", "program", "script", "function"]
        ):
            return TaskType.CODE_GENERATION
        elif any(keyword in func_name for keyword in ["translate", "convert"]):
            return TaskType.TRANSLATION
        elif any(keyword in func_name for keyword in ["summarize", "summary"]):
            return TaskType.SUMMARIZATION
        elif any(keyword in func_name for keyword in ["answer", "question", "qa"]):
            return TaskType.QUESTION_ANSWERING
        elif any(keyword in func_name for keyword in ["classify", "categorize"]):
            return TaskType.CLASSIFICATION
        elif any(keyword in func_name for keyword in ["sentiment", "emotion"]):
            return TaskType.SENTIMENT_ANALYSIS
        elif any(keyword in func_name for keyword in ["image", "vision", "analyze"]):
            return TaskType.VISION_ANALYSIS
        elif any(keyword in func_name for keyword in ["audio", "transcribe", "speech"]):
            return TaskType.AUDIO_TRANSCRIPTION
        elif any(keyword in func_name for keyword in ["json", "xml", "structured"]):
            return TaskType.STRUCTURED_OUTPUT
        elif any(keyword in func_name for keyword in ["function", "tool", "call"]):
            return TaskType.FUNCTION_CALLING
        elif any(keyword in func_name for keyword in ["reason", "think", "analyze"]):
            return TaskType.REASONING
        elif any(keyword in func_name for keyword in ["math", "calculate", "solve"]):
            return TaskType.MATH
        else:
            return TaskType.TEXT_GENERATION  # Default

    def _prepare_request(
        self, func: Callable, args: tuple, kwargs: dict, task_type: TaskType
    ) -> TaskRequest:
        """Prepare TaskRequest from function call."""
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Extract prompt from arguments
        prompt = self._extract_prompt(bound_args.arguments)

        # Extract additional parameters
        temperature = bound_args.arguments.get("temperature", 0.7)
        max_tokens = bound_args.arguments.get("max_tokens")
        images = bound_args.arguments.get("images")
        audio = bound_args.arguments.get("audio")
        structured_output = bound_args.arguments.get("structured_output")
        functions = bound_args.arguments.get("functions")

        return TaskRequest(
            prompt=prompt,
            task_type=task_type,
            max_tokens=max_tokens,
            temperature=temperature,
            images=images,
            audio=audio,
            structured_output=structured_output,
            functions=functions,
            metadata={
                "function_name": func.__name__,
                "module": func.__module__,
                "decorator_kwargs": self.kwargs,
            },
        )

    def _extract_prompt(self, arguments: dict) -> str:
        """Extract prompt from function arguments."""
        # Common prompt parameter names
        prompt_params = ["prompt", "text", "input", "message", "query", "question"]

        for param in prompt_params:
            if param in arguments and arguments[param]:
                return str(arguments[param])

        # If no explicit prompt parameter, use the first string argument
        for value in arguments.values():
            if isinstance(value, str) and value.strip():
                return value

        # Fallback
        return "Please process this request."

    def _get_constraints(self) -> Dict[str, Any]:
        """Get constraints for LLM selection."""
        constraints = {}

        if self.max_cost is not None:
            constraints["max_cost"] = self.max_cost

        if self.max_latency is not None:
            constraints["max_latency"] = self.max_latency

        if self.providers:
            constraints["allowed_providers"] = self.providers

        if self.model:
            constraints["preferred_model"] = self.model

        return constraints

    def _extract_result(self, response: TaskResponse, func: Callable) -> Any:
        """Extract result from TaskResponse."""
        # Check if function expects a specific return type
        sig = inspect.signature(func)
        return_annotation = sig.return_annotation

        if return_annotation == str or return_annotation == inspect.Signature.empty:
            return response.content
        elif return_annotation == TaskResponse:
            return response
        elif return_annotation == dict:
            try:
                import json

                return json.loads(response.content)
            except:
                return {"content": response.content, "metadata": response.metadata}
        else:
            # Try to parse as the expected type
            try:
                return return_annotation(response.content)
            except:
                return response.content


def llm_dispatcher(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    fallback_enabled: bool = True,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    **kwargs,
) -> LLMSwitchDecorator:
    """
    Decorator for intelligent LLM switching.

    Args:
        task_type: Specific task type for the function
        optimization_strategy: Strategy for LLM selection
        max_cost: Maximum cost per request
        max_latency: Maximum latency in milliseconds
        fallback_enabled: Whether to enable automatic fallback
        providers: List of allowed providers
        model: Preferred model
        **kwargs: Additional parameters

    Returns:
        Decorator function

    Example:
        @llm_dispatcher(task_type=TaskType.CODE_GENERATION)
        def generate_code(description: str) -> str:
            return description
    """
    return LLMSwitchDecorator(
        task_type=task_type,
        optimization_strategy=optimization_strategy,
        max_cost=max_cost,
        max_latency=max_latency,
        fallback_enabled=fallback_enabled,
        providers=providers,
        model=model,
        **kwargs,
    )


def route(
    task_type: TaskType,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    **kwargs,
) -> LLMSwitchDecorator:
    """
    Decorator for routing specific task types to optimal LLMs.

    Args:
        task_type: Task type to route
        optimization_strategy: Strategy for LLM selection
        **kwargs: Additional parameters

    Returns:
        Decorator function

    Example:
        @route(TaskType.VISION_ANALYSIS)
        def analyze_image(image_path: str) -> dict:
            return {"analysis": "Image processed"}
    """
    return LLMSwitchDecorator(
        task_type=task_type, optimization_strategy=optimization_strategy, **kwargs
    )


def init(
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    google_api_key: Optional[str] = None,
    grok_api_key: Optional[str] = None,
    config: Optional[SwitchConfig] = None,
    **provider_kwargs,
) -> LLMSwitch:
    """
    Initialize the global LLM-Dispatcher instance.

    Args:
        openai_api_key: OpenAI API key
        anthropic_api_key: Anthropic API key
        google_api_key: Google API key
        grok_api_key: Grok API key
        config: Switch configuration
        **provider_kwargs: Additional provider configuration

    Returns:
        Initialized LLMSwitch instance

    Example:
        llm_dispatcher.init(
            openai_api_key="sk-...",
            anthropic_api_key="sk-ant-...",
            google_api_key="...",
            grok_api_key="..."
        )
    """
    global _global_switch

    providers = {}

    # Initialize providers
    if openai_api_key:
        providers["openai"] = OpenAIProvider(
            openai_api_key, **provider_kwargs.get("openai", {})
        )

    if anthropic_api_key:
        providers["anthropic"] = AnthropicProvider(
            anthropic_api_key, **provider_kwargs.get("anthropic", {})
        )

    if google_api_key:
        providers["google"] = GoogleProvider(
            google_api_key, **provider_kwargs.get("google", {})
        )

    if grok_api_key:
        providers["grok"] = GrokProvider(
            grok_api_key, **provider_kwargs.get("grok", {})
        )

    if not providers:
        raise ValueError("At least one provider API key must be provided")

    # Create switch instance
    _global_switch = LLMSwitch(providers, config)

    logger.info(f"LLM-Dispatcher initialized with providers: {list(providers.keys())}")
    return _global_switch


def get_global_switch() -> Optional[LLMSwitch]:
    """Get the global LLM-Dispatcher instance."""
    return _global_switch


def set_global_switch(switch: LLMSwitch) -> None:
    """Set the global LLM-Dispatcher instance."""
    global _global_switch
    _global_switch = switch


# Convenience functions for common use cases
def for_text_generation(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for text generation tasks."""
    return llm_dispatcher(task_type=TaskType.TEXT_GENERATION, **kwargs)


def for_code_generation(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for code generation tasks."""
    return llm_dispatcher(task_type=TaskType.CODE_GENERATION, **kwargs)


def for_reasoning(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for reasoning tasks."""
    return llm_dispatcher(task_type=TaskType.REASONING, **kwargs)


def for_vision(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for vision tasks."""
    return llm_dispatcher(task_type=TaskType.VISION_ANALYSIS, **kwargs)


def for_math(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for math tasks."""
    return llm_dispatcher(task_type=TaskType.MATH, **kwargs)


def cost_optimized(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for cost efficiency."""
    return llm_dispatcher(optimization_strategy=OptimizationStrategy.COST, **kwargs)


def speed_optimized(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for speed."""
    return llm_dispatcher(optimization_strategy=OptimizationStrategy.SPEED, **kwargs)


def performance_optimized(**kwargs) -> LLMSwitchDecorator:
    """Decorator optimized for performance."""
    return llm_dispatcher(
        optimization_strategy=OptimizationStrategy.PERFORMANCE, **kwargs
    )


def _detect_task_type(func: Callable, args: tuple, kwargs: dict) -> TaskType:
    """Standalone function to detect task type from function name and parameters."""
    func_name = func.__name__.lower()

    # Simple task type detection based on function name
    if any(
        keyword in func_name for keyword in ["generate", "write", "create", "compose"]
    ):
        return TaskType.TEXT_GENERATION
    elif any(
        keyword in func_name for keyword in ["code", "program", "script", "function"]
    ):
        return TaskType.CODE_GENERATION
    elif any(keyword in func_name for keyword in ["translate", "convert"]):
        return TaskType.TRANSLATION
    elif any(keyword in func_name for keyword in ["summarize", "summary"]):
        return TaskType.SUMMARIZATION
    elif any(keyword in func_name for keyword in ["answer", "question", "qa"]):
        return TaskType.QUESTION_ANSWERING
    elif any(keyword in func_name for keyword in ["classify", "categorize"]):
        return TaskType.CLASSIFICATION
    elif any(keyword in func_name for keyword in ["sentiment", "emotion"]):
        return TaskType.SENTIMENT_ANALYSIS
    elif any(keyword in func_name for keyword in ["image", "vision", "analyze"]):
        return TaskType.VISION_ANALYSIS
    elif any(keyword in func_name for keyword in ["audio", "transcribe", "speech"]):
        return TaskType.AUDIO_TRANSCRIPTION
    elif any(keyword in func_name for keyword in ["json", "xml", "structured"]):
        return TaskType.STRUCTURED_OUTPUT
    elif any(keyword in func_name for keyword in ["function", "tool", "call"]):
        return TaskType.FUNCTION_CALLING
    elif any(keyword in func_name for keyword in ["reason", "think", "analyze"]):
        return TaskType.REASONING
    elif any(keyword in func_name for keyword in ["math", "calculate", "solve"]):
        return TaskType.MATH
    else:
        return TaskType.TEXT_GENERATION  # Default


def _prepare_request(
    func: Callable, args: tuple, kwargs: dict, task_type: TaskType
) -> TaskRequest:
    """Standalone function to prepare TaskRequest from function call."""
    # Get function signature
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()

    # Extract prompt from arguments
    prompt = _extract_prompt(bound_args.arguments)

    # Extract additional parameters
    temperature = bound_args.arguments.get("temperature", 0.7)
    max_tokens = bound_args.arguments.get("max_tokens")
    images = bound_args.arguments.get("images")
    audio = bound_args.arguments.get("audio")
    structured_output = bound_args.arguments.get("structured_output")
    functions = bound_args.arguments.get("functions")

    return TaskRequest(
        prompt=prompt,
        task_type=task_type,
        max_tokens=max_tokens,
        temperature=temperature,
        images=images,
        audio=audio,
        structured_output=structured_output,
        functions=functions,
        metadata={
            "function_name": func.__name__,
            "module": func.__module__,
        },
    )


def _extract_prompt(arguments: dict) -> str:
    """Standalone function to extract prompt from function arguments."""
    # Common prompt parameter names
    prompt_params = ["prompt", "text", "input", "message", "query", "question"]

    for param in prompt_params:
        if param in arguments and arguments[param]:
            return str(arguments[param])

    # If no explicit prompt parameter, use the first string argument
    for value in arguments.values():
        if isinstance(value, str) and value.strip():
            return value

    # Fallback
    return "Please process this request."


def llm_stream(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    chunk_callback: Optional[callable] = None,
    metadata_callback: Optional[callable] = None,
    **kwargs,
) -> Callable[[F], F]:
    """
    Decorator for streaming LLM responses.

    Args:
        task_type: Type of task (auto-detected if not provided)
        optimization_strategy: Strategy for optimization (cost, speed, balanced)
        max_cost: Maximum cost per request
        max_latency: Maximum latency in milliseconds
        providers: List of preferred providers
        model: Specific model to use
        chunk_callback: Optional callback for processing chunks
        metadata_callback: Optional callback for receiving metadata
        **kwargs: Additional configuration options

    Returns:
        Decorated function that yields streaming responses

    Example:
        @llm_stream(task_type=TaskType.TEXT_GENERATION)
        async def stream_text(prompt: str):
            async for chunk in _stream_generator():
                yield chunk
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def streaming_wrapper(*args, **kwargs):
            # Get global switch instance
            switch = get_global_switch()
            if not switch:
                raise RuntimeError(
                    "LLM-Dispatcher not initialized. Call llm_dispatcher.init() first."
                )

            # Detect task type if not specified
            detected_task_type = task_type or _detect_task_type(func, args, kwargs)

            # Prepare request
            request = _prepare_request(func, args, kwargs, detected_task_type)

            # Set constraints
            constraints = {
                "max_cost": max_cost,
                "max_latency": max_latency,
                "allowed_providers": providers,
                "preferred_model": model,
            }
            constraints = {k: v for k, v in constraints.items() if v is not None}

            try:
                # Execute streaming
                async for chunk in switch.execute_stream(
                    request, chunk_callback, metadata_callback, constraints
                ):
                    yield chunk
            except Exception as e:
                logger.error(f"Streaming execution failed: {e}")
                raise

        return cast(F, streaming_wrapper)

    return decorator


def llm_stream_with_metadata(
    task_type: Optional[TaskType] = None,
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED,
    max_cost: Optional[float] = None,
    max_latency: Optional[int] = None,
    providers: Optional[List[str]] = None,
    model: Optional[str] = None,
    include_timing: bool = True,
    include_tokens: bool = True,
    **kwargs,
) -> Callable[[F], F]:
    """
    Decorator for streaming LLM responses with detailed metadata.

    Args:
        task_type: Type of task (auto-detected if not provided)
        optimization_strategy: Strategy for optimization (cost, speed, balanced)
        max_cost: Maximum cost per request
        max_latency: Maximum latency in milliseconds
        providers: List of preferred providers
        model: Specific model to use
        include_timing: Whether to include timing information
        include_tokens: Whether to include token estimation
        **kwargs: Additional configuration options

    Returns:
        Decorated function that yields streaming responses with metadata

    Example:
        @llm_stream_with_metadata(task_type=TaskType.TEXT_GENERATION)
        async def stream_text_with_metadata(prompt: str):
            async for metadata in _stream_generator():
                yield metadata
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def streaming_metadata_wrapper(*args, **kwargs):
            # Get global switch instance
            switch = get_global_switch()
            if not switch:
                raise RuntimeError(
                    "LLM-Dispatcher not initialized. Call llm_dispatcher.init() first."
                )

            # Detect task type if not specified
            detected_task_type = task_type or _detect_task_type(func, args, kwargs)

            # Prepare request
            request = _prepare_request(func, args, kwargs, detected_task_type)

            # Set constraints
            constraints = {
                "max_cost": max_cost,
                "max_latency": max_latency,
                "allowed_providers": providers,
                "preferred_model": model,
            }
            constraints = {k: v for k, v in constraints.items() if v is not None}

            try:
                # Execute streaming with metadata
                async for metadata in switch.execute_stream_with_metadata(
                    request, include_timing, include_tokens, constraints
                ):
                    yield metadata
            except Exception as e:
                logger.error(f"Streaming with metadata execution failed: {e}")
                raise

        return cast(F, streaming_metadata_wrapper)

    return decorator
