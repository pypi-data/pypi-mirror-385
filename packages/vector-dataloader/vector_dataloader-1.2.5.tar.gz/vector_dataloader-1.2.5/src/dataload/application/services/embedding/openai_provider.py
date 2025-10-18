import os
from typing import List
from dataload.interfaces.embedding_provider import EmbeddingProviderInterface
from dataload.config import logger
from dataload.domain.entities import EmbeddingError


class OpenAIEmbeddingProvider(EmbeddingProviderInterface):
    """Embedding provider using OpenAI API."""

    def __init__(self):
        # --- LAZY IMPORT openai HERE ---
        try:
            from openai import OpenAI  # Import moved here!
        except ImportError:
            raise EmbeddingError(
                "The 'openai' extra is required to use OpenAIEmbeddingProvider. "
                "Install with: pip install vector-dataloader[openai]"
            )
        # -----------------------------

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EmbeddingError("OPENAI_API_KEY is not set in environment variables")

        # Use the lazily imported class
        self.client = OpenAI(api_key=api_key)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.
        """
        # This method is fine because it relies on self.client created in __init__
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small", input=texts
            )
            results = [item.embedding for item in response.data]

            logger.info(f"Generated {len(results)} embeddings with OpenAI")
            return results

        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise EmbeddingError(f"OpenAI embedding failed: {e}")
