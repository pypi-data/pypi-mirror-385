"""Embedding models for Nexus AI SDK."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage information for embedding requests."""

    prompt_tokens: int = Field(..., description="Number of input tokens")
    total_tokens: int = Field(..., description="Total number of tokens")


class EmbeddingObject(BaseModel):
    """Individual embedding object."""

    object: str = Field(default="embedding", description="Object type")
    embedding: List[float] = Field(..., description="The embedding vector")
    index: int = Field(..., description="Index of this embedding in the batch")


class EmbeddingResponse(BaseModel):
    """Response from embedding API - OpenAI compatible."""

    object: str = Field(default="list", description="Response object type")
    data: List[EmbeddingObject] = Field(..., description="List of embedding objects")
    model: str = Field(..., description="Model used for embedding")
    usage: TokenUsage = Field(..., description="Token usage information")


class EmbeddingBatchInfo(BaseModel):
    """Batch processing information."""

    total_texts: int = Field(..., description="Total number of input texts")
    batch_size: int = Field(..., description="Batch size used for processing")
    processing_time: Optional[float] = Field(None, description="Total processing time in seconds")
    batches_processed: int = Field(..., description="Number of batches processed")


class EmbeddingBatchResponse(BaseModel):
    """Response from batch embedding processing."""

    object: str = Field(default="list", description="Response object type")
    data: List[EmbeddingObject] = Field(..., description="List of embedding objects")
    model: str = Field(..., description="Model used for embedding")
    usage: TokenUsage = Field(..., description="Token usage information")
    batch_info: EmbeddingBatchInfo = Field(..., description="Batch processing information")


class EmbeddingModel(BaseModel):
    """Available embedding model information."""

    id: str = Field(..., description="Model identifier")
    object: str = Field(default="model", description="Object type")
    created: int = Field(..., description="Model creation timestamp")
    owned_by: str = Field(..., description="Model owner")
    dimensions: int = Field(..., description="Embedding dimensions")
    max_input: int = Field(..., description="Maximum input length")
    description: str = Field(..., description="Model description")


class EmbeddingModelListResponse(BaseModel):
    """Response from model list endpoint."""

    object: str = Field(default="list", description="Response object type")
    data: List[EmbeddingModel] = Field(..., description="List of available models")


class EmbeddingHealthResponse(BaseModel):
    """Response from embedding health check."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    embedding_service: str = Field(..., description="Embedding service status")
    model_dimension: int = Field(..., description="Default model dimension")
    timestamp: float = Field(..., description="Health check timestamp")