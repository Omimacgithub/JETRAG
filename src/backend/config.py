from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///jetrag.db"
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    
    # Triton
    TRITON_SERVER_URL: str = "http://triton:8001"
    TRITON_LLM_MODEL_NAME: str = "phi3"
    TRITON_EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    # API
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "JETRAG"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
