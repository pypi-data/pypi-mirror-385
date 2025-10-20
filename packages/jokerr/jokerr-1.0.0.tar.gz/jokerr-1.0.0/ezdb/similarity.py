"""
Similarity metrics for vector comparison
"""
from enum import Enum
import numpy as np
from typing import Union


class SimilarityMetric(Enum):
    """Supported similarity metrics"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    Returns value between -1 and 1, where 1 means identical direction.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Cosine similarity score
    """
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    return dot_product / (norm_v1 * norm_v2)


def euclidean_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two vectors.
    Lower values mean more similar.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Euclidean distance
    """
    return np.linalg.norm(v1 - v2)


def dot_product(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculate dot product between two vectors.
    Higher values mean more similar (for normalized vectors).

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Dot product value
    """
    return np.dot(v1, v2)


def calculate_similarity(
    v1: np.ndarray,
    v2: np.ndarray,
    metric: Union[SimilarityMetric, str] = SimilarityMetric.COSINE
) -> float:
    """
    Calculate similarity between two vectors using specified metric.

    Args:
        v1: First vector
        v2: Second vector
        metric: Similarity metric to use

    Returns:
        Similarity score
    """
    if isinstance(metric, str):
        metric = SimilarityMetric(metric)

    if metric == SimilarityMetric.COSINE:
        return cosine_similarity(v1, v2)
    elif metric == SimilarityMetric.EUCLIDEAN:
        # Return negative distance so higher is better
        return -euclidean_distance(v1, v2)
    elif metric == SimilarityMetric.DOT_PRODUCT:
        return dot_product(v1, v2)
    else:
        raise ValueError(f"Unknown metric: {metric}")


def batch_similarity(
    query_vector: np.ndarray,
    vectors: np.ndarray,
    metric: Union[SimilarityMetric, str] = SimilarityMetric.COSINE
) -> np.ndarray:
    """
    Calculate similarity between a query vector and multiple vectors efficiently.

    Args:
        query_vector: Query vector (1D array)
        vectors: Matrix of vectors (2D array, each row is a vector)
        metric: Similarity metric to use

    Returns:
        Array of similarity scores
    """
    if isinstance(metric, str):
        metric = SimilarityMetric(metric)

    if metric == SimilarityMetric.COSINE:
        # Normalize vectors
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        return np.dot(vectors_norm, query_norm)

    elif metric == SimilarityMetric.EUCLIDEAN:
        # Calculate distances and return negative (so higher is better)
        distances = np.linalg.norm(vectors - query_vector, axis=1)
        return -distances

    elif metric == SimilarityMetric.DOT_PRODUCT:
        return np.dot(vectors, query_vector)

    else:
        raise ValueError(f"Unknown metric: {metric}")
