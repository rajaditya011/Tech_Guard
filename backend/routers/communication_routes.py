"""
HomeGuardian AI — Communication Routes
"""

from fastapi import APIRouter, Depends
from models import SendMessageRequest, MessageResponse
from auth import get_current_user, require_role
from models import UserRole
from services.communication_service import communication_service

router = APIRouter()


@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: SendMessageRequest,
    user: dict = Depends(require_role(UserRole.NEW_DEVICE))
):
    """Send a message from dashboard to an old device."""
    result = await communication_service.send_message_to_device(
        target_device_id=request.target_device_id,
        message_text=request.message_text,
        audio_url=request.audio_url,
        sender_id=user["id"]
    )
    return MessageResponse(
        message_id=result["message_id"],
        status=result["status"],
        sent_at=result["sent_at"]
    )
