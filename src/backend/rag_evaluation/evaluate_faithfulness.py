"""RAG Faithfulness evaluation using ragas and a local gemma4 judge LLM."""

import pandas as pd
from datasets import Dataset
from openai import OpenAI
from ragas import evaluate
from ragas.embeddings import OpenAIEmbeddings as RagasOpenAIEmbeddings
from ragas.llms import llm_factory
from ragas.metrics import Faithfulness

PARQUET_PATH = "train-00000-of-00001.parquet"
LLM_BASE_URL = "http://localhost:8000/v1/"
LLM_MODEL = "gemma4"
API_KEY = "not-needed"


def load_dataset(parquet_path: str) -> Dataset:
    df = pd.read_parquet(parquet_path)
    df = df.rename(columns={"reference_contexts": "contexts"})
    df["response"] = ""
    return Dataset.from_pandas(df)


def generate_responses(dataset: Dataset, client: OpenAI) -> list[str]:
    responses: list[str] = []
    for row in dataset:
        context_block = "\n\n".join(row["contexts"])
        result = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Answer the question using ONLY the provided context.",
                    "refusal": "refuso"
                },
                {
                    "role": "user",
                    "content": f"Context:\n{context_block}\n\nQuestion: {row['user_input']}",
                    "refusal": "refuso"
                },
            ],
            temperature=0.0,
        )
        responses.append(result.choices[0].message.content or "")
    return responses


def main() -> None:
    client = OpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)

    judge_llm = llm_factory(LLM_MODEL, client=client)
    judge_embeddings = RagasOpenAIEmbeddings(
        model=LLM_MODEL, client=client
    )

    print(f"Loading dataset from {PARQUET_PATH}...")
    ds = load_dataset(PARQUET_PATH)
    print(f"Loaded {len(ds)} samples.")

    print("Generating responses with gemma4...")
    responses = generate_responses(ds, client)
    ds = ds.add_column("response", responses)

    print("Running Faithfulness evaluation...")
    faithfulness = Faithfulness(llm=judge_llm)
    result = evaluate(
        dataset=ds,
        metrics=[faithfulness],
        llm=judge_llm,
        embeddings=judge_embeddings,
    )

    print("\n=== Faithfulness Evaluation Results ===")
    print(result)
    print(f"\nOverall Faithfulness score: {result['faithfulness']:.4f}")


if __name__ == "__main__":
    main()
