import csv
import sys
import time

# Not for all systems
csv.field_size_limit(sys.maxsize)

from datetime import datetime
from pathlib import Path
from typing import Dict, List

import asyncio
import httpx
from openai import AsyncOpenAI

from ragas.llms import llm_factory
from ragas import Dataset

from src.backend.config import config
from src.backend.models.schemas import ChestCreate, SourceCreate
from src.backend.rag_evaluation.create_dataset import create_ragas_dataset
from src.backend.rag_evaluation.eval import evaluate_rag
from src.backend.core.database import get_db
from src.backend.services.chest_service import create_chest, get_chests
from src.backend.services.source_service import (
    create_source,
    delete_source,
    get_sources_by_chest,
)

# Name of the chest used to group every document uploaded during evaluation
CHEST_NAME = "ragas_evaluation"
BATCH_SIZE = 5

# Code for providing Gemma4 local model as OpenAI API compatible server for RAGAS
client = AsyncOpenAI(base_url=config.OPENAI_SERVER_URL,#"http://localhost:8080/v1", 
                     api_key=config.API_KEY)#, default_headers={"X-DashScope-Async": "disable"})
llm = llm_factory(config.MODEL_NAME, client=client)


def setup_evaluation_chest(documents: List[Dict[str, str]]) -> int:
    """Upload documents to the backend sources API so that their chunks and
    embeddings get persisted into the Chroma vector database.

    Documents are grouped under a dedicated chest that is created on the first
    run and reused afterwards. Sources previously uploaded to that chest are
    removed before inserting new ones so re-runs do not duplicate chunks.

    Returns:
        chest_id of the chest that owns the uploaded sources.
    """
    if config.USE_BACKEND:
        backend_url = config.BACKEND_API_URL.rstrip("/")
        with httpx.Client(base_url=backend_url, timeout=httpx.Timeout(120.0)) as http_client:
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

            sources = http_client.get("/api/sources/", params={"chest_id": chest_id})
            sources.raise_for_status()
            for source in sources.json():
                deleted = http_client.delete(f"/api/sources/{source['id']}")
                deleted.raise_for_status()

            for document in documents:
                source = SourceCreate(
                    name=document["source"],
                    type="TXT",
                    content=document["text"],
                    is_enabled=True,
                    chest_id=chest_id,
                )
                created_source = http_client.post("/api/sources/", json=source.model_dump())
                created_source.raise_for_status()
    else:
        print("Getting database, please wait... ")
        start = time.time()
        db_generator = get_db()
        db = next(db_generator)
        print(f"Time: {time.time() - start} seconds")
        try:
            chest = next(
                (chest for chest in get_chests(db) if chest.name == CHEST_NAME),
                None,
            )
            if chest is None:
                print("Creating chest, please wait...")
                start = time.time()
                new_chest = create_chest(db, ChestCreate(name=CHEST_NAME))
                print(f"Time: {time.time() - start} seconds")

                chest_id = new_chest.id

                print("Deleting sources, please wait...")
                start = time.time()
                for source in get_sources_by_chest(db, chest_id):
                    delete_source(db, source.id)
                print(f"Time: {time.time() - start} seconds")

                print("Creating sources from documents, please wait...")
                start = time.time()
                for document in documents:
                    create_source(
                        SourceCreate(
                            name=document["source"],
                            type="TXT",
                            content=document["text"],
                            is_enabled=True,
                            chest_id=chest_id,
                        ),
                        db,
                    )
                print(f"Time: {time.time() - start} seconds")
            else: 
                chest_id = chest.id

        finally:
            db_generator.close()

    return chest_id


def load_documents() -> List[Dict[str, str]]:
    csv_path = Path(__file__).parent / "documents" / "huggingface_doc.csv"
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [{"text": row["text"], "source": row["source"]} for row in reader]


async def run_evaluation():
    print("INFO: Creating dataset, please wait...")
    start = time.time()
    dataset = create_ragas_dataset()
    print(f"Time: {time.time() - start} seconds")
    print("INFO: Loading document, please wait...")
    start = time.time()
    documents = load_documents()
    print(f"Time: {time.time() - start} seconds")
    # Store documents into ChromaDB through the sources API before evaluating
    print("Store documents into ChromaDB through the sources API before evaluating, please wait...")
    chest_id = setup_evaluation_chest(documents)

    results = []
    items = list(dataset)

    rag_implementation = config.RAG_IMPL if hasattr(config, "RAG_IMPL") else "naive"
    
    start = time.time()
    print(f"Experiment started at {start}")
    for xed, i in enumerate(range(0, len(items), BATCH_SIZE)):
        exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M')}_" + rag_implementation + f"_rag_batch_{xed}"
        print(f"Run evaluation on batch {xed}, please wait...")
        
        batch = items[i:i + BATCH_SIZE]
        print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(items) + BATCH_SIZE - 1)//BATCH_SIZE}")

        batch_dataset = Dataset(
        name=dataset.name,
        backend=dataset.backend,
        #root_dir=dataset.root_dir,
        data=batch
    )
        
        batch_results = await evaluate_rag.arun(batch_dataset, name=exp_name, llm=llm, chest_id=chest_id)
        results.extend(batch_results)

    # Run evaluation experiment
    #exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_naiverag"
    #print("Run evaluation, please wait...")
    #start = time.time()
    #results = asyncio.run(
    #    evaluate_rag.arun(dataset, name=exp_name, llm=llm, chest_id=chest_id)
    #)
    #print(f"Time: {time.time() - start} seconds")

    # Print results
    if results:
        pass_count = sum(
            1 for result in results if result.get("correctness_score") == "pass"
        )
        total_count = len(results)
        pass_rate = (pass_count / total_count) * 100 if total_count > 0 else 0
        print("---------------------------------")
        print(f"RESULTS: {pass_count}/{total_count} PASSED ({pass_rate:.1f}%)")
        print(f"Total experiment time: {time.time() - start}")
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
results = asyncio.run(run_evaluation())

# Pretty-print results table
print_results_table(results)
