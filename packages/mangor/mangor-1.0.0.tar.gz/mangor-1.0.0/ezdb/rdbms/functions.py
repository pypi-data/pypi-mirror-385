"""
SQL Functions for EzDB RDBMS
Includes vector similarity functions and standard SQL functions
"""

import numpy as np
from typing import Any, Union, List
from ..similarity import SimilarityMetric, calculate_similarity


class VectorFunctions:
    """Vector-specific SQL functions"""

    @staticmethod
    def vector_similarity(
        vector1: Union[np.ndarray, List[float]],
        vector2: Union[np.ndarray, List[float]],
        metric: str = 'cosine'
    ) -> float:
        """
        Calculate similarity between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector
            metric: Similarity metric ('cosine', 'euclidean', 'dot_product')

        Returns:
            Similarity score

        Usage in SQL:
            SELECT vector_similarity(embedding, [0.1, 0.2, ...]) as score
            FROM products
            WHERE score > 0.8
        """
        if vector1 is None or vector2 is None:
            return 0.0

        vec1 = np.array(vector1, dtype=np.float32)
        vec2 = np.array(vector2, dtype=np.float32)

        metric_enum = SimilarityMetric(metric.lower())
        similarity = calculate_similarity(vec1, vec2, metric_enum)

        return float(similarity)

    @staticmethod
    def vector_distance(
        vector1: Union[np.ndarray, List[float]],
        vector2: Union[np.ndarray, List[float]],
        metric: str = 'euclidean'
    ) -> float:
        """
        Calculate distance between two vectors.

        Args:
            vector1: First vector
            vector2: Second vector
            metric: Distance metric ('euclidean', 'cosine', 'manhattan')

        Returns:
            Distance value (lower = more similar)

        Usage in SQL:
            SELECT vector_distance(embedding, [0.1, 0.2, ...]) as dist
            FROM products
            ORDER BY dist
            LIMIT 10
        """
        if vector1 is None or vector2 is None:
            return float('inf')

        vec1 = np.array(vector1, dtype=np.float32)
        vec2 = np.array(vector2, dtype=np.float32)

        if metric.lower() == 'euclidean':
            return float(np.linalg.norm(vec1 - vec2))
        elif metric.lower() == 'manhattan':
            return float(np.sum(np.abs(vec1 - vec2)))
        elif metric.lower() == 'cosine':
            # Cosine distance = 1 - cosine similarity
            sim = calculate_similarity(vec1, vec2, SimilarityMetric.COSINE)
            return float(1.0 - sim)
        else:
            raise ValueError(f"Unknown distance metric: {metric}")

    @staticmethod
    def vector_normalize(vector: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Normalize a vector to unit length.

        Args:
            vector: Input vector

        Returns:
            Normalized vector

        Usage in SQL:
            SELECT vector_normalize(embedding) as normalized
            FROM products
        """
        if vector is None:
            return None

        vec = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(vec)

        if norm == 0:
            return vec

        return vec / norm

    @staticmethod
    def vector_dot(
        vector1: Union[np.ndarray, List[float]],
        vector2: Union[np.ndarray, List[float]]
    ) -> float:
        """
        Calculate dot product of two vectors.

        Args:
            vector1: First vector
            vector2: Second vector

        Returns:
            Dot product

        Usage in SQL:
            SELECT vector_dot(v1, v2) as dot_prod
            FROM vectors
        """
        if vector1 is None or vector2 is None:
            return 0.0

        vec1 = np.array(vector1, dtype=np.float32)
        vec2 = np.array(vector2, dtype=np.float32)

        return float(np.dot(vec1, vec2))

    @staticmethod
    def vector_magnitude(vector: Union[np.ndarray, List[float]]) -> float:
        """
        Calculate magnitude (L2 norm) of a vector.

        Args:
            vector: Input vector

        Returns:
            Magnitude

        Usage in SQL:
            SELECT vector_magnitude(embedding) as mag
            FROM products
        """
        if vector is None:
            return 0.0

        vec = np.array(vector, dtype=np.float32)
        return float(np.linalg.norm(vec))


class ScalarFunctions:
    """Standard SQL scalar functions"""

    @staticmethod
    def upper(text: str) -> str:
        """Convert text to uppercase"""
        return text.upper() if text else None

    @staticmethod
    def lower(text: str) -> str:
        """Convert text to lowercase"""
        return text.lower() if text else None

    @staticmethod
    def length(text: str) -> int:
        """Get length of text"""
        return len(text) if text else 0

    @staticmethod
    def abs(value: Union[int, float]) -> Union[int, float]:
        """Absolute value"""
        return abs(value) if value is not None else None

    @staticmethod
    def round(value: float, decimals: int = 0) -> float:
        """Round to specified decimals"""
        return round(value, decimals) if value is not None else None

    @staticmethod
    def ceil(value: float) -> int:
        """Round up to nearest integer"""
        import math
        return math.ceil(value) if value is not None else None

    @staticmethod
    def floor(value: float) -> int:
        """Round down to nearest integer"""
        import math
        return math.floor(value) if value is not None else None

    @staticmethod
    def coalesce(*values) -> Any:
        """Return first non-NULL value"""
        for val in values:
            if val is not None:
                return val
        return None


class AggregateFunctions:
    """SQL aggregate functions (for GROUP BY)"""

    @staticmethod
    def count(values: List[Any]) -> int:
        """Count non-NULL values"""
        return sum(1 for v in values if v is not None)

    @staticmethod
    def sum(values: List[Union[int, float]]) -> Union[int, float]:
        """Sum of values"""
        filtered = [v for v in values if v is not None]
        return sum(filtered) if filtered else None

    @staticmethod
    def avg(values: List[Union[int, float]]) -> float:
        """Average of values"""
        filtered = [v for v in values if v is not None]
        return sum(filtered) / len(filtered) if filtered else None

    @staticmethod
    def min(values: List[Any]) -> Any:
        """Minimum value"""
        filtered = [v for v in values if v is not None]
        return min(filtered) if filtered else None

    @staticmethod
    def max(values: List[Any]) -> Any:
        """Maximum value"""
        filtered = [v for v in values if v is not None]
        return max(filtered) if filtered else None

    @staticmethod
    def stddev(values: List[Union[int, float]]) -> float:
        """Standard deviation"""
        filtered = [v for v in values if v is not None]
        if not filtered:
            return None
        arr = np.array(filtered)
        return float(np.std(arr))

    @staticmethod
    def variance(values: List[Union[int, float]]) -> float:
        """Variance"""
        filtered = [v for v in values if v is not None]
        if not filtered:
            return None
        arr = np.array(filtered)
        return float(np.var(arr))


# Function registry for easy lookup
FUNCTION_REGISTRY = {
    # Vector functions
    'vector_similarity': VectorFunctions.vector_similarity,
    'vector_distance': VectorFunctions.vector_distance,
    'vector_normalize': VectorFunctions.vector_normalize,
    'vector_dot': VectorFunctions.vector_dot,
    'vector_magnitude': VectorFunctions.vector_magnitude,

    # Scalar functions
    'upper': ScalarFunctions.upper,
    'lower': ScalarFunctions.lower,
    'length': ScalarFunctions.length,
    'abs': ScalarFunctions.abs,
    'round': ScalarFunctions.round,
    'ceil': ScalarFunctions.ceil,
    'floor': ScalarFunctions.floor,
    'coalesce': ScalarFunctions.coalesce,

    # Aggregate functions
    'count': AggregateFunctions.count,
    'sum': AggregateFunctions.sum,
    'avg': AggregateFunctions.avg,
    'min': AggregateFunctions.min,
    'max': AggregateFunctions.max,
    'stddev': AggregateFunctions.stddev,
    'variance': AggregateFunctions.variance,
}


def call_function(func_name: str, *args, **kwargs) -> Any:
    """
    Call a SQL function by name.

    Args:
        func_name: Function name (case-insensitive)
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Function result

    Raises:
        ValueError: If function not found
    """
    func_name_lower = func_name.lower()

    if func_name_lower not in FUNCTION_REGISTRY:
        raise ValueError(f"Unknown function: {func_name}")

    func = FUNCTION_REGISTRY[func_name_lower]
    return func(*args, **kwargs)
