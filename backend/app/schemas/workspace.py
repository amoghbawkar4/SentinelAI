from datetime import datetime

from pydantic import BaseModel, Field


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationOut):
    messages: list[MessageOut]


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=100_000)


class ChatMessageResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
