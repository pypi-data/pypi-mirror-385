"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional, Union


class InsertRequest(BaseModel):
    """Request model for inserting a vector"""
    vector: Optional[List[float]] = Field(None, description="Vector to insert (required if text/image not provided)")
    text: Optional[str] = Field(None, description="Text to auto-embed (required if vector/image not provided)")
    image: Optional[str] = Field(None, description="Image to auto-embed: file path, URL, or base64 data URI")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    id: Optional[str] = Field(None, description="Optional custom ID")
    document: Optional[str] = Field(None, description="Optional document text to store")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "vector": [0.1, 0.2, 0.3],
                    "metadata": {"text": "Hello world", "category": "greeting"},
                    "id": "doc-123"
                },
                {
                    "text": "Hello world",
                    "metadata": {"category": "greeting"},
                    "id": "doc-124"
                }
            ]
        }
    }


class InsertResponse(BaseModel):
    """Response model for insert operation"""
    id: str = Field(..., description="ID of inserted vector")
    success: bool = Field(True, description="Whether operation succeeded")


class BatchInsertRequest(BaseModel):
    """Request model for batch inserting vectors"""
    vectors: List[List[float]] = Field(..., description="List of vectors to insert")
    metadata_list: Optional[List[Dict[str, Any]]] = Field(None, description="List of metadata")
    ids: Optional[List[str]] = Field(None, description="List of custom IDs")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "vectors": [[0.1, 0.2], [0.3, 0.4]],
                    "metadata_list": [{"text": "Doc 1"}, {"text": "Doc 2"}]
                }
            ]
        }
    }


class BatchInsertResponse(BaseModel):
    """Response model for batch insert operation"""
    ids: List[str] = Field(..., description="IDs of inserted vectors")
    count: int = Field(..., description="Number of vectors inserted")
    success: bool = Field(True, description="Whether operation succeeded")


class SearchRequest(BaseModel):
    """Request model for searching vectors"""
    vector: Optional[List[float]] = Field(None, description="Query vector (required if text/image not provided)")
    text: Optional[str] = Field(None, description="Query text to auto-embed (required if vector/image not provided)")
    image: Optional[str] = Field(None, description="Query image to auto-embed: file path, URL, or base64 data URI")
    top_k: int = Field(10, ge=1, le=1000, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    ef: Optional[int] = Field(None, description="HNSW search parameter")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "vector": [0.1, 0.2, 0.3],
                    "top_k": 5,
                    "filters": {"category": "tech"}
                },
                {
                    "text": "machine learning",
                    "top_k": 5,
                    "filters": {"category": "tech"}
                }
            ]
        }
    }


class SearchResultItem(BaseModel):
    """Single search result"""
    id: str = Field(..., description="Vector ID")
    score: float = Field(..., description="Similarity score")
    metadata: Dict[str, Any] = Field(..., description="Vector metadata")
    vector: Optional[List[float]] = Field(None, description="Vector data (optional)")
    document: Optional[str] = Field(None, description="Original document/text (if stored)")


class SearchResponse(BaseModel):
    """Response model for search operation"""
    results: List[SearchResultItem] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results returned")
    success: bool = Field(True, description="Whether operation succeeded")


class DocumentSearchRequest(BaseModel):
    """Request model for full-text document search"""
    query: str = Field(..., description="Text query to search for in documents")
    top_k: int = Field(10, ge=1, le=1000, description="Number of results to return")
    case_sensitive: bool = Field(False, description="Whether search is case-sensitive")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "machine learning",
                    "top_k": 5
                },
                {
                    "query": "Python programming",
                    "top_k": 10,
                    "case_sensitive": False,
                    "filters": {"category": "tech"}
                }
            ]
        }
    }


class GetResponse(BaseModel):
    """Response model for get operation"""
    id: str = Field(..., description="Vector ID")
    vector: List[float] = Field(..., description="Vector data")
    metadata: Dict[str, Any] = Field(..., description="Vector metadata")
    document: Optional[str] = Field(None, description="Original document/text (if stored)")
    success: bool = Field(True, description="Whether operation succeeded")


class UpdateRequest(BaseModel):
    """Request model for updating a vector"""
    vector: Optional[List[float]] = Field(None, description="New vector (None to keep existing)")
    text: Optional[str] = Field(None, description="New text to auto-embed (None to keep existing)")
    image: Optional[str] = Field(None, description="New image to auto-embed (None to keep existing)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="New metadata (None to keep existing)")
    document: Optional[str] = Field(None, description="New document (None to keep existing)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "metadata": {"category": "updated", "version": 2}
                },
                {
                    "vector": [0.5, 0.6, 0.7],
                    "metadata": {"updated": True}
                },
                {
                    "text": "Updated content",
                    "metadata": {"category": "updated"}
                }
            ]
        }
    }


