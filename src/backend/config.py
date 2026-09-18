from pydantic_settings import BaseSettings

import os
from dotenv import load_dotenv

from pathlib import Path

class Settings(BaseSettings):
    # Path of models downloaded from huggingface hub
    HF_MODELS_PATH: str = os.getenv("HOME") + "/.cache/huggingface/hub/"

    # Embeddings model path
    EMBEDDINGS_MODEL_PATH: str = (
        HF_MODELS_PATH
        + "models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/"
    )

    # --------------------
    # --- RAG SETTINGS ---
    # --------------------

    # Trigger llama_index SentenceSplitter, otherwise a simple regexp splitter is used
    LLAMA_SPLITTER: bool = True
    # Set size of chunk text division
    CHUNK_SIZE: int = 250
    # Text overlapping between chunks
    CHUNK_OVERLAP: int = 0
    # Number of best matching chunks returned from user query
    TOP_K: int = 5

    # Flag to not load LLM model (for frontend debugging).
    MOCK_MODE: bool = False

    # ------------------------------------------------------
    # --- LLM SETTINGS (used on services/rag_service.py) ---
    # ------------------------------------------------------

    # GGUF model for inference on llama.cpp
    GGUF_MODEL: str = (
        HF_MODELS_PATH
        + "models--unsloth--gemma-4-E4B-it-GGUF/snapshots/bfc15c382204943c3a8fff0c750b94ae2364d7a3/gemma-4-E4B-it-Q4_K_M.gguf"
    )

    # TODO: Enables model thinking
    ENABLE_THINKING: bool = False

    # Return inference tokens as they are generated
    STREAMING: bool = False

    # Max tokens for model context (None if max token context)
    MAX_TOKENS: int = 4096  # 16384 #8192 #6144 #4096

    # Sets the number of tokens processed on each model forward pass
    BATCH_SIZE: int = 256

    # Number of model layers to execute on GPU (-1 to execute all layers, else total_model_layers - GPU_LAYERS = layers to offload to CPU)
    GPU_LAYERS: int = 37

    # Set bit precission for K cache content
    TYPE_K: int = 8

    # Set bit precission for V cache content
    TYPE_V: int = 8

    # Saves memory with no performance impact
    FLASH_ATTN: bool = True

    # When True, rag_answer_generator sends inference requests to a localhosted
    # llama.cpp web server (LLAMA_SERVER_URL) instead of using the in-process
    # Llama object. No API key is required for the local server.
    USE_LLAMA_SERVER: bool = True

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "JETRAG"

    # ---------------------------------------------------------
    # --- RAG EVALUATION SETTINGS (used by rag_evaluation/* ) ---
    # ---------------------------------------------------------
    
    # RAG implementation to use, existing options are: "naive", "langchain"
    # "langchain" now is ONLY for evaluation purposes (collection_name is always hardcoded to "chest_2")
    RAG_IMPL: str = "langchain"

    # Send requests to backend when evaluating RAG, this can be useful when evaluating remote instances of JETRAG.
    USE_BACKEND: bool = False

    # REST endpoint of the running JETRAG backend, used by the evaluation
    # pipeline to feed documents (sources API) and query the RAG system
    # (chat API) over HTTP.
    BACKEND_API_URL: str = "http://localhost:8000"

    # If True, set database test data paths for RAG evaluation experiments, also avoid to store chat messages on every RAG call
    EVAL_MODE: bool = True

    # Database
    if EVAL_MODE:
        DATABASE_URL: str = "sqlite:///test_data/jetrag.db"
    else:
        DATABASE_URL: str = "sqlite:///msgs_data/jetrag.db"

    # ChromaDB
    if EVAL_MODE:
        CHROMA_PERSIST_DIRECTORY: str = "./data/test/chroma"
    else:
        CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    ENV_FILE: str = Path(__file__).parent.resolve().__str__() + "/.env"

    # WARNING: DON'T USE THE SAME MACRO NAME ON BOTH .ENV AND CONFIG.PY FILES
    load_dotenv(dotenv_path=ENV_FILE)
    key: str = os.getenv("ALIBABA_API_KEY") #"not-needed"

    API_KEY: str = key if key else "useful-key"
    #ALIBABA_API_KEY: str <- gets the variable directly from .env file
    MODEL_NAME: str = "glm-5.1" #"kimi-k2.7-code"
    OPENAI_SERVER_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1" #"http://localhost:8080"


config = Settings()
print("---- CONFIG.PY PARAMS ----")
print("USE_LLAMA_SERVER (if you use a local llama_server or an API LLM, set this to true): " + str(config.USE_LLAMA_SERVER))
print("RAG_IMPL: " + str(config.RAG_IMPL))
print("USE_BACKEND: " + str(config.USE_BACKEND))
print("OPENAI_SERVER_URL: " + str(config.OPENAI_SERVER_URL))
print("MODEL_NAME: " + str(config.MODEL_NAME))
print("STREAMING: " + str(config.STREAMING))

input("This settings are correct?: ")

