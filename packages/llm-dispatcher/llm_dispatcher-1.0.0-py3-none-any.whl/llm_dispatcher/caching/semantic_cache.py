"""
Semantic cache for intelligent response retrieval.

This module provides semantic similarity-based caching that can find
cached responses for semantically similar requests, not just exact matches.
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from sentence_transformers import SentenceTransformer
import faiss

from .cache_manager import CacheManager, CacheEntry
from ..core.base import TaskRequest, TaskResponse

logger = logging.getLogger(__name__)


@dataclass
class SemanticCacheEntry(CacheEntry):
    """Semantic cache entry with embedding."""

    embedding: Optional[np.ndarray] = None
    similarity_threshold: float = 0.85


class SemanticCache:
    """
    Semantic cache for intelligent response retrieval.

    This class provides semantic similarity-based caching that can find
    cached responses for semantically similar requests using embeddings.
    """

    def __init__(
        self,
        cache_manager: CacheManager,
        similarity_threshold: float = 0.85,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.cache_manager = cache_manager
        self.similarity_threshold = similarity_threshold

        # Initialize embedding model
        self.embedding_model = SentenceTransformer(model_name)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # FAISS index for fast similarity search
        self.faiss_index = faiss.IndexFlatIP(
            self.embedding_dim
        )  # Inner product (cosine similarity)
        self.entry_mapping: Dict[int, str] = {}  # FAISS index -> cache key mapping

        # Cache for embeddings
        self.embedding_cache: Dict[str, np.ndarray] = {}

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text with caching."""
        if text in self.embedding_cache:
            return self.embedding_cache[text]

        # Clean and prepare text
        clean_text = self._preprocess_text(text)

        # Generate embedding
        embedding = self.embedding_model.encode(clean_text, normalize_embeddings=True)

        # Cache embedding
        self.embedding_cache[text] = embedding

        return embedding

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for embedding."""
        # Remove extra whitespace and normalize
        text = " ".join(text.strip().split())

        # Truncate if too long (most embedding models have limits)
        max_length = 512  # Conservative limit
        if len(text) > max_length:
            text = text[:max_length]

        return text

    async def get_similar_response(
        self, request: TaskRequest, max_results: int = 5
    ) -> List[Tuple[TaskResponse, float]]:
        """Get semantically similar cached responses."""
        # Get embedding for request
        request_embedding = self._get_embedding(request.prompt)
        request_embedding = request_embedding.reshape(1, -1)

        # Search FAISS index
        if self.faiss_index.ntotal == 0:
            return []

        # Get top similar entries
        similarities, indices = self.faiss_index.search(request_embedding, max_results)

        results = []
        for similarity, idx in zip(similarities[0], indices[0]):
            if similarity >= self.similarity_threshold and idx in self.entry_mapping:
                cache_key = self.entry_mapping[idx]
                if cache_key in self.cache_manager.cache:
                    entry = self.cache_manager.cache[cache_key]
                    if self.cache_manager._is_entry_valid(entry):
                        results.append((entry.response, float(similarity)))

        # Sort by similarity (descending)
        results.sort(key=lambda x: x[1], reverse=True)

        return results

    async def add_to_semantic_cache(
        self, request: TaskRequest, response: TaskResponse
    ) -> bool:
        """Add response to semantic cache."""
        # First add to regular cache
        cache_key = self.cache_manager._generate_cache_key(request)
        cache_entry = CacheEntry(
            key=cache_key,
            request_hash=cache_key,
            response=response,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            tags=self.cache_manager._extract_tags(request),
            metadata=self.cache_manager._extract_metadata(request, response),
        )

        # Add to cache manager
        self.cache_manager.cache[cache_key] = cache_entry
        self.cache_manager.access_order.append(cache_key)

        # Get embedding for semantic indexing
        request_embedding = self._get_embedding(request.prompt)

        # Add to FAISS index
        embedding_array = request_embedding.reshape(1, -1)
        self.faiss_index.add(embedding_array)

        # Map FAISS index to cache key
        faiss_index_id = self.faiss_index.ntotal - 1
        self.entry_mapping[faiss_index_id] = cache_key

        logger.debug(
            f"Added to semantic cache: {cache_key[:16]}... (similarity threshold: {self.similarity_threshold})"
        )
        return True

    async def find_best_similar_response(
        self, request: TaskRequest
    ) -> Optional[Tuple[TaskResponse, float]]:
        """Find the best semantically similar response."""
        similar_responses = await self.get_similar_response(request, max_results=1)
        return similar_responses[0] if similar_responses else None

    def update_similarity_threshold(self, new_threshold: float) -> None:
        """Update similarity threshold for cache retrieval."""
        self.similarity_threshold = new_threshold
        logger.info(f"Updated similarity threshold to: {new_threshold}")

    def get_semantic_cache_stats(self) -> Dict[str, Any]:
        """Get semantic cache statistics."""
        base_stats = self.cache_manager.get_cache_stats()

        return {
            **base_stats,
            "semantic_entries": self.faiss_index.ntotal,
            "similarity_threshold": self.similarity_threshold,
            "embedding_dimension": self.embedding_dim,
            "embedding_cache_size": len(self.embedding_cache),
        }

    async def rebuild_semantic_index(self) -> None:
        """Rebuild the semantic index from current cache."""
        logger.info("Rebuilding semantic index...")

        # Clear existing index
        self.faiss_index.reset()
        self.entry_mapping.clear()

        # Rebuild from current cache
        embeddings_to_add = []
        cache_keys = []

        for cache_key, entry in self.cache_manager.cache.items():
            if self.cache_manager._is_entry_valid(entry):
                embedding = self._get_embedding(entry.response.content)
                embeddings_to_add.append(embedding)
                cache_keys.append(cache_key)

        if embeddings_to_add:
            # Add all embeddings at once
            embedding_matrix = np.vstack(embeddings_to_add)
            self.faiss_index.add(embedding_matrix)

            # Update mapping
            for i, cache_key in enumerate(cache_keys):
                self.entry_mapping[i] = cache_key

        logger.info(f"Rebuilt semantic index with {len(cache_keys)} entries")

    def find_semantic_clusters(self, min_cluster_size: int = 2) -> List[Dict[str, Any]]:
        """Find clusters of semantically similar cache entries."""
        if self.faiss_index.ntotal < min_cluster_size:
            return []

        # Get all embeddings
        all_embeddings = []
        cache_keys = []

        for i in range(self.faiss_index.ntotal):
            if i in self.entry_mapping:
                cache_key = self.entry_mapping[i]
                if cache_key in self.cache_manager.cache:
                    entry = self.cache_manager.cache[cache_key]
                    embedding = self._get_embedding(entry.response.content)
                    all_embeddings.append(embedding)
                    cache_keys.append(cache_key)

        if len(all_embeddings) < min_cluster_size:
            return []

        # Simple clustering based on similarity
        clusters = []
        used_indices = set()

        for i, embedding1 in enumerate(all_embeddings):
            if i in used_indices:
                continue

            cluster = [i]
            used_indices.add(i)

            # Find similar entries
            for j, embedding2 in enumerate(all_embeddings):
                if j in used_indices or j == i:
                    continue

                similarity = np.dot(embedding1, embedding2)
                if similarity >= self.similarity_threshold:
                    cluster.append(j)
                    used_indices.add(j)

            if len(cluster) >= min_cluster_size:
                cluster_info = {
                    "size": len(cluster),
                    "entries": [
                        {
                            "cache_key": cache_keys[idx][:16] + "...",
                            "response_length": len(
                                self.cache_manager.cache[
                                    cache_keys[idx]
                                ].response.content
                            ),
                            "access_count": self.cache_manager.cache[
                                cache_keys[idx]
                            ].access_count,
                        }
                        for idx in cluster
                    ],
                }
                clusters.append(cluster_info)

        return clusters

    async def cleanup_semantic_cache(self) -> None:
        """Clean up semantic cache by removing invalid entries."""
        logger.info("Cleaning up semantic cache...")

        # Get list of valid cache keys
        valid_keys = set()
        for cache_key, entry in self.cache_manager.cache.items():
            if self.cache_manager._is_entry_valid(entry):
                valid_keys.add(cache_key)

        # Remove invalid entries from FAISS index and mapping
        indices_to_remove = []
        for faiss_idx, cache_key in list(self.entry_mapping.items()):
            if cache_key not in valid_keys:
                indices_to_remove.append(faiss_idx)
                del self.entry_mapping[faiss_idx]

        if indices_to_remove:
            logger.info(
                f"Removing {len(indices_to_remove)} invalid semantic cache entries"
            )
            # Note: FAISS doesn't support direct removal, so we rebuild the index
            await self.rebuild_semantic_index()

    def export_semantic_cache(self, filepath: str) -> None:
        """Export semantic cache data."""
        import pickle

        cache_data = {
            "entries": {
                key: {
                    "request_hash": entry.request_hash,
                    "response_content": entry.response.content,
                    "created_at": entry.created_at.isoformat(),
                    "last_accessed": entry.last_accessed.isoformat(),
                    "access_count": entry.access_count,
                    "tags": entry.tags,
                    "metadata": entry.metadata,
                }
                for key, entry in self.cache_manager.cache.items()
                if self.cache_manager._is_entry_valid(entry)
            },
            "entry_mapping": self.entry_mapping,
            "similarity_threshold": self.similarity_threshold,
            "embedding_cache": {k: v.tolist() for k, v in self.embedding_cache.items()},
        }

        with open(filepath, "wb") as f:
            pickle.dump(cache_data, f)

        logger.info(f"Exported semantic cache to: {filepath}")
