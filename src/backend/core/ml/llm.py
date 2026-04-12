import httpx
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class TritonLLMClient:
    def __init__(self):
        self.server_url = settings.TRITON_SERVER_URL
        self.model_name = settings.TRITON_LLM_MODEL_NAME
        self.generate_url = f"{self.server_url}/v2/models/{self.model_name}/generate"
        
    async def generate(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7):
        """Generate text using Triton LLM"""
        try:
            payload = {
                "text_input": prompt,
                "parameters": {
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.generate_url,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                return result.get("text_output", "")
                
        except Exception as e:
            logger.error(f"Error calling Triton LLM: {e}")
            raise

# Global instance
triton_llm_client = TritonLLMClient()