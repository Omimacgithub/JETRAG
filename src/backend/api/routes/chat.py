from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from core.database import get_db
from models.schemas import ChatMessage, ChatMessageCreate, RAGQuery, RAGResponse
from services import rag_service
from models.source import Source

router = APIRouter()

@router.post("/", response_model=ChatMessage)
def create_chat_message(chat_message: ChatMessageCreate, db: Session = Depends(get_db)):
    # Store user message
    db_chat_message = chat_message.dict()
    # In a real app, we'd store this in the database
    # For now, we'll just return it
    
    # Get chest sources for context
    # Actually, we'll process the RAG query
    
    return chat_message

@router.post("/query", response_model=RAGResponse)
def process_chat_query(rag_query: RAGQuery, db: Session = Depends(get_db)):
    # Process RAG query
    import asyncio
    result = asyncio.run(rag_service.process_rag_query(db, rag_query.chest_id, rag_query.question))
    
    # Store the chat messages (user and assistant)
    # In a real app, we'd store both user and assistant messages
    
    return result

# Alternative streaming endpoint
@router.post("/stream")
async def process_chat_query_stream(rag_query: RAGQuery, db: Session = Depends(get_db)):
    # For streaming response, we'd use StreamingResponse
    # For now, we'll return the regular response
    import asyncio
    result = await rag_service.process_rag_query(db, rag_query.chest_id, rag_query.question)
    return result