class UpdateResponse(BaseModel):
    """Response model for update operation"""
    id: str = Field(..., description="ID of updated vector")
    success: bool = Field(..., description="Whether update succeeded")


class UpsertRequest(BaseModel):
    """Request model for upserting a vector"""
    id: str = Field(..., description="Vector ID (required for upsert)")
    vector: Optional[List[float]] = Field(None, description="Vector to upsert (required if text/image not provided)")
    text: Optional[str] = Field(None, description="Text to auto-embed (required if vector/image not provided)")
    image: Optional[str] = Field(None, description="Image to auto-embed (required if vector/text not provided)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata")
    document: Optional[str] = Field(None, description="Optional document")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "doc-123",
                    "vector": [0.1, 0.2, 0.3],
                    "metadata": {"category": "tech"}
                },
                {
                    "id": "doc-124",
                    "text": "Machine learning tutorial",
                    "metadata": {"category": "tech"}
                }
            ]
        }
    }


class UpsertResponse(BaseModel):
    """Response model for upsert operation"""
    id: str = Field(..., description="ID of upserted vector")
    updated: bool = Field(..., description="True if existing vector was updated, False if inserted")
    success: bool = Field(True, description="Whether operation succeeded")


class DeleteResponse(BaseModel):
    """Response model for delete operation"""
    id: str = Field(..., description="ID of deleted vector")
    success: bool = Field(..., description="Whether deletion succeeded")


class StatsResponse(BaseModel):
    """Response model for database statistics"""
    dimension: int = Field(..., description="Vector dimension")
    metric: str = Field(..., description="Similarity metric")
    index_type: str = Field(..., description="Index type")
    size: int = Field(..., description="Number of vectors")
    index_count: int = Field(..., description="Number of vectors in index")
    index_dirty: bool = Field(..., description="Whether index needs rebuilding")


class CreateCollectionRequest(BaseModel):
    """Request model for creating a collection"""
    name: str = Field(..., description="Collection name")
    dimension: Union[int, None] = Field(default=None, description="Vector dimension (required if embedding_function not provided)")
    metric: str = Field(default="cosine", description="Similarity metric")
    index_type: str = Field(default="hnsw", description="Index type")
    embedding_function: Union[str, None] = Field(default=None, description="Auto-embedding function (e.g., 'default', 'sentence-transformers/all-MiniLM-L6-v2')")

    @model_validator(mode='after')
    def validate_dimension_or_embedding(self):
        """Validate that either dimension or embedding_function is provided"""
        if self.dimension is None and self.embedding_function is None:
            raise ValueError("Either 'dimension' or 'embedding_function' must be provided")
        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "documents",
                    "dimension": 384,
                    "metric": "cosine"
                },
                {
                    "name": "auto_docs",
                    "embedding_function": "default",
                    "metric": "cosine"
                }
            ]
        }
    }


class CreateCollectionResponse(BaseModel):
    """Response model for create collection"""
    name: str = Field(..., description="Collection name")
    success: bool = Field(True, description="Whether operation succeeded")


class ListCollectionsResponse(BaseModel):
    """Response model for listing collections"""
    collections: List[str] = Field(..., description="List of collection names")
    count: int = Field(..., description="Number of collections")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    success: bool = Field(False, description="Always false for errors")


class SQLQueryRequest(BaseModel):
    """Request model for SQL query execution"""
    query: str = Field(..., description="SQL query to execute on collection metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "SELECT * FROM movie_ratings"
                },
                {
                    "query": "SELECT title, year, rating FROM movie_ratings WHERE rating >= 8.0"
                },
                {
                    "query": "SELECT * FROM movie_ratings WHERE genre = 'Action' ORDER BY rating DESC LIMIT 10"
                }
            ]
        }
    }


class SQLQueryResponse(BaseModel):
    """Response model for SQL query execution"""
    columns: List[str] = Field(..., description="Column names")
    rows: List[Dict[str, Any]] = Field(..., description="Query result rows")
    total: int = Field(..., description="Total rows matching query (before LIMIT)")
    returned: int = Field(..., description="Number of rows returned")
    query: str = Field(..., description="Executed query")
    success: bool = Field(True, description="Whether operation succeeded")
