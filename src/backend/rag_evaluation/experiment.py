from create_dataset import download_and_save_dataset, create_ragas_dataset
from eval import evaluate_rag
from openai import OpenAI
from ragas.llms import llm_factory

# Import required components
import asyncio
from datetime import datetime

LLM_BASE_URL = "http://localhost:8000/v1/"
LLM_MODEL = "gemma4"
API_KEY = "not-needed"

#provide_llm: method for providing Gemma4 local model as OpenAI API compatible server for RAGAS
def provide_llm():
    client = OpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)
    return llm_factory(LLM_MODEL, client=client)
    

async def run_evaluation():
    # Download and prepare dataset
    dataset_path = download_and_save_dataset()
    dataset = create_ragas_dataset(dataset_path)

    rag = # PUT MY RAG PIPELINE HERE

    # Run evaluation experiment
    exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_naiverag"
    results = await evaluate_rag.arun(
        dataset, 
        name=exp_name,
        rag=rag,
        llm=provide_llm()
    )

    # Print results
    if results:
        pass_count = sum(1 for result in results if result.get("correctness_score") == "pass")
        total_count = len(results)
        pass_rate = (pass_count / total_count) * 100 if total_count > 0 else 0
        print(f"Results: {pass_count}/{total_count} passed ({pass_rate:.1f}%)")

    return results

# Run the evaluation
results = await run_evaluation()
print(results)
