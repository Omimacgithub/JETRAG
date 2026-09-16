from datetime import datetime
from typing import List

import asyncio
import httpx
from openai import AsyncOpenAI

from ragas.llms import llm_factory

from src.backend.config import config
from src.backend.models.schemas import SourceCreate
from src.backend.rag_evaluation.create_dataset import create_ragas_dataset
from src.backend.rag_evaluation.eval import evaluate_rag

# OpenAI-compatible endpoint exposed by the local llama.cpp server hosting the LLM
LLM_BASE_URL = config.LLAMA_SERVER_URL.rstrip("/") + "/v1/"
LLM_MODEL = "gemma4"
API_KEY = "not-needed"

# Name of the chest used to group every document uploaded during evaluation
CHEST_NAME = "ragas_evaluation"

# Code for providing Gemma4 local model as OpenAI API compatible server for RAGAS
client = AsyncOpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)
llm = llm_factory(LLM_MODEL, client=client)


def setup_evaluation_chest(documents: List[str]) -> int:
    """Upload documents to the backend sources API so that their chunks and
    embeddings get persisted into the Chroma vector database.

    Documents are grouped under a dedicated chest that is created on the first
    run and reused afterwards. Sources previously uploaded to that chest are
    removed before inserting new ones so re-runs do not duplicate chunks.

    Returns:
        chest_id of the chest that owns the uploaded sources.
    """
    backend_url = config.BACKEND_API_URL.rstrip("/")
    with httpx.Client(base_url=backend_url, timeout=httpx.Timeout(120.0)) as http_client:
        # Reuse the evaluation chest if it already exists, create it otherwise.
        chests = http_client.get("/api/chests/")
        chests.raise_for_status()
        chest_id = next(
            (chest["id"] for chest in chests.json() if chest["name"] == CHEST_NAME),
            None,
        )
        if chest_id is None:
            created_chest = http_client.post("/api/chests/", json={"name": CHEST_NAME})
            created_chest.raise_for_status()
            chest_id = created_chest.json()["id"]

        # Clear sources loaded on previous runs to keep the vector store clean.
        sources = http_client.get("/api/sources/", params={"chest_id": chest_id})
        sources.raise_for_status()
        for source in sources.json():
            deleted = http_client.delete(f"/api/sources/{source['id']}")
            deleted.raise_for_status()

        # Store every document as a source through the sources API.
        for index, document in enumerate(documents):
            source = SourceCreate(
                name=f"eval_source_{index}",
                type="TXT",
                content=document,
                is_enabled=True,
                chest_id=chest_id,
            )
            created_source = http_client.post("/api/sources/", json=source.model_dump())
            created_source.raise_for_status()

        return chest_id


def run_evaluation():
    # Download and prepare dataset
    # dataset_path = download_and_save_dataset()
    dataset = create_ragas_dataset()  # dataset_path)
    documents = [
        "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
        "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
        "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
        "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'.",
        "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    ]

    # Store documents into ChromaDB through the sources API before evaluating
    chest_id = setup_evaluation_chest(documents)

    # Run evaluation experiment
    exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_naiverag"
    results = asyncio.run(
        evaluate_rag.arun(dataset, name=exp_name, llm=llm, chest_id=chest_id)
    )

    # Print results
    if results:
        pass_count = sum(
            1 for result in results if result.get("correctness_score") == "pass"
        )
        total_count = len(results)
        pass_rate = (pass_count / total_count) * 100 if total_count > 0 else 0
        print("---------------------------------")
        print(f"RESULTS: {pass_count}/{total_count} PASSED ({pass_rate:.1f}%)")
        print("---------------------------------")

    return results


def print_results_table(results: list) -> None:
    """Pretty-print evaluation results as a formatted table."""
    if not results:
        print("No results to display.")
        return

    columns = ["question", "expected_answer", "model_response", "correctness_score", "correctness_reason"]
    col_widths = {col: len(col) for col in columns}

    rows = []
    for result in results:
        row = {}
        for col in columns:
            value = str(result.get(col, "N/A"))
            row[col] = value
            if len(value) > col_widths[col]:
                col_widths[col] = len(value)
        rows.append(row)

    # Cap column widths for readability
    max_col_width = 60
    for col in columns:
        col_widths[col] = min(col_widths[col], max_col_width)

    def truncate(text: str, width: int) -> str:
        return text[: width - 3] + "..." if len(text) > width else text

    separator = "+-" + "-+-".join("-" * col_widths[col] for col in columns) + "-+"
    header = "| " + " | ".join(col.ljust(col_widths[col]) for col in columns) + " |"

    print()
    print(separator)
    print(header)
    print(separator)
    for row in rows:
        line = "| " + " | ".join(
            truncate(row[col], col_widths[col]).ljust(col_widths[col]) for col in columns
        ) + " |"
        print(line)
    print(separator)


# Run the evaluation
results = run_evaluation()

# Pretty-print results table
print_results_table(results)
