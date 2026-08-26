from datasets import load_dataset
from ragas import evaluate, EvaluationDataset, SingleTurnSample, Dataset
from ragas.llms import llm_factory
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from openai import AsyncOpenAI
from ragas.metrics.collections import Faithfulness
import asyncio

client = AsyncOpenAI(
    base_url="http://localhost:8000/v1/",  # local Ollama server
    api_key="unused",
)  # required by the client, ignored by Ollama

llm = llm_factory("gemma4", client=client)
# Login using e.g. `huggingface-cli login` to access this dataset
# ds = load_dataset("dwb2023/ragas-golden-dataset")

# Create metric
scorer = Faithfulness(llm=llm)

"""
async def running_free():
  scorerer = scorer.ascore(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967",
    retrieved_contexts=[
        "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
    ]
  await scorerer
)

# Evaluate
result = asyncio.run(running_free())
print(f"Faithfulness Score: {result.value}")
"""
