import httpx
import numpy as np
import logging
from config import settings

logger = logging.getLogger(__name__)

class TritonEmbeddingClient:
    def __init__(self):
        self.server_url = settings.TRITON_SERVER_URL
        self.model_name = settings.TRITON_EMBEDDING_MODEL_NAME
        self.embeddings_url = f"{self.server_url}/v2/models/{self.model_name}/infer"
        
    async def embed(self, texts: list[str]):
        """Get embeddings for a list of texts using Triton"""
        try:
            # Prepare input for Triton inference server
            # Triton expects a specific format for text inputs
            input_data = {
                "inputs": [
                    {
                        "name": "TEXT",
                        "shape": [len(texts), 1],
                        "datatype": "BYTES",
                        "data": [[text] for text in texts]  # Triton expects list of lists
                    }
                ],
                "outputs": [
                    {
                        "name": "EMBEDDING"
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.embeddings_url,
                    json=input_data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract embeddings from result
                embeddings_data = result["outputs"][0]["data"]
                # Convert to numpy array and reshape
                embeddings = np.array(embeddings_data).reshape(len(texts), -1)
                return embeddings.tolist()  # Return as list for JSON serialization
                
        except Exception as e:
            logger.error(f"Error calling Triton embedding service: {e}")
            raise

# Global instance
triton_embedding_client = TritonEmbeddingClient()