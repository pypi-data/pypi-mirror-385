"""Qdrant vector store with HNSW tuning."""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchAny,
    MatchValue,
    OptimizersConfigDiff,
    PayloadSchemaType,
    PointStruct,
    SearchParams,
    VectorParams,
    WalConfigDiff,
)

from hippocampai.utils.retry import get_qdrant_retry_decorator

logger = logging.getLogger(__name__)


class QdrantStore:
    """Qdrant store with HNSW optimization."""

    def __init__(
        self,
        url: str = "http://localhost:6333",
        collection_facts: str = "hippocampai_facts",
        collection_prefs: str = "hippocampai_prefs",
        dimension: int = 384,
        hnsw_m: int = 48,
        ef_construction: int = 256,
        ef_search: int = 128,
    ):
        self.client = QdrantClient(url=url)
        self.collection_facts = collection_facts
        self.collection_prefs = collection_prefs
        self.dimension = dimension
        self.hnsw_m = hnsw_m
        self.ef_construction = ef_construction
        self.ef_search = ef_search

        logger.info(f"Connected to Qdrant at {url}")
        self._ensure_collections()

    def _ensure_collections(self):
        """Create collections if they don't exist."""
        for collection_name in [self.collection_facts, self.collection_prefs]:
            if not self.client.collection_exists(collection_name):
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
                    hnsw_config=HnswConfigDiff(m=self.hnsw_m, ef_construct=self.ef_construction),
                    optimizers_config=OptimizersConfigDiff(indexing_threshold=20000),
                    wal_config=WalConfigDiff(wal_capacity_mb=32),
                )

                # Create payload indices
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="user_id",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="type",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name="tags",
                    field_schema=PayloadSchemaType.KEYWORD,
                )

                logger.info(f"Created collection: {collection_name}")

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def upsert(self, collection_name: str, id: str, vector: np.ndarray, payload: Dict[str, Any]):
        """Insert or update a point (with automatic retry on transient failures)."""
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=id,
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else vector,
                    payload=payload,
                )
            ],
        )

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def search(
        self,
        collection_name: str,
        vector: np.ndarray,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        ef: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Vector similarity search (with automatic retry on transient failures)."""
        query_filter = None
        if filters:
            conditions = []
            if "user_id" in filters:
                conditions.append(
                    FieldCondition(key="user_id", match=MatchValue(value=filters["user_id"]))
                )
            if "type" in filters:
                conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=filters["type"]))
                )
            if "tags" in filters:
                # Support both single tag and list of tags
                tags = filters["tags"]
                if isinstance(tags, str):
                    tags = [tags]
                conditions.append(FieldCondition(key="tags", match=MatchAny(any=tags)))
            if conditions:
                query_filter = Filter(must=conditions)

        # Build search params
        hnsw_ef = ef if ef else self.ef_search
        search_params = SearchParams(hnsw_ef=hnsw_ef) if hnsw_ef else None

        # Use query_points instead of deprecated search
        results = self.client.query_points(
            collection_name=collection_name,
            query=vector.tolist() if isinstance(vector, np.ndarray) else vector,
            limit=limit,
            query_filter=query_filter,
            search_params=search_params,
            with_payload=True,
        ).points

        return [{"id": str(r.id), "score": r.score, "payload": r.payload} for r in results]

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def scroll(
        self, collection_name: str, filters: Optional[Dict[str, Any]] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Scroll through points (with automatic retry on transient failures)."""
        query_filter = None
        if filters:
            conditions = []
            if "user_id" in filters:
                conditions.append(
                    FieldCondition(key="user_id", match=MatchValue(value=filters["user_id"]))
                )
            if "type" in filters:
                conditions.append(
                    FieldCondition(key="type", match=MatchValue(value=filters["type"]))
                )
            if "tags" in filters:
                # Support both single tag and list of tags
                tags = filters["tags"]
                if isinstance(tags, str):
                    tags = [tags]
                conditions.append(FieldCondition(key="tags", match=MatchAny(any=tags)))
            if conditions:
                query_filter = Filter(must=conditions)

        results, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return [{"id": str(r.id), "payload": r.payload} for r in results]

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def delete(self, collection_name: str, ids: List[str]):
        """Delete points by IDs (with automatic retry on transient failures)."""
        self.client.delete(collection_name=collection_name, points_selector=ids)

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def get(self, collection_name: str, id: str) -> Optional[Dict[str, Any]]:
        """Get a single point by ID (with automatic retry on transient failures)."""
        try:
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[id],
                with_payload=True,
                with_vectors=False,
            )
            if result:
                return {"id": str(result[0].id), "payload": result[0].payload}
            return None
        except Exception as e:
            logger.error(f"Failed to get point {id}: {e}")
            return None

    @get_qdrant_retry_decorator(max_attempts=3, min_wait=1, max_wait=5)
    def update(self, collection_name: str, id: str, payload: Dict[str, Any]) -> bool:
        """Update payload of an existing point (with automatic retry on transient failures)."""
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=[id],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update point {id}: {e}")
            return False

    def create_snapshot(self, collection_name: str) -> str:
        """Create collection snapshot."""
        result = self.client.create_snapshot(collection_name=collection_name)
        return result.name
