"""Triton client for embedding model inference."""
import numpy as np
import tritonclient.http as triton_http
from tritonclient.utils import np_to_triton_dtype

from config import get_settings

settings = get_settings()


class EmbeddingClient:
    """Client for Triton inference server embedding model."""

    def __init__(self, url: str | None = None):
        self.url = url or settings.triton_url
        self.model_name = settings.embedding_model_name
        self.client = triton_http.InferenceServerClient(
            url=self.url,
            verbose=False,
        )
        self._warm_up_done = False

    def warm_up(self) -> None:
        """Pre-warm the model to avoid first-request latency."""
        if self._warm_up_done:
            return
        dummy_text = ["warmup"]
        self.encode(dummy_text)
        self._warm_up_done = True

    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Encode texts into embedding vectors.

        Args:
            texts: List of text strings to encode.

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        inputs = triton_http.InferInput(
            "TEXT",
            [len(texts)],
            np_to_triton_dtype(np.object_),
        )
        inputs.set_data_from_numpy(np.array(texts, dtype=np.object_))

        outputs = triton_http.InferRequestedOutput("EMBEDDINGS")

        results = self.client.infer(
            model_name=self.model_name,
            inputs=[inputs],
            outputs=[outputs],
        )

        embeddings = results.as_numpy("EMBEDDINGS")
        return embeddings

    def encode_query(self, query: str) -> np.ndarray:
        """Encode a single query string."""
        return self.encode([query])[0]


embedding_client: EmbeddingClient | None = None


def get_embedding_client() -> EmbeddingClient:
    """Get or create the global embedding client."""
    global embedding_client
    if embedding_client is None:
        embedding_client = EmbeddingClient()
    return embedding_client
