from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # Path of models downloaded from huggingface hub
    HF_MODELS_PATH: str = os.getenv("HOME") + "/.cache/huggingface/hub/"

    # Database
    DATABASE_URL: str = "sqlite:///msgs_data/jetrag.db"

    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    # Embeddings model path
    EMBEDDINGS_MODEL_PATH: str = (
        HF_MODELS_PATH
        + "models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/"
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

    # Print to stdout inference tokens as they are generated
    STREAMING: bool = True

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

    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "JETRAG"

    class Config:
        case_sensitive = True
        env_file = ".env"


config = Settings()
