"""
Token counting utilities for accurate cost estimation.

This module provides token counting functionality for different LLM providers
to ensure accurate cost estimation and context window management.
"""

from typing import Dict, List, Optional, Union
import tiktoken
import re
from abc import ABC, abstractmethod


class TokenCounter(ABC):
    """Abstract base class for token counters."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text."""
        pass

    @abstractmethod
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts."""
        pass

    @abstractmethod
    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        pass


class OpenAITokenCounter(TokenCounter):
    """Token counter for OpenAI models using tiktoken."""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base encoding for unknown models
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken encoding."""
        return len(self.encoding.encode(text))

    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts."""
        return [self.count_tokens(text) for text in texts]

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text

        truncated_tokens = tokens[:max_tokens]
        return self.encoding.decode(truncated_tokens)


class AnthropicTokenCounter(TokenCounter):
    """Token counter for Anthropic models."""

    def __init__(self):
        # Anthropic uses a different tokenization scheme
        # This is an approximation based on their documentation
        self.avg_chars_per_token = 4.0

    def count_tokens(self, text: str) -> int:
        """Estimate token count for Anthropic models."""
        # Anthropic's tokenization is similar to GPT-3.5
        # This is a rough approximation
        return int(len(text) / self.avg_chars_per_token)

    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts."""
        return [self.count_tokens(text) for text in texts]

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        estimated_tokens = self.count_tokens(text)
        if estimated_tokens <= max_tokens:
            return text

        # Truncate by character count
        max_chars = int(max_tokens * self.avg_chars_per_token)
        return text[:max_chars]


class GoogleTokenCounter(TokenCounter):
    """Token counter for Google models."""

    def __init__(self):
        # Google's tokenization is similar to SentencePiece
        self.avg_chars_per_token = 3.5

    def count_tokens(self, text: str) -> int:
        """Estimate token count for Google models."""
        # Google uses SentencePiece tokenization
        # This is a rough approximation
        return int(len(text) / self.avg_chars_per_token)

    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts."""
        return [self.count_tokens(text) for text in texts]

    def truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit."""
        estimated_tokens = self.count_tokens(text)
        if estimated_tokens <= max_tokens:
            return text

        # Truncate by character count
        max_chars = int(max_tokens * self.avg_chars_per_token)
        return text[:max_chars]


class UniversalTokenCounter(TokenCounter):
    """
    Universal token counter that can handle multiple providers.

    This counter provides a unified interface for token counting across
    different LLM providers with provider-specific implementations.
    """

    def __init__(self):
        self.counters: Dict[str, TokenCounter] = {
            "openai": OpenAITokenCounter(),
            "anthropic": AnthropicTokenCounter(),
            "google": GoogleTokenCounter(),
        }
        self.default_counter = OpenAITokenCounter()

    def count_tokens(self, text: str, provider: str = "openai") -> int:
        """Count tokens using provider-specific counter."""
        counter = self.counters.get(provider, self.default_counter)
        return counter.count_tokens(text)

    def count_tokens_batch(
        self, texts: List[str], provider: str = "openai"
    ) -> List[int]:
        """Count tokens for multiple texts using provider-specific counter."""
        counter = self.counters.get(provider, self.default_counter)
        return counter.count_tokens_batch(texts)

    def truncate_to_tokens(
        self, text: str, max_tokens: int, provider: str = "openai"
    ) -> str:
        """Truncate text to fit within token limit using provider-specific counter."""
        counter = self.counters.get(provider, self.default_counter)
        return counter.truncate_to_tokens(text, max_tokens)

    def estimate_context_usage(
        self, prompt: str, expected_response_length: int = 100, provider: str = "openai"
    ) -> Dict[str, int]:
        """
        Estimate total context usage for a request.

        Args:
            prompt: Input prompt text
            expected_response_length: Expected response length in characters
            provider: LLM provider name

        Returns:
            Dictionary with token counts for input, output, and total
        """
        input_tokens = self.count_tokens(prompt, provider)
        output_tokens = self.count_tokens("x" * expected_response_length, provider)
        total_tokens = input_tokens + output_tokens

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        }

    def get_context_window_usage(
        self, prompt: str, context_window: int, provider: str = "openai"
    ) -> Dict[str, Union[int, float, bool]]:
        """
        Calculate context window usage and check if request fits.

        Args:
            prompt: Input prompt text
            context_window: Maximum context window size
            provider: LLM provider name

        Returns:
            Dictionary with usage statistics and fit status
        """
        input_tokens = self.count_tokens(prompt, provider)
        usage_percentage = (input_tokens / context_window) * 100
        fits = input_tokens <= context_window
        remaining_tokens = max(0, context_window - input_tokens)

        return {
            "input_tokens": input_tokens,
            "context_window": context_window,
            "usage_percentage": usage_percentage,
            "fits": fits,
            "remaining_tokens": remaining_tokens,
        }

    def optimize_prompt_length(
        self,
        prompt: str,
        max_tokens: int,
        provider: str = "openai",
        preserve_structure: bool = True,
    ) -> str:
        """
        Optimize prompt length to fit within token limit.

        Args:
            prompt: Original prompt text
            max_tokens: Maximum token limit
            provider: LLM provider name
            preserve_structure: Whether to preserve prompt structure

        Returns:
            Optimized prompt text
        """
        current_tokens = self.count_tokens(prompt, provider)

        if current_tokens <= max_tokens:
            return prompt

        if preserve_structure:
            # Try to preserve structure by truncating from the middle
            # This is a simple implementation - could be more sophisticated
            return self.truncate_to_tokens(prompt, max_tokens, provider)
        else:
            # Simple truncation from the end
            return self.truncate_to_tokens(prompt, max_tokens, provider)

    def add_counter(self, provider: str, counter: TokenCounter) -> None:
        """Add a custom token counter for a provider."""
        self.counters[provider] = counter

    def get_supported_providers(self) -> List[str]:
        """Get list of supported providers."""
        return list(self.counters.keys())


# Global instance for easy access
token_counter = UniversalTokenCounter()


def count_tokens(text: str, provider: str = "openai") -> int:
    """Convenience function to count tokens."""
    return token_counter.count_tokens(text, provider)


def estimate_context_usage(
    prompt: str, expected_response_length: int = 100, provider: str = "openai"
) -> Dict[str, int]:
    """Convenience function to estimate context usage."""
    return token_counter.estimate_context_usage(
        prompt, expected_response_length, provider
    )
