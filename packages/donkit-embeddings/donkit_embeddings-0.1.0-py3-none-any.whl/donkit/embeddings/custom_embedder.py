import asyncio
import json
import os
from typing import Literal

from google import genai
from google.genai import types
from langchain_core.embeddings import Embeddings
from openai import OpenAI


class CustomEmbeddings(Embeddings):
    """Custom embeddings using OpenAI-compatible API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        batch_size: int = 50,
        vector_size: int | None = None,
    ) -> None:
        """Initialize CustomEmbeddings.

        Args:
            base_url: Base URL for the OpenAI-compatible API
            api_key: API key for authentication
            model: Model name to use for embeddings
            batch_size: Batch size for embedding documents
            vector_size: Vector size for embeddings (auto-detected if None)
        """
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.__batch_size = batch_size
        self.vector_size = vector_size or self.set_vector_size()

    def set_vector_size(self) -> int:
        """Auto-detect vector size by embedding a test string."""
        text = "test"
        response = self.client.embeddings.create(
            model=self.model,
            input=[text],
        )
        return len(response.data[0].embedding)

    def embed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of texts to embed
            batch_size: Batch size (uses default if None)

        Returns:
            List of embeddings
        """
        all_embeddings: list[list[float]] = []
        batch_size = batch_size or self.__batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                )
            except Exception as e:
                raise Exception(f"Failed to embed documents: {batch}") from e
            embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(embeddings)
        return all_embeddings

    async def aembed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Async version of embed_documents."""
        return await asyncio.to_thread(self.embed_documents, texts, batch_size)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        response = self.client.embeddings.create(
            model=self.model,
            input=[text],
        )
        return response.data[0].embedding

    async def aembed_query(self, text: str) -> list[float]:
        """Async version of embed_query."""
        return await asyncio.to_thread(self.embed_query, text)


class VertexEmbeddings(Embeddings):
    """Vertex AI embeddings using google-genai SDK."""

    def __init__(
        self,
        credentials_data: dict,
        model_name: Literal[
            "text-embedding-005",
            "text-multilingual-embedding-002",
        ] = "text-multilingual-embedding-002",
        vector_size: int = 768,
        batch_size: int = 100,
    ):
        """Initialize VertexEmbeddings.

        Args:
            credentials_data: GCP service account credentials
            model_name: Vertex AI embedding model name
            vector_size: Output dimensionality for embeddings
            batch_size: Batch size for embedding documents
        """
        # Set up environment for Vertex AI
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/vertex_creds.json"
        with open("/tmp/vertex_creds.json", "w") as f:
            json.dump(credentials_data, f)

        # Create client for Vertex AI
        self._client = genai.Client(
            vertexai=True,
            project=credentials_data.get("project_id"),
            location="us-central1",
        )
        self.model_name = model_name
        self.vector_size = vector_size
        self.__batch_size = batch_size

    def embed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Embed a list of documents.

        Args:
            texts: List of texts to embed
            batch_size: Batch size (uses default if None)

        Returns:
            List of embeddings
        """
        all_embeddings: list[list[float]] = []
        batch_size = batch_size or self.__batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # Replace empty texts with placeholder
            batch = [text or "EMPTY" for text in batch]

            try:
                # Use embed_content with the new SDK
                response = self._client.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=self.vector_size,
                    ),
                )

                # Extract embeddings from response
                embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(embeddings)
            except Exception as e:
                raise Exception(f"Failed to embed documents {e} - {batch}") from e

        return all_embeddings

    async def aembed_documents(
        self, texts: list[str], batch_size: int | None = None
    ) -> list[list[float]]:
        """Async version of embed_documents."""
        all_embeddings: list[list[float]] = []
        batch_size = batch_size or self.__batch_size
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            # Replace empty texts with placeholder
            batch = [text or "EMPTY" for text in batch]

            try:
                # Use embed_content with the new SDK
                response = await self._client.aio.models.embed_content(
                    model=self.model_name,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type="RETRIEVAL_DOCUMENT",
                        output_dimensionality=self.vector_size,
                    ),
                )

                # Extract embeddings from response
                embeddings = [emb.values for emb in response.embeddings]
                all_embeddings.extend(embeddings)
            except Exception as e:
                raise Exception(f"Failed to embed documents {e} - {batch}") from e

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self._client.models.embed_content(
                model=self.model_name,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=self.vector_size,
                ),
            )
            return response.embeddings[0].values
        except Exception as e:
            raise Exception(f"Failed to embed query: {e}") from e

    async def aembed_query(self, text: str) -> list[float]:
        """Async version of embed_query."""
        try:
            response = await self._client.aio.models.embed_content(
                model=self.model_name,
                contents=[text],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=self.vector_size,
                ),
            )
            return response.embeddings[0].values
        except Exception as e:
            raise Exception(f"Failed to embed query: {e}") from e


def get_custom_embeddings_openai_api(
    base_url: str, api_key: str, model: str
) -> Embeddings:
    """Factory function for CustomEmbeddings.

    Args:
        base_url: Base URL for the OpenAI-compatible API
        api_key: API key for authentication
        model: Model name to use for embeddings

    Returns:
        CustomEmbeddings instance
    """
    return CustomEmbeddings(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )


def get_vertexai_embeddings(
    credentials_data: dict[str, str],
    *,
    model_name: Literal[
        "text-embedding-005",
        "text-multilingual-embedding-002",
    ] = "text-multilingual-embedding-002",
    vector_size: int = 768,
    batch_size: int = 100,
) -> Embeddings:
    """Factory function for VertexEmbeddings.

    Args:
        credentials_data: GCP service account credentials
        model_name: Vertex AI embedding model name
        vector_size: Output dimensionality for embeddings
        batch_size: Batch size for embedding documents

    Returns:
        VertexEmbeddings instance
    """
    return VertexEmbeddings(
        credentials_data=credentials_data,
        model_name=model_name,
        vector_size=vector_size,
        batch_size=batch_size,
    )
