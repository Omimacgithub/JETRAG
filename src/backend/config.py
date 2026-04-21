from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///jetrag.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    
    # Triton (We don't use Triton on Jetson Orin Nano)
    TRITON_SERVER_URL: str = "http://triton:8001"
    TRITON_LLM_MODEL_NAME: str = "phi3"
    TRITON_EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    # Embeddings model path
    EMBEDDINGS_MODEL_PATH: str = "/home/omi/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/c9745ed1d9f207416be6d2e6f8de32d1f16199bf/"

    #Trigger llama_index SentenceSplitter, otherwise a simple regexp splitter is used
    LLAMA_SPLITTER: bool = True
    #Set size of chunk text division
    CHUNK_SIZE: int = 250
    #Text overlapping between chunks
    CHUNK_OVERLAP: int = 0
    #Number of best matching chunks returned from user query  
    TOP_K: int = 5
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "JETRAG"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
