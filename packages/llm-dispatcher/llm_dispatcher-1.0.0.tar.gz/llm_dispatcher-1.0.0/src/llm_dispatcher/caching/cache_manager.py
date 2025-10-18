"""
Advanced cache manager for LLM-Dispatcher.

This module provides comprehensive caching capabilities including response caching,
intelligent cache policies, and cache optimization strategies.
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import asyncio
import logging

from ..core.base import TaskRequest, TaskResponse, TaskType

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """A cache entry with metadata."""

    key: str
    request_hash: str
    response: TaskResponse
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    hit_score: float = 1.0  # For cache optimization
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CachePolicy(ABC):
    """Abstract base class for cache policies."""

    @abstractmethod
    def should_cache(self, request: TaskRequest, response: TaskResponse) -> bool:
        """Determine if a response should be cached."""
        pass

    @abstractmethod
    def get_ttl(self, request: TaskRequest, response: TaskResponse) -> timedelta:
        """Get time-to-live for a cache entry."""
        pass

    @abstractmethod
    def should_evict(self, entry: CacheEntry) -> bool:
        """Determine if a cache entry should be evicted."""
        pass


class LRUPolicy(CachePolicy):
    """Least Recently Used cache policy."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size

    def should_cache(self, request: TaskRequest, response: TaskResponse) -> bool:
        """Cache all successful responses."""
        return response.finish_reason == "stop"

    def get_ttl(self, request: TaskRequest, response: TaskResponse) -> timedelta:
        """Default TTL based on task type."""
        ttl_mapping = {
            TaskType.TEXT_GENERATION: timedelta(hours=24),
            TaskType.CODE_GENERATION: timedelta(hours=12),
            TaskType.QUESTION_ANSWERING: timedelta(hours=48),
            TaskType.SUMMARIZATION: timedelta(hours=24),
            TaskType.TRANSLATION: timedelta(days=7),
            TaskType.CLASSIFICATION: timedelta(hours=6),
            TaskType.REASONING: timedelta(hours=12),
            TaskType.MATH: timedelta(hours=24),
        }
        return ttl_mapping.get(request.task_type, timedelta(hours=12))

    def should_evict(self, entry: CacheEntry) -> bool:
        """Evict if expired or cache is full."""
        return datetime.now() > entry.created_at + self.get_ttl(
            TaskRequest(prompt="", task_type=TaskType.TEXT_GENERATION), entry.response
        )


class TTLPolicy(CachePolicy):
    """Time-to-Live based cache policy."""

    def __init__(self, default_ttl: timedelta = timedelta(hours=12)):
        self.default_ttl = default_ttl

    def should_cache(self, request: TaskRequest, response: TaskResponse) -> bool:
        """Cache based on response quality and task type."""
        # Don't cache if response is too short or has errors
        if len(response.content.strip()) < 10:
            return False

        # Don't cache certain task types
        no_cache_types = {TaskType.FUNCTION_CALLING, TaskType.AUDIO_TRANSCRIPTION}
        return request.task_type not in no_cache_types

    def get_ttl(self, request: TaskRequest, response: TaskResponse) -> timedelta:
        """Get TTL based on task complexity and response length."""
        base_ttl = self.default_ttl

        # Adjust based on task type
        if request.task_type in [TaskType.TRANSLATION, TaskType.CLASSIFICATION]:
            base_ttl *= 2  # Longer TTL for deterministic tasks
        elif request.task_type in [TaskType.CODE_GENERATION, TaskType.REASONING]:
            base_ttl *= 0.5  # Shorter TTL for creative tasks

        # Adjust based on response length
        if len(response.content) > 1000:
            base_ttl *= 1.5  # Longer TTL for substantial responses

        return base_ttl

    def should_evict(self, entry: CacheEntry) -> bool:
        """Evict if TTL expired."""
        return datetime.now() > entry.created_at + self.get_ttl(
            TaskRequest(prompt="", task_type=TaskType.TEXT_GENERATION), entry.response
        )


class SizePolicy(CachePolicy):
    """Size-based cache policy with memory management."""

    def __init__(self, max_memory_mb: int = 100):
        self.max_memory_mb = max_memory_mb
        self.current_size_bytes = 0

    def should_cache(self, request: TaskRequest, response: TaskResponse) -> bool:
        """Cache if response is not too large."""
        response_size = len(response.content.encode("utf-8"))
        max_response_size = 1024 * 1024  # 1MB max per response
        return response_size < max_response_size

    def get_ttl(self, request: TaskRequest, response: TaskResponse) -> timedelta:
        """TTL based on response size."""
        response_size = len(response.content.encode("utf-8"))
        if response_size < 1024:  # < 1KB
            return timedelta(hours=24)
        elif response_size < 10240:  # < 10KB
            return timedelta(hours=12)
        else:
            return timedelta(hours=6)

    def should_evict(self, entry: CacheEntry) -> bool:
        """Evict if memory limit exceeded."""
        return self.current_size_bytes > (self.max_memory_mb * 1024 * 1024)


