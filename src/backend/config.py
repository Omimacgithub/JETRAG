from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    
    #Path of models downloaded from huggingface hub
    HF_MODELS_PATH: str = os.getenv("HOME") + ".cache/huggingface/hub/"

    # Database
    DATABASE_URL: str = "sqlite:///jetrag.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"

    # Embeddings model path
    EMBEDDINGS_MODEL_PATH: str = HF_MODELS_PATH + "models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/"

    #Trigger llama_index SentenceSplitter, otherwise a simple regexp splitter is used
    LLAMA_SPLITTER: bool = True
    #Set size of chunk text division
    CHUNK_SIZE: int = 250
    #Text overlapping between chunks
    CHUNK_OVERLAP: int = 0
    #Number of best matching chunks returned from user query  
    TOP_K: int = 5

    #GGUF model for inference on llama.cpp
    GGUF_MODEL: str = HF_MODELS_PATH + "models--unsloth--gemma-4-E2B-it-GGUF/snapshots/f064409f340b34190993560b2168133e5dbae558/gemma-4-E2B-it-Q4_K_S.gguf"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "JETRAG"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
