from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_workspace_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.workspace import ChatMessageRequest, ChatMessageResponse, ConversationDetail, ConversationOut
from app.services.conversation_service import ConversationService
from app.gateway.context import RequestContext
from app.gateway.service import GatewayError, SentinelAIGateway

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(user: User = Depends(get_workspace_user), db: Session = Depends(get_db)) -> list[ConversationOut]:
    return ConversationService(db).list_for_session(user.id)


@router.post("/conversations", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(user: User = Depends(get_workspace_user), db: Session = Depends(get_db)) -> ConversationOut:
    return ConversationService(db).create(user.id)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(conversation_id: str, user: User = Depends(get_workspace_user), db: Session = Depends(get_db)) -> ConversationDetail:
    conversation = ConversationService(db).get_for_session(conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(conversation_id: str, user: User = Depends(get_workspace_user), db: Session = Depends(get_db)) -> None:
    conversations = ConversationService(db)
    conversation = conversations.get_for_session(conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    conversations.delete(conversation)


@router.post("/conversations/{conversation_id}/messages", response_model=ChatMessageResponse)
def send_message(conversation_id: str, payload: ChatMessageRequest, user: User = Depends(get_workspace_user), db: Session = Depends(get_db)) -> ChatMessageResponse:
    conversations = ConversationService(db)
    conversation = conversations.get_for_session(conversation_id, user.id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    user_message = conversations.add_message(conversation, "user", payload.content)
    history = [{"role": message.role, "content": message.content} for message in conversation.messages]
    context = RequestContext(
        request_id=str(uuid4()),
        conversation_id=conversation.id,
        user_id=user.id,
        role=user.role.name,
        prompt=payload.content,
        timestamp=datetime.now(timezone.utc),
        provider="openai",
    )
    try:
        response = SentinelAIGateway(db=db).process_request(context, history)
    except GatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    assistant_message = conversations.add_message(conversation, "assistant", response)
    return ChatMessageResponse(user_message=user_message, assistant_message=assistant_message)
