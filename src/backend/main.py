"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chests, chat, sources
from config import get_settings
from core.database import init_db
from core.ml.embeddings import get_embedding_client
from core.ml.llm import get_llm_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    init_db()

    try:
        embedding_client = get_embedding_client()
        embedding_client.warm_up()
    except Exception:
        pass

    try:
        llm_client = get_llm_client()
        llm_client.warm_up()
    except Exception:
        pass

    yield


app = FastAPI(
    title=settings.app_name,
    description="RAG chatbot with local sources",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chests.router)
app.include_router(sources.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
