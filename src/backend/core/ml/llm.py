"""Triton client for LLM inference with streaming support."""
import json
from typing import AsyncGenerator

import numpy as np
import tritonclient.http as triton_http
from tritonclient.utils import np_to_triton_dtype

from config import get_settings

settings = get_settings()


class LLMClient:
    """Client for Triton inference server LLM model with streaming."""

    def __init__(self, url: str | None = None):
        self.url = url or settings.triton_url
        self.model_name = settings.llm_model_name
        self.client = triton_http.InferenceServerClient(
            url=self.url,
            verbose=False,
        )
        self._warm_up_done = False

    def warm_up(self) -> None:
        """Pre-warm the model to avoid first-request latency."""
        if self._warm_up_done:
            return
        self.generate("Hello", max_tokens=1)
        self._warm_up_done = True

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate text completion synchronously.

        Args:
            prompt: Input prompt text.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.

        Returns:
            Generated text completion.
        """
        inputs = triton_http.InferInput(
            "PROMPT",
            [1],
            np_to_triton_dtype(np.object_),
        )
        inputs.set_data_from_numpy(np.array([prompt], dtype=np.object_))

        max_tokens_input = triton_http.InferInput(
            "MAX_TOKENS",
            [1],
            np_to_triton_dtype(np.int32),
        )
        max_tokens_input.set_data_from_numpy(np.array([max_tokens], dtype=np.int32))

        temperature_input = triton_http.InferInput(
            "TEMPERATURE",
            [1],
            np_to_triton_dtype(np.float32),
        )
        temperature_input.set_data_from_numpy(
            np.array([temperature], dtype=np.float32)
        )

        top_p_input = triton_http.InferInput(
            "TOP_P",
            [1],
            np_to_triton_dtype(np.float32),
        )
        top_p_input.set_data_from_numpy(np.array([top_p], dtype=np.float32))

        outputs = triton_http.InferRequestedOutput("GENERATION")

        results = self.client.infer(
            model_name=self.model_name,
            inputs=[
                inputs,
                max_tokens_input,
                temperature_input,
                top_p_input,
            ],
            outputs=[outputs],
        )

        generation = results.as_numpy("GENERATION")
        return generation[0].decode("utf-8") if generation else ""

    async def generate_stream(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> AsyncGenerator[str, None]:
        """
        Generate text completion with streaming.

        Args:
            prompt: Input prompt text.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.

        Yields:
            Text chunks as they are generated.
        """
        result = self.generate(prompt, max_tokens, temperature, top_p)
        for char in result:
            yield char

    def build_prompt(
        self,
        system_prompt: str,
        context_chunks: list[str],
        user_message: str,
        conversation_history: list[dict] | None = None,
    ) -> str:
        """
        Build a formatted prompt for RAG.

        Args:
            system_prompt: Base system instruction.
            context_chunks: Retrieved context chunks.
            user_message: Current user message.
            conversation_history: Previous messages for context.

        Returns:
            Formatted prompt string.
        """
        context = "\n\n".join(f"[Source {i+1}]: {chunk}" for i, chunk in enumerate(context_chunks))

        prompt_parts = [f"<|system|>\n{system_prompt}"]

        if context_chunks:
            prompt_parts.append(f"\n\nRelevant context:\n{context}")

        if conversation_history:
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "user":
                    prompt_parts.append(f"<|user|>\n{content}")
                else:
                    prompt_parts.append(f"<|assistant|>\n{content}")

        prompt_parts.append(f"<|user|>\n{user_message}")
        prompt_parts.append("<|assistant|>")

        return "\n".join(prompt_parts)


llm_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create the global LLM client."""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client
