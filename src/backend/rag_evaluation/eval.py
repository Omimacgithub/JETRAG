# examples/ragas_examples/improve_rag/evals.py
# Followed the tutorial https://docs.ragas.io/en/stable/tutorials/rag/
import asyncio
from typing import Dict, Any
import httpx

from ragas import experiment

from src.backend.config import config

from ragas.metrics import DiscreteMetric

# Define correctness metric
correctness_metric = DiscreteMetric(
    
name="correctness",
    
prompt="""Compare the model response to the expected answer and determine if it's correct.

Consider the response correct if it:
1. Contains the key information from the expected answer
2. Is factually accurate based on the provided context
3. Adequately addresses the question asked

Return 'pass' if the response is correct, 'fail' if it's incorrect.

Question: {question}
Expected Answer: {expected_answer}
Model Response: {response}

Evaluation:""",
    
allowed_values=["pass", "fail"],
)

@experiment()
async def evaluate_rag(row: Dict[str, Any], llm, chest_id: int) -> Dict[str, Any]:
    """
    Run RAG evaluation on a single row.

    Args:
        row: Dictionary containing question and expected_answer
        rag: Pre-initialized RAG instance
        llm: Pre-initialized LLM client for evaluation
        chest_id: Identifier of the chest holding the sources used to answer

    Returns:
        Dictionary with evaluation results
    """
    question = row["question"]

    # Query the RAG system by calling the backend chat API endpoint
    payload = {"question": question, "chest_id": chest_id, "stream": False}
    async with httpx.AsyncClient(
        base_url=config.BACKEND_API_URL.rstrip("/"),
        timeout=httpx.Timeout(300.0),
    ) as http_client:
        chat_response = await http_client.post("/api/chat/", json=payload)
        chat_response.raise_for_status()
        rag_response = chat_response.json()

    # Evaluate correctness asynchronously
    score = await correctness_metric.ascore(
        question=question,
        expected_answer=row["expected_answer"],
        response=rag_response["answer"],
        llm=llm
    )

    # Return evaluation results
    result = {
        **row,
        "model_response": rag_response["answer"],
        "correctness_score": score.value,
        "correctness_reason": score.reason,
        "retrieved_documents": rag_response["retrieved_documents"]
    }

    '''
    result = {
            **row,
            "model_response": rag_response["answer"],
            "correctness_score": score.value,
            "correctness_reason": score.reason,
            "mlflow_trace_id": rag_response.get("mlflow_trace_id", "N/A"),  # MLflow trace ID for debugging (explained later)
            "retrieved_documents": [
                doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", "")
                for doc in rag_response.get("retrieved_documents", [])
            ]
        }
    '''

    return result