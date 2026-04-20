from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.backend.core.database import engine, Base
from src.backend.api.routes import chests, sources, chat

from dotenv import load_dotenv
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    pass

app = FastAPI(
    title="JETRAG API",
    description="API for managing chests, sources and chat",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chests.router, prefix="/api/chests", tags=["chests"])
app.include_router(sources.router, prefix="/api/sources", tags=["sources"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to JETRAG API"}
