"""
Indexing system using HNSW for fast approximate nearest neighbor search
"""
import numpy as np
from typing import List, Tuple, Optional
import hnswlib


class HNSWIndex:
    """
    HNSW (Hierarchical Navigable Small World) index for fast similarity search.
    This provides approximate nearest neighbor search with high recall.
    """

    def __init__(
        self,
        dimension: int,
        space: str = 'cosine',
        max_elements: int = 10000,
        ef_construction: int = 200,
        M: int = 16
    ):
        """
        Initialize HNSW index.

        Args:
            dimension: Vector dimensionality
            space: Distance metric ('cosine', 'l2', or 'ip' for inner product)
            max_elements: Maximum number of vectors the index can hold
            ef_construction: Controls index construction quality (higher = better, slower)
            M: Number of bi-directional links per node (higher = better recall, more memory)
        """
        self.dimension = dimension
        self.space = space
        self.max_elements = max_elements
        self.ef_construction = ef_construction
        self.M = M

        # Initialize hnswlib index
        self.index = hnswlib.Index(space=space, dim=dimension)
        self.index.init_index(
            max_elements=max_elements,
            ef_construction=ef_construction,
            M=M
        )

        # Track how many items are in the index
        self.current_count = 0
        self.is_built = False

    def build(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """
        Build index from vectors.

        Args:
            vectors: Matrix of vectors (each row is a vector)
            ids: Optional array of integer IDs for each vector
        """
        if len(vectors) == 0:
            return

        # Use sequential IDs if none provided
        if ids is None:
            ids = np.arange(len(vectors))

        # Add items to index
        self.index.add_items(vectors, ids)
        self.current_count = len(vectors)
        self.is_built = True

    def add_items(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """
        Add new vectors to existing index.

        Args:
            vectors: Matrix of vectors to add
            ids: Optional array of integer IDs for each vector
        """
        if len(vectors) == 0:
            return

        # Check if we need to resize
        if self.current_count + len(vectors) > self.max_elements:
            new_max = max(self.max_elements * 2, self.current_count + len(vectors))
            self.index.resize_index(new_max)
            self.max_elements = new_max

        # Use sequential IDs starting from current count if none provided
        if ids is None:
            ids = np.arange(self.current_count, self.current_count + len(vectors))

        self.index.add_items(vectors, ids)
        self.current_count += len(vectors)
        self.is_built = True

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        ef: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors.

        Args:
            query_vector: Query vector
            k: Number of neighbors to return
            ef: Size of the dynamic candidate list (higher = better recall, slower)
                Defaults to max(k, 50)

        Returns:
            Tuple of (indices, distances) arrays
        """
        if not self.is_built or self.current_count == 0:
            return np.array([]), np.array([])

        # Set ef parameter
        if ef is None:
            ef = max(k, 50)
        self.index.set_ef(ef)

        # Ensure k doesn't exceed number of items
        k = min(k, self.current_count)

        # Query the index
        query_vector = query_vector.reshape(1, -1)
        indices, distances = self.index.knn_query(query_vector, k=k)

        return indices[0], distances[0]

    def rebuild(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """
        Completely rebuild the index from scratch.

        Args:
            vectors: Matrix of all vectors
            ids: Optional array of integer IDs
        """
        # Reinitialize index
        self.index = hnswlib.Index(space=self.space, dim=self.dimension)
        self.index.init_index(
            max_elements=max(self.max_elements, len(vectors)),
            ef_construction=self.ef_construction,
            M=self.M
        )
        self.current_count = 0
        self.is_built = False

        # Build with new data
        self.build(vectors, ids)

    def save(self, filepath: str):
        """Save index to disk."""
        if self.is_built:
            self.index.save_index(filepath)

    def load(self, filepath: str, max_elements: Optional[int] = None):
        """
        Load index from disk.

        Args:
            filepath: Path to saved index file
            max_elements: Maximum number of elements (uses default if not specified)
        """
        if max_elements is None:
            max_elements = self.max_elements

        self.index.load_index(filepath, max_elements=max_elements)
        self.current_count = self.index.get_current_count()
        self.is_built = True

    def get_count(self) -> int:
        """Get number of vectors in index."""
        return self.current_count


class BruteForceIndex:
    """
    Simple brute force search for exact nearest neighbors.
    Useful for small datasets or when exact results are needed.
    """

    def __init__(self, dimension: int, metric: str = 'cosine'):
        """
        Initialize brute force index.

        Args:
            dimension: Vector dimensionality
            metric: Distance metric to use
        """
        self.dimension = dimension
        self.metric = metric
        self.vectors = None
        self.ids = None

    def build(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """Store vectors for brute force search."""
        self.vectors = vectors
        if ids is None:
            self.ids = np.arange(len(vectors))
        else:
            self.ids = ids

    def add_items(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """Add vectors to existing collection."""
        if self.vectors is None:
            self.build(vectors, ids)
        else:
            if ids is None:
                start_id = len(self.vectors)
                ids = np.arange(start_id, start_id + len(vectors))

            self.vectors = np.vstack([self.vectors, vectors])
            self.ids = np.concatenate([self.ids, ids])

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        **kwargs
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for k nearest neighbors using brute force.

        Args:
            query_vector: Query vector
            k: Number of neighbors to return

        Returns:
            Tuple of (indices, distances) arrays
        """
        if self.vectors is None or len(self.vectors) == 0:
            return np.array([]), np.array([])

        # Calculate distances based on metric
        if self.metric == 'cosine':
            # Normalize vectors
            query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-10)
            vectors_norm = self.vectors / (np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-10)
            similarities = np.dot(vectors_norm, query_norm)
            # Convert to distances (lower is better)
            distances = 1 - similarities
        elif self.metric == 'l2' or self.metric == 'euclidean':
            distances = np.linalg.norm(self.vectors - query_vector, axis=1)
        elif self.metric == 'ip' or self.metric == 'dot':
            # Inner product (negate so lower is better for consistency)
            distances = -np.dot(self.vectors, query_vector)
        else:
            raise ValueError(f"Unknown metric: {self.metric}")

        # Get top k
        k = min(k, len(self.vectors))
        top_k_indices = np.argpartition(distances, k)[:k]
        top_k_indices = top_k_indices[np.argsort(distances[top_k_indices])]

        return self.ids[top_k_indices], distances[top_k_indices]

    def get_count(self) -> int:
        """Get number of vectors in index."""
        return 0 if self.vectors is None else len(self.vectors)

    def rebuild(self, vectors: np.ndarray, ids: Optional[np.ndarray] = None):
        """Rebuild index (same as build for brute force)."""
        self.build(vectors, ids)