class CacheManager:
    """
    Advanced cache manager for LLM-Dispatcher.

    This class provides comprehensive caching capabilities including
    response caching, intelligent eviction policies, and cache optimization.
    """

    def __init__(self, policy: CachePolicy = None, max_size: int = 1000):
        self.policy = policy or LRUPolicy(max_size)
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # For LRU tracking

        # Cache statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        # Background cleanup
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the cache manager background tasks."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Cache manager started")

    async def stop(self) -> None:
        """Stop the cache manager background tasks."""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Cache manager stopped")

    def _generate_cache_key(self, request: TaskRequest) -> str:
        """Generate cache key from request."""
        # Create a normalized version of the request for caching
        cache_data = {
            "prompt": request.prompt.strip().lower(),
            "task_type": request.task_type.value,
            "temperature": round(request.temperature, 2),
            "max_tokens": request.max_tokens,
            "top_p": round(request.top_p, 2),
        }

        # Include images if present (hash them)
        if request.images:
            cache_data["images"] = [
                hashlib.sha256(img.encode()).hexdigest()[:16] for img in request.images
            ]

        # Create deterministic hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def get(self, request: TaskRequest) -> Optional[TaskResponse]:
        """Get cached response for request."""
        cache_key = self._generate_cache_key(request)

        if cache_key in self.cache:
            entry = self.cache[cache_key]

            # Check if entry is still valid
            if self._is_entry_valid(entry):
                # Update access tracking
                entry.last_accessed = datetime.now()
                entry.access_count += 1

                # Update LRU order
                if cache_key in self.access_order:
                    self.access_order.remove(cache_key)
                self.access_order.append(cache_key)

                self.hits += 1
                logger.debug(f"Cache hit for key: {cache_key[:16]}...")
                return entry.response
            else:
                # Remove expired entry
                del self.cache[cache_key]
                if cache_key in self.access_order:
                    self.access_order.remove(cache_key)

        self.misses += 1
        logger.debug(f"Cache miss for key: {cache_key[:16]}...")
        return None

    async def put(self, request: TaskRequest, response: TaskResponse) -> bool:
        """Cache a response."""
        # Check if we should cache this response
        if not self.policy.should_cache(request, response):
            logger.debug("Response not cached due to policy")
            return False

        cache_key = self._generate_cache_key(request)

        # Create cache entry
        entry = CacheEntry(
            key=cache_key,
            request_hash=cache_key,
            response=response,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            tags=self._extract_tags(request),
            metadata=self._extract_metadata(request, response),
        )

        # Check if we need to evict entries
        await self._ensure_space(entry)

        # Add to cache
        self.cache[cache_key] = entry
        self.access_order.append(cache_key)

        logger.debug(f"Cached response for key: {cache_key[:16]}...")
        return True

    def _is_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid."""
        return not self.policy.should_evict(entry)

    def _extract_tags(self, request: TaskRequest) -> List[str]:
        """Extract tags from request for cache organization."""
        tags = [request.task_type.value]

        # Add provider tags if available
        if hasattr(request, "preferred_provider"):
            tags.append(f"provider:{request.preferred_provider}")

        # Add complexity tags
        if len(request.prompt) > 1000:
            tags.append("complex")
        else:
            tags.append("simple")

        return tags

    def _extract_metadata(
        self, request: TaskRequest, response: TaskResponse
    ) -> Dict[str, Any]:
        """Extract metadata from request and response."""
        return {
            "request_length": len(request.prompt),
            "response_length": len(response.content),
            "response_time": response.latency_ms,
            "model_used": response.model_used,
            "provider_used": response.provider,
            "tokens_used": response.tokens_used,
            "cost": response.cost,
        }

    async def _ensure_space(self, new_entry: CacheEntry) -> None:
        """Ensure there's space for new entry."""
        # Simple size check - remove expired entries first
        await self._remove_expired_entries()

        # If still no space, use LRU eviction
        while len(self.cache) >= self.policy.max_size and self.access_order:
            oldest_key = self.access_order[0]
            if oldest_key in self.cache:
                del self.cache[oldest_key]
                self.access_order.remove(oldest_key)
                self.evictions += 1
                logger.debug(f"Evicted cache entry: {oldest_key[:16]}...")

    async def _remove_expired_entries(self) -> None:
        """Remove expired cache entries."""
        expired_keys = []

        for key, entry in self.cache.items():
            if self.policy.should_evict(entry):
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            self.evictions += 1
            logger.debug(f"Removed expired entry: {key[:16]}...")

    async def _cleanup_loop(self) -> None:
        """Background task for cache cleanup."""
        while self._running:
            try:
                await self._remove_expired_entries()
                await asyncio.sleep(300)  # Cleanup every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
                await asyncio.sleep(60)

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        invalidated = 0

        # Simple pattern matching on prompt content
        for key, entry in list(self.cache.items()):
            if pattern.lower() in entry.response.content.lower():
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                invalidated += 1

        logger.info(
            f"Invalidated {invalidated} cache entries matching pattern: {pattern}"
        )
        return invalidated

    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate cache entries with specific tags."""
        invalidated = 0

        for key, entry in list(self.cache.items()):
            if any(tag in entry.tags for tag in tags):
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                invalidated += 1

        logger.info(f"Invalidated {invalidated} cache entries with tags: {tags}")
        return invalidated

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0

        # Calculate memory usage
        total_size = sum(
            len(entry.response.content.encode("utf-8")) for entry in self.cache.values()
        )

        return {
            "cache_size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "evictions": self.evictions,
            "memory_usage_mb": total_size / (1024 * 1024),
            "oldest_entry": min(
                (entry.created_at for entry in self.cache.values()), default=None
            ),
            "newest_entry": max(
                (entry.created_at for entry in self.cache.values()), default=None
            ),
        }

    def get_popular_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently accessed cache entries."""
        sorted_entries = sorted(
            self.cache.values(), key=lambda x: x.access_count, reverse=True
        )

        return [
            {
                "key": entry.key[:16] + "...",
                "access_count": entry.access_count,
                "last_accessed": entry.last_accessed.isoformat(),
                "response_length": len(entry.response.content),
                "tags": entry.tags,
            }
            for entry in sorted_entries[:limit]
        ]

    def clear_cache(self) -> int:
        """Clear all cache entries."""
        cleared_count = len(self.cache)
        self.cache.clear()
        self.access_order.clear()
        logger.info(f"Cleared {cleared_count} cache entries")
        return cleared_count
