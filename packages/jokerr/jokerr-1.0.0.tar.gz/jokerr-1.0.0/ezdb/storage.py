"""
Core storage engine for vectors and metadata
"""
import numpy as np
from typing import List, Dict, Any, Optional
import uuid


class VectorStore:
    """
    In-memory storage for vectors and their metadata.
    Each vector gets a unique ID and can have associated metadata.
    """

    def __init__(self, dimension: int):
        """
        Initialize vector store.

        Args:
            dimension: Dimensionality of vectors to store
        """
        self.dimension = dimension
        self.vectors = []  # List of numpy arrays
        self.metadata = []  # List of metadata dictionaries
        self.documents = []  # List of original documents/text
        self.ids = []  # List of unique IDs
        self._id_to_index = {}  # Map ID to index for fast lookup

    def insert(
        self,
        vector: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
        vector_id: Optional[str] = None,
        document: Optional[str] = None
    ) -> str:
        """
        Insert a vector with optional metadata and document.

        Args:
            vector: Vector to insert (must match dimension)
            metadata: Optional metadata dictionary
            vector_id: Optional custom ID (auto-generated if not provided)
            document: Optional original document/text

        Returns:
            ID of inserted vector

        Raises:
            ValueError: If vector dimension doesn't match
        """
        vector = np.array(vector, dtype=np.float32)

        if len(vector) != self.dimension:
            raise ValueError(
                f"Vector dimension {len(vector)} doesn't match "
                f"store dimension {self.dimension}"
            )

        # Generate ID if not provided
        if vector_id is None:
            vector_id = str(uuid.uuid4())
        elif vector_id in self._id_to_index:
            raise ValueError(f"Vector ID {vector_id} already exists")

        # Store vector, metadata, and document
        index = len(self.vectors)
        self.vectors.append(vector)
        self.metadata.append(metadata or {})
        self.documents.append(document)
        self.ids.append(vector_id)
        self._id_to_index[vector_id] = index

        return vector_id

    def insert_batch(
        self,
        vectors: List[np.ndarray],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        documents: Optional[List[str]] = None
    ) -> List[str]:
        """
        Insert multiple vectors at once.

        Args:
            vectors: List of vectors to insert
            metadata_list: Optional list of metadata dictionaries
            ids: Optional list of custom IDs
            documents: Optional list of original documents/text

        Returns:
            List of IDs for inserted vectors
        """
        if metadata_list is None:
            metadata_list = [None] * len(vectors)
        if ids is None:
            ids = [None] * len(vectors)
        if documents is None:
            documents = [None] * len(vectors)

        inserted_ids = []
        for vector, metadata, vector_id, document in zip(vectors, metadata_list, ids, documents):
            inserted_id = self.insert(vector, metadata, vector_id, document)
            inserted_ids.append(inserted_id)

        return inserted_ids

    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Get vector, metadata, and document by ID.

        Args:
            vector_id: ID of vector to retrieve

        Returns:
            Dictionary with 'id', 'vector', 'metadata', and 'document', or None if not found
        """
        if vector_id not in self._id_to_index:
            return None

        index = self._id_to_index[vector_id]
        return {
            'id': vector_id,
            'vector': self.vectors[index],
            'metadata': self.metadata[index],
            'document': self.documents[index]
        }

    def update(
        self,
        vector_id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> bool:
        """
        Update an existing vector's data, metadata, or document.

        Args:
            vector_id: ID of vector to update
            vector: Optional new vector (None to keep existing)
            metadata: Optional new metadata (None to keep existing)
            document: Optional new document (None to keep existing)

        Returns:
            True if updated, False if not found

        Raises:
            ValueError: If vector dimension doesn't match
        """
        if vector_id not in self._id_to_index:
            return False

        index = self._id_to_index[vector_id]

        # Update vector if provided
        if vector is not None:
            vector = np.array(vector, dtype=np.float32)
            if len(vector) != self.dimension:
                raise ValueError(
                    f"Vector dimension {len(vector)} doesn't match "
                    f"store dimension {self.dimension}"
                )
            self.vectors[index] = vector

        # Update metadata if provided
        if metadata is not None:
            self.metadata[index] = metadata

        # Update document if provided
        if document is not None:
            self.documents[index] = document

        return True

    def upsert(
        self,
        vector: np.ndarray,
        vector_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        document: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Insert or update a vector (upsert = update or insert).

        Args:
            vector: Vector to insert/update
            vector_id: ID of vector (required for upsert)
            metadata: Optional metadata dictionary
            document: Optional original document/text

        Returns:
            Tuple of (vector_id, was_update) where was_update is True if existing vector was updated

        Raises:
            ValueError: If vector dimension doesn't match or vector_id not provided
        """
        if vector_id is None:
            raise ValueError("vector_id is required for upsert operation")

        # Check if vector exists
        if vector_id in self._id_to_index:
            # Update existing vector
            self.update(vector_id, vector, metadata, document)
            return vector_id, True
        else:
            # Insert new vector
            self.insert(vector, metadata, vector_id, document)
            return vector_id, False

    def delete(self, vector_id: str) -> bool:
        """
        Delete a vector by ID.

        Args:
            vector_id: ID of vector to delete

        Returns:
            True if deleted, False if not found
        """
        if vector_id not in self._id_to_index:
            return False

        index = self._id_to_index[vector_id]

        # Remove from lists
        del self.vectors[index]
        del self.metadata[index]
        del self.documents[index]
        del self.ids[index]

        # Rebuild index mapping
        self._id_to_index = {vid: i for i, vid in enumerate(self.ids)}

        return True

    def get_all_vectors(self) -> np.ndarray:
        """
        Get all vectors as a numpy matrix.

        Returns:
            2D numpy array where each row is a vector
        """
        if not self.vectors:
            return np.array([]).reshape(0, self.dimension)
        return np.vstack(self.vectors)

    def get_all_metadata(self) -> List[Dict[str, Any]]:
        """Get all metadata as a list."""
        return self.metadata.copy()

    def get_all_documents(self) -> List[Optional[str]]:
        """Get all documents as a list."""
        return self.documents.copy()

    def get_all_ids(self) -> List[str]:
        """Get all vector IDs."""
        return self.ids.copy()

    def size(self) -> int:
        """Get number of vectors stored."""
        return len(self.vectors)

    def clear(self):
        """Remove all vectors, metadata, and documents."""
        self.vectors.clear()
        self.metadata.clear()
        self.documents.clear()
        self.ids.clear()
        self._id_to_index.clear()

    def _match_condition(self, value: Any, condition: Any) -> bool:
        """
        Check if a value matches a filter condition.

        Args:
            value: The value to check
            condition: The condition to match (can be a value or dict with operators)

        Returns:
            True if condition matches

        Supported operators:
            - $eq: Equal to
            - $ne: Not equal to
            - $gt: Greater than
            - $gte: Greater than or equal to
            - $lt: Less than
            - $lte: Less than or equal to
            - $in: In list
            - $nin: Not in list
            - $exists: Field exists (value is boolean)
            - $regex: Regex match (for strings)
        """
        # If condition is not a dict, treat as equality check
        if not isinstance(condition, dict):
            return value == condition

        # Handle operator-based conditions
        for op, op_value in condition.items():
            if op == "$eq":
                if value != op_value:
                    return False
            elif op == "$ne":
                if value == op_value:
                    return False
            elif op == "$gt":
                if not (value > op_value):
                    return False
            elif op == "$gte":
                if not (value >= op_value):
                    return False
            elif op == "$lt":
                if not (value < op_value):
                    return False
            elif op == "$lte":
                if not (value <= op_value):
                    return False
            elif op == "$in":
                if value not in op_value:
                    return False
            elif op == "$nin":
                if value in op_value:
                    return False
            elif op == "$exists":
                # This is handled at the key level, not here
                pass
            elif op == "$regex":
                import re
                if not isinstance(value, str):
                    return False
                if not re.search(op_value, value):
                    return False
            else:
                # Unknown operator, treat as key name (backward compatibility)
                return value == condition

        return True

    def filter_by_metadata(
        self,
        filters: Dict[str, Any]
    ) -> List[int]:
        """
        Get indices of vectors matching metadata filters with query operators.

        Args:
            filters: Dictionary of key-value pairs or operator queries

        Returns:
            List of indices matching all filters

        Examples:
            Simple equality: {"category": "tech"}
            Operators: {"age": {"$gte": 18, "$lt": 65}}
            In list: {"status": {"$in": ["active", "pending"]}}
            Exists: {"email": {"$exists": True}}
            Regex: {"name": {"$regex": "^John"}}
        """
        matching_indices = []

        for i, meta in enumerate(self.metadata):
            matches = True

            for key, condition in filters.items():
                # Handle $exists operator
                if isinstance(condition, dict) and "$exists" in condition:
                    exists = key in meta
                    if exists != condition["$exists"]:
                        matches = False
                        break
                    # If exists check passes and it's the only condition, continue
                    if len(condition) == 1:
                        continue
                    # Otherwise, check other conditions if key exists
                    if not exists:
                        matches = False
                        break

                # Check if key exists (for other operators)
                if key not in meta:
                    matches = False
                    break

                # Check condition
                if not self._match_condition(meta[key], condition):
                    matches = False
                    break

            if matches:
                matching_indices.append(i)

        return matching_indices
