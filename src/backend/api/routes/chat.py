"""Chat API endpoints with streaming response."""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.dependencies import get_chest_service, get_rag_service
from core.database import get_db
from models.schemas import ChatMessageCreate, ChatMessageResponse
from services.chest_service import ChestService
from services.rag_service import RagService

router = APIRouter(tags=["chat"])


@router.get("/chests/{chest_id}/messages", response_model=list[ChatMessageResponse])
def get_chat_messages(
    chest_id: str,
    chest_service: ChestService = Depends(get_chest_service),
    rag_service: RagService = Depends(get_rag_service),
) -> list[ChatMessageResponse]:
    """Get all chat messages for a chest."""
    chest = chest_service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )

    messages = rag_service.get_messages(chest_id)
    return [
        ChatMessageResponse(
            id=msg.id,
            chest_id=msg.chest_id,
            role=msg.role,
            content=msg.content,
            sources_used=json.loads(msg.sources_used) if msg.sources_used else None,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.post("/chests/{chest_id}/chat")
async def chat(
    chest_id: str,
    data: ChatMessageCreate,
    db: Session = Depends(get_db),
    chest_service: ChestService = Depends(get_chest_service),
) -> StreamingResponse:
    """Send a message and stream the response."""
    chest = chest_service.get_by_id(chest_id)
    if not chest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chest {chest_id} not found",
        )

    rag_service = RagService(db)

    async def event_generator():
        async for event in rag_service.generate_response(chest_id, data.message):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
