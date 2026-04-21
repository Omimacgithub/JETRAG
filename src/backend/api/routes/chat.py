from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json
from src.backend.core.database import get_db
from src.backend.models.schemas import ChatMessage, ChatMessageCreate, RAGQuery, RAGResponse
from src.backend.models.source import Source
from src.backend.models.chat_message import ChatMessage as DBChatMessage
from src.backend.services import rag_service
import asyncio

router = APIRouter()

def _create_chat_message(db: Session, chat_message: ChatMessageCreate) -> DBChatMessage:
    db_chat_message = DBChatMessage(**chat_message.dict())
    db.add(db_chat_message)
    db.commit()
    db.refresh(db_chat_message)
    return db_chat_message

#@router.post("/", response_model=ChatMessage)
#def create_chat_message(chat_message: ChatMessageCreate, db: Session = Depends(get_db)):
#    return _create_chat_message(db, chat_message)

@router.post("/", response_model=RAGResponse)
def process_chat_query(rag_query: RAGQuery, db: Session = Depends(get_db)):
    # Store user message
    user_message = ChatMessageCreate(
        role="USER",
        content=rag_query.question,
        sources_used=None,
        chest_id=rag_query.chest_id
    )
    _create_chat_message(db, user_message)
    
    # Process RAG query
    result = asyncio.run(rag_service.process_rag_query(db, rag_query.chest_id, rag_query.question))
    
    # Store assistant message
    assistant_message = ChatMessageCreate(
        role="ASSISTANT",
        content=result['answer'],
        sources_used=result['sources_used'],
        chest_id=rag_query.chest_id
    )
    _create_chat_message(db, assistant_message)
    
    return result

# Alternative streaming endpoint
@router.post("/stream")
async def process_chat_query_stream(rag_query: RAGQuery, db: Session = Depends(get_db)):
    # For streaming response, we'd use StreamingResponse
    # For now, we'll return the regular response
    result = await rag_service.process_rag_query(db, rag_query.chest_id, rag_query.question)
    return result