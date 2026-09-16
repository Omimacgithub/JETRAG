from pathlib import Path
from typing import List

import pandas as pd
from ragas import Dataset

PARQUET_PATH = Path(__file__).parent / "datasets" / "huggingface_doc_qa_eval.parquet"


def create_ragas_dataset() -> Dataset:
    df = pd.read_parquet(PARQUET_PATH)

    sample_queries: List[str] = df["question"].tolist()
    expected_responses: List[str] = df["answer"].tolist()

    dataset = Dataset(
        name="huggingface_doc_qa_eval",
        backend="local/csv",
        root_dir="src/backend/rag_evaluation/",
    )
    for sample_query, expected_response in zip(sample_queries, expected_responses):
        dataset.append({"question": sample_query, "expected_answer": expected_response})

    dataset.save()
    return dataset