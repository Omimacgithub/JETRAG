from fastapi import APIRouter, FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
import json
import asyncio
from src.backend.core.database import get_db
from src.backend.models.schemas import (
    ChatMessage,
    ChatMessageCreate,
    RAGQuery,
    RAGResponse,
)
from src.backend.models.source import Source
from src.backend.models.chat_message import ChatMessage as DBChatMessage
from src.backend.services import rag_service
from src.backend.config import config
# from fastapi.background import BackgroundTasks

router = APIRouter()
# app = FastAPI()


def _create_chat_message(db: Session, chat_message: ChatMessageCreate) -> DBChatMessage:
    db_chat_message = DBChatMessage(**chat_message.dict())
    db.add(db_chat_message)
    db.commit()
    db.refresh(db_chat_message)
    return db_chat_message


async def sse_response_generator(
    db: Session,
    chest_id: int,
    question: str,
    # background_tasks: BackgroundTasks
) -> AsyncGenerator[str, None]:
    # chunk_text = ""
    async for chunk in rag_service.stream_rag_response(db, chest_id, question):
        yield chunk
    #    chunk_text += chunk
    """
    assistant_message = ChatMessageCreate(
        role="ASSISTANT",
        content=chunk_text,
        retrieved_documents=response['retrieved_documents'],
        chest_id=chest_id
    )
    background_tasks.add_task(_create_chat_message(db, assistant_message))
    """


@router.post("/")
async def process_chat_query(
    rag_query: RAGQuery,
    db: Session = Depends(get_db),
    # background_tasks: BackgroundTasks = None
):
    user_message = ChatMessageCreate(
        role="USER",
        content=rag_query.question,
        retrieved_documents=None,
        chest_id=rag_query.chest_id,
    )
    _create_chat_message(db, user_message)

    print("STREAMING FLAG: ", rag_query.stream)

    if rag_query.stream:
        return StreamingResponse(
            rag_service.stream_rag_response(db, rag_query.chest_id, rag_query.question),
            # sse_response_generator(db, rag_query.chest_id, rag_query.question),#background_tasks),
            media_type="text/plain",  # event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )

    # Non streaming way
    response = rag_service.process_rag_query(rag_query.chest_id, rag_query.question, db)

    '''
    assistant_message = ChatMessageCreate(
        role="ASSISTANT",
        content=response["answer"],
        retrieved_documents=response["retrieved_documents"],
        chest_id=rag_query.chest_id,
    )

    _create_chat_message(db, assistant_message)
    '''

    return response
