"""Embedding resource module."""

from typing import Union, List, Optional, Dict, Any
import time
from nexusai.models.embedding import (
    EmbeddingResponse,
    EmbeddingBatchResponse,
    EmbeddingModelListResponse,
    EmbeddingHealthResponse,
    EmbeddingObject,
    TokenUsage,
    EmbeddingBatchInfo,
)
from nexusai.error import NexusAIError


class EmbeddingsResource:
    """
    Text embedding resource.

    Provides methods for converting text into high-dimensional vectors
    using state-of-the-art embedding models. Supports both single text
    and batch processing with OpenAI-compatible API design.

    Example:
        ```python
        from nexusai import NexusAIClient

        client = NexusAIClient(api_key="your-api-key")

        # Single text embedding
        response = client.embeddings.create(
            input="你好，这是一个测试文本",
            model="BAAI/bge-base-zh-v1.5"
        )
        vector = response.data[0].embedding

        # Batch processing
        response = client.embeddings.create(
            input=["文本1", "文本2", "文本3"],
            model="BAAI/bge-base-zh-v1.5"
        )
        vectors = [item.embedding for item in response.data]
        ```
    """

    def __init__(self, client):
        """
        Initialize embedding resource.

        Args:
            client: InternalClient instance
        """
        self._client = client

    def create(
        self,
        input: Union[str, List[str]],
        model: str = "BAAI/bge-base-zh-v1.5",
        encoding_format: str = "float",
        dimensions: Optional[int] = None,
        user: Optional[str] = None,
    ) -> Union[EmbeddingResponse, EmbeddingBatchResponse]:
        """
        Create embeddings for text input.

        Args:
            input: Text string or list of text strings to embed
            model: Embedding model to use. Options:
                  - "BAAI/bge-base-zh-v1.5" (768 dimensions, default)
                  - "BAAI/bge-large-zh-v1.5" (1024 dimensions)
            encoding_format: Format of the embeddings. Currently only "float" is supported.
            dimensions: Number of dimensions in output embeddings (read-only, determined by model)
            user: Unique identifier for the end-user (optional, for tracking)

        Returns:
            EmbeddingResponse for single input or EmbeddingBatchResponse for list input

        Raises:
            NexusAIError: If the request fails or model is not available

        Example:
            ```python
            # Single text
            response = client.embeddings.create(
                input="你好世界",
                model="BAAI/bge-base-zh-v1.5"
            )

            # Multiple texts
            response = client.embeddings.create(
                input=["文本1", "文本2", "文本3"]
            )
            ```
        """
        # Validate inputs
        if not input:
            raise NexusAIError("Input cannot be empty")

        if encoding_format != "float":
            raise NexusAIError("Only 'float' encoding format is currently supported")

        # Prepare request payload
        payload = {
            "input": input,
            "model": model,
        }

        # Add optional parameters
        if user:
            payload["user"] = user

        try:
            # Make API request
            response = self._client.request("POST", "/embeddings", json_data=payload)

            # Parse response based on input type
            if isinstance(input, str):
                return self._parse_single_response(response, model)
            else:
                return self._parse_batch_response(response, model, len(input))

        except Exception as e:
            raise NexusAIError(f"Embedding request failed: {str(e)}") from e

    def create_batch(
        self,
        texts: List[str],
        model: str = "BAAI/bge-base-zh-v1.5",
        batch_size: int = 32,
        max_workers: int = 4,
    ) -> EmbeddingBatchResponse:
        """
        Create embeddings for a large batch of texts with optimized processing.

        This method uses the dedicated batch endpoint for better performance
        when processing large numbers of texts.

        Args:
            texts: List of text strings to embed
            model: Embedding model to use
            batch_size: Number of texts to process per batch (max 100)
            max_workers: Number of concurrent workers (currently unused, reserved for future async support)

        Returns:
            EmbeddingBatchResponse with all embeddings and batch processing info

        Raises:
            NexusAIError: If the request fails

        Example:
            ```python
            # Large batch processing
            texts = ["文本{}".format(i) for i in range(1000)]
            response = client.embeddings.create_batch(
                texts=texts,
                batch_size=50
            )
            ```
        """
        if not texts:
            raise NexusAIError("Texts list cannot be empty")

        if batch_size > 100:
            raise NexusAIError("Batch size cannot exceed 100")

        start_time = time.time()

        # Prepare request payload
        payload = {
            "texts": texts,
            "model": model,
            "batch_size": batch_size,
        }

        try:
            # Use dedicated batch endpoint
            response = self._client.request("POST", "/embeddings/batch", json_data=payload)

            processing_time = time.time() - start_time

            return self._parse_batch_response(
                response,
                model,
                len(texts),
                batch_size=batch_size,
                processing_time=processing_time
            )

        except Exception as e:
            raise NexusAIError(f"Batch embedding request failed: {str(e)}") from e

    def list_models(self) -> EmbeddingModelListResponse:
        """
        List available embedding models.

        Returns:
            EmbeddingModelListResponse with list of available models

        Raises:
            NexusAIError: If the request fails

        Example:
            ```python
            models = client.embeddings.list_models()
            for model in models.data:
                print(f"{model.id}: {model.dimensions} dimensions")
            ```
        """
        try:
            response = self._client.request("GET", "/embeddings/models")
            return EmbeddingModelListResponse.model_validate(response)
        except Exception as e:
            raise NexusAIError(f"Failed to list embedding models: {str(e)}") from e

    def health_check(self) -> EmbeddingHealthResponse:
        """
        Check embedding service health.

        Returns:
            EmbeddingHealthResponse with service status

        Raises:
            NexusAIError: If the request fails

        Example:
            ```python
            health = client.embeddings.health_check()
            print(f"Service status: {health.status}")
            ```
        """
        try:
            response = self._client.request("GET", "/embeddings/health")
            return EmbeddingHealthResponse.model_validate(response)
        except Exception as e:
            raise NexusAIError(f"Health check failed: {str(e)}") from e

    def _parse_single_response(self, response_data: Dict[str, Any], model: str) -> EmbeddingResponse:
        """Parse response for single text input."""
        return EmbeddingResponse(
            object="list",
            data=[
                EmbeddingObject(
                    object="embedding",
                    embedding=item["embedding"],
                    index=item["index"]
                ) for item in response_data["data"]
            ],
            model=model,
            usage=TokenUsage(
                prompt_tokens=response_data["usage"]["prompt_tokens"],
                total_tokens=response_data["usage"]["total_tokens"]
            )
        )

    def _parse_batch_response(
        self,
        response_data: Dict[str, Any],
        model: str,
        total_texts: int,
        batch_size: int = 1,
        processing_time: Optional[float] = None
    ) -> EmbeddingBatchResponse:
        """Parse response for batch input."""
        # Calculate number of batches
        batches_processed = (total_texts + batch_size - 1) // batch_size

        # Handle different response formats for batch endpoints
        if "vectors" in response_data:
            # Optimized batch endpoint format
            embedding_data = [
                EmbeddingObject(
                    object="embedding",
                    embedding=vector,
                    index=i
                ) for i, vector in enumerate(response_data["vectors"])
            ]
        else:
            # Standard embedding endpoint format
            embedding_data = [
                EmbeddingObject(
                    object="embedding",
                    embedding=item["embedding"],
                    index=item["index"]
                ) for item in response_data["data"]
            ]

        return EmbeddingBatchResponse(
            object="list",
            data=embedding_data,
            model=model,
            usage=TokenUsage(
                prompt_tokens=response_data["usage"]["prompt_tokens"],
                total_tokens=response_data["usage"]["total_tokens"]
            ),
            batch_info=EmbeddingBatchInfo(
                total_texts=total_texts,
                batch_size=batch_size,
                processing_time=processing_time,
                batches_processed=batches_processed
            )
        )