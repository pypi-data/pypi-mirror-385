"""
Main database interface for EzDB vector database
"""
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
import json
import pickle
import os

from .storage import VectorStore
from .index import HNSWIndex, BruteForceIndex
from .similarity import SimilarityMetric, calculate_similarity


class SearchResult:
    """Container for search results"""

    def __init__(self, id: str, score: float, vector: np.ndarray, metadata: Dict[str, Any], document: Optional[str] = None):
        self.id = id
        self.score = score
        self.vector = vector
        self.metadata = metadata
        self.document = document

    def __repr__(self):
        return f"SearchResult(id={self.id}, score={self.score:.4f}, metadata={self.metadata})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'score': float(self.score),
            'metadata': self.metadata,
            'vector': self.vector.tolist()
        }
        if self.document is not None:
            result['document'] = self.document
        return result


class EzDB:
    """
    EzDB - A simple and efficient vector database.

    Supports:
    - Fast similarity search using HNSW indexing
    - Multiple similarity metrics (cosine, euclidean, dot product)
    - Metadata filtering
    - Persistence (save/load)
    - Batch operations
    """

    def __init__(
        self,
        dimension: int,
        metric: Union[str, SimilarityMetric] = SimilarityMetric.COSINE,
        index_type: str = 'hnsw',
        max_elements: int = 10000,
        ef_construction: int = 200,
        M: int = 16
    ):
        """
        Initialize EzDB database.

        Args:
            dimension: Vector dimensionality
            metric: Similarity metric ('cosine', 'euclidean', 'dot_product')
            index_type: Type of index ('hnsw' or 'brute_force')
            max_elements: Maximum number of vectors (for HNSW)
            ef_construction: HNSW construction parameter (higher = better quality)
            M: HNSW connectivity parameter (higher = better recall)
        """
        self.dimension = dimension
        self.metric = SimilarityMetric(metric) if isinstance(metric, str) else metric
        self.index_type = index_type

        # Initialize storage
        self.store = VectorStore(dimension=dimension)

        # Initialize index
        if index_type == 'hnsw':
            space = self._metric_to_space(self.metric)
            self.index = HNSWIndex(
                dimension=dimension,
                space=space,
                max_elements=max_elements,
                ef_construction=ef_construction,
                M=M
            )
        elif index_type == 'brute_force':
            space = self._metric_to_space(self.metric)
            self.index = BruteForceIndex(dimension=dimension, metric=space)
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Track if index needs rebuilding
        self._index_dirty = False

    def _metric_to_space(self, metric: SimilarityMetric) -> str:
        """Convert SimilarityMetric to index space string"""
        mapping = {
            SimilarityMetric.COSINE: 'cosine',
            SimilarityMetric.EUCLIDEAN: 'l2',
            SimilarityMetric.DOT_PRODUCT: 'ip'
        }
        return mapping[metric]

    def insert(
        self,
        vector: Union[List[float], np.ndarray],
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        document: Optional[str] = None
    ) -> str:
        """
        Insert a vector into the database.

        Args:
            vector: Vector to insert
            metadata: Optional metadata dictionary
            id: Optional custom ID
            document: Optional original document/text

        Returns:
            ID of inserted vector
        """
        vector = np.array(vector, dtype=np.float32)

        # Insert into storage
        vector_id = self.store.insert(vector, metadata, id, document)

        # Mark index as needing rebuild
        self._index_dirty = True

        return vector_id

    def insert_batch(
        self,
        vectors: List[Union[List[float], np.ndarray]],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        documents: Optional[List[str]] = None
    ) -> List[str]:
        """
        Insert multiple vectors at once (more efficient).

        Args:
            vectors: List of vectors to insert
            metadata_list: Optional list of metadata dictionaries
            ids: Optional list of custom IDs
            documents: Optional list of original documents/text

        Returns:
            List of IDs for inserted vectors
        """
        vectors = [np.array(v, dtype=np.float32) for v in vectors]
        inserted_ids = self.store.insert_batch(vectors, metadata_list, ids, documents)

        # Mark index as needing rebuild
        self._index_dirty = True

        return inserted_ids

    def search(
        self,
        query_vector: Union[List[float], np.ndarray],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        ef: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query vector
            top_k: Number of results to return
            filters: Optional metadata filters
            ef: HNSW search parameter (higher = better recall, slower)

        Returns:
            List of SearchResult objects, sorted by similarity
        """
        query_vector = np.array(query_vector, dtype=np.float32)

        if query_vector.shape[0] != self.dimension:
            raise ValueError(
                f"Query vector dimension {query_vector.shape[0]} "
                f"doesn't match database dimension {self.dimension}"
            )

        # Rebuild index if needed
        if self._index_dirty:
            self._rebuild_index()

        # Handle empty database
        if self.store.size() == 0:
            return []

        # Apply metadata filters first if provided
        if filters:
            candidate_indices = self.store.filter_by_metadata(filters)
            if not candidate_indices:
                return []

            # Search only within filtered candidates
            candidate_vectors = np.vstack([self.store.vectors[i] for i in candidate_indices])
            candidate_ids = [self.store.ids[i] for i in candidate_indices]

            # Use brute force for filtered search
            from .similarity import batch_similarity
            scores = batch_similarity(query_vector, candidate_vectors, self.metric)

            # Get top k
            top_k = min(top_k, len(scores))
            top_indices = np.argsort(scores)[::-1][:top_k]

            results = []
            for idx in top_indices:
                store_idx = candidate_indices[idx]
                results.append(SearchResult(
                    id=candidate_ids[idx],
                    score=float(scores[idx]),
                    vector=self.store.vectors[store_idx],
                    metadata=self.store.metadata[store_idx],
                    document=self.store.documents[store_idx]
                ))

            return results
        else:
            # Use index for fast search
            indices, distances = self.index.search(query_vector, k=top_k, ef=ef)

            # Convert to SearchResult objects
            results = []
            for idx, distance in zip(indices, distances):
                # Convert distance to similarity score
                if self.metric == SimilarityMetric.COSINE:
                    score = 1 - distance
                elif self.metric == SimilarityMetric.EUCLIDEAN:
                    score = -distance
                else:  # DOT_PRODUCT
                    score = -distance

                vector_id = self.store.ids[idx]
                results.append(SearchResult(
                    id=vector_id,
                    score=float(score),
                    vector=self.store.vectors[idx],
                    metadata=self.store.metadata[idx],
                    document=self.store.documents[idx]
                ))

            return results

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """
        Get a vector by ID.

        Args:
            id: Vector ID

        Returns:
            Dictionary with 'id', 'vector', and 'metadata', or None if not found
        """
        return self.store.get(id)

    def update(
        self,
        id: str,
        vector: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> bool:
        """
        Update an existing vector's data, metadata, or document.

        Args:
            id: Vector ID
            vector: Optional new vector (None to keep existing)
            metadata: Optional new metadata (None to keep existing)
            document: Optional new document (None to keep existing)

        Returns:
            True if updated, False if not found
        """
        if vector is not None:
            vector = np.array(vector, dtype=np.float32)

        success = self.store.update(id, vector, metadata, document)
        if success and vector is not None:
            # Only mark index dirty if vector was updated
            self._index_dirty = True
        return success

    def upsert(
        self,
        vector: Union[List[float], np.ndarray],
        id: str,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> Tuple[str, bool]:
        """
        Insert or update a vector (upsert = update or insert).

        Args:
            vector: Vector to insert/update
            id: ID of vector (required for upsert)
            metadata: Optional metadata dictionary
            document: Optional original document/text

        Returns:
            Tuple of (vector_id, was_update) where was_update is True if existing vector was updated
        """
        vector = np.array(vector, dtype=np.float32)
        vector_id, was_update = self.store.upsert(vector, id, metadata, document)
        self._index_dirty = True
        return vector_id, was_update

    def search_documents(
        self,
        query: str,
        top_k: int = 10,
        case_sensitive: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Full-text search on stored documents.

        Args:
            query: Text query to search for
            top_k: Number of results to return
            case_sensitive: Whether search is case-sensitive
            filters: Optional metadata filters to apply first

        Returns:
            List of SearchResult objects with relevance scores
        """
        import re

        if not query:
            return []

        # Prepare query for matching
        search_query = query if case_sensitive else query.lower()

        # Get candidate indices (with metadata filtering if provided)
        if filters:
            candidate_indices = self.store.filter_by_metadata(filters)
        else:
            candidate_indices = list(range(self.store.size()))

        # Score documents by relevance
        scored_results = []
        for idx in candidate_indices:
            document = self.store.documents[idx]

            # Skip vectors without documents
            if document is None:
                continue

            # Prepare document for matching
            doc_text = document if case_sensitive else document.lower()

            # Calculate relevance score (simple count of query occurrences)
            # More sophisticated scoring could use TF-IDF, BM25, etc.
            query_words = search_query.split()
            score = 0.0

            for word in query_words:
                # Count word occurrences
                count = doc_text.count(word)
                score += count

            # Only include documents that match
            if score > 0:
                scored_results.append((idx, score))

        # Sort by score (descending) and get top k
        scored_results.sort(key=lambda x: x[1], reverse=True)
        scored_results = scored_results[:top_k]

        # Build result objects
        results = []
        for idx, score in scored_results:
            results.append(SearchResult(
                id=self.store.ids[idx],
                score=float(score),
                vector=self.store.vectors[idx],
                metadata=self.store.metadata[idx],
                document=self.store.documents[idx]
            ))

        return results

    def delete(self, id: str) -> bool:
        """
        Delete a vector by ID.

        Args:
            id: Vector ID

        Returns:
            True if deleted, False if not found
        """
        success = self.store.delete(id)
        if success:
            self._index_dirty = True
        return success

    def _rebuild_index(self):
        """Rebuild the index from current vectors"""
        if self.store.size() == 0:
            return

        vectors = self.store.get_all_vectors()
        ids = np.arange(len(vectors))

        self.index.rebuild(vectors, ids)
        self._index_dirty = False

    def size(self) -> int:
        """Get number of vectors in database"""
        return self.store.size()

    def get_all_vectors(self) -> List[Dict[str, Any]]:
        """
        Get all vectors with their metadata.

        Returns:
            List of dictionaries with 'id', 'vector', 'metadata', and 'document'
        """
        all_vectors = []
        for i in range(self.store.size()):
            all_vectors.append({
                'id': self.store.ids[i],
                'vector': self.store.vectors[i],
                'metadata': self.store.metadata[i],
                'document': self.store.documents[i]
            })
        return all_vectors

    def clear(self):
        """Remove all vectors from database"""
        self.store.clear()
        self._index_dirty = True

    def save(self, filepath: str):
        """
        Save database to disk.

        Args:
            filepath: Path to save database (will create .ezdb file)
        """
        # Ensure index is up to date
        if self._index_dirty:
            self._rebuild_index()

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        # Save metadata and configuration
        metadata = {
            'dimension': self.dimension,
            'metric': self.metric.value,
            'index_type': self.index_type,
            'size': self.store.size(),
            'ids': self.store.ids,
            'metadata': self.store.metadata,
            'vectors': self.store.get_all_vectors().tolist()
        }

        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save index separately if using HNSW
        if self.index_type == 'hnsw':
            index_path = filepath + '.index'
            self.index.save(index_path)

        print(f"Database saved to {filepath}")

    @classmethod
    def load(cls, filepath: str) -> 'EzDB':
        """
        Load database from disk.

        Args:
            filepath: Path to saved database file

        Returns:
            Loaded EzDB instance
        """
        # Load metadata
        with open(filepath, 'r') as f:
            metadata = json.load(f)

        # Create new database instance
        db = cls(
            dimension=metadata['dimension'],
            metric=metadata['metric'],
            index_type=metadata['index_type']
        )

        # Restore vectors and metadata
        vectors = [np.array(v, dtype=np.float32) for v in metadata['vectors']]
        db.store.insert_batch(
            vectors=vectors,
            metadata_list=metadata['metadata'],
            ids=metadata['ids']
        )

        # Load index
        if metadata['index_type'] == 'hnsw':
            index_path = filepath + '.index'
            if os.path.exists(index_path):
                db.index.load(index_path)
                db._index_dirty = False
            else:
                db._rebuild_index()
        else:
            db._rebuild_index()

        print(f"Database loaded from {filepath} ({metadata['size']} vectors)")

        return db

    def stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with database stats
        """
        return {
            'dimension': self.dimension,
            'metric': self.metric.value,
            'index_type': self.index_type,
            'size': self.store.size(),
            'index_count': self.index.get_count(),
            'index_dirty': self._index_dirty
        }

    def __repr__(self):
        return f"EzDB(dimension={self.dimension}, metric={self.metric.value}, size={self.size()})"
