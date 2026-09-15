from create_dataset import download_and_save_dataset, create_ragas_dataset
from eval import evaluate_rag
from openai import OpenAI
from ragas.llms import llm_factory
from src.backend.core.vector_store import get_or_create_collection
from src.backend.services.source_service import create_source
from src.backend.models.schemas import SourceCreate

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
    #dataset_path = download_and_save_dataset()
    dataset = create_ragas_dataset()#dataset_path)
    knowledge_base = [
    
"Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    
"Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    
"Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    
"Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'.",
    
"Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine."
]
    #add collection to ChromaDB
    chest_id=0
    #collection = get_or_create_collection(collection_name=chest_id)

    # Create collection and add sources to ChromaDB
    create_source(SourceCreate(name="Papadopoulo", type="TXT", content=knowledge_base, is_enabled=True, chest_id=chest_id))    

    # Run evaluation experiment
    exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_naiverag"
    results = await evaluate_rag.arun(
        dataset, 
        name=exp_name,
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
