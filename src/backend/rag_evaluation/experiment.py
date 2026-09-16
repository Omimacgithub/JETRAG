#import sys
#print("PATH: " + str(sys.path))
from src.backend.rag_evaluation.create_dataset import download_and_save_dataset, create_ragas_dataset
from openai import OpenAI
from ragas.llms import llm_factory
# Import required components
import asyncio
from datetime import datetime

from src.backend.rag_evaluation.eval import evaluate_rag
from src.backend.core.vector_store import get_or_create_collection
#Loads all-Mini
from src.backend.services.source_service import create_source
from src.backend.models.schemas import SourceCreate

LLM_BASE_URL = "http://localhost:8000/v1/"
LLM_MODEL = "gemma4"
API_KEY = "not-needed"

#Code for providing Gemma4 local model as OpenAI API compatible server for RAGAS
client = OpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)
llm = llm_factory(LLM_MODEL, client=client)
    
def run_evaluation():
    # Download and prepare dataset
    #dataset_path = download_and_save_dataset()
    dataset = create_ragas_dataset()#dataset_path)
    documents = [
    
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
    for i, source in enumerate(documents):
        create_source(SourceCreate(name=f"Papadopoulo_{i}", type="TXT", content=source, is_enabled=True, chest_id=chest_id))    

    # Run evaluation experiment
    exp_name = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_naiverag"
    results = evaluate_rag.arun(
        dataset, 
        name=exp_name,
        llm=llm
    )

    # Print results
    if results:
        pass_count = sum(1 for result in results if result.get("correctness_score") == "pass")
        total_count = len(results)
        pass_rate = (pass_count / total_count) * 100 if total_count > 0 else 0
        print(f"Results: {pass_count}/{total_count} passed ({pass_rate:.1f}%)")

    return results

# Run the evaluation
results = run_evaluation()
print(results)
