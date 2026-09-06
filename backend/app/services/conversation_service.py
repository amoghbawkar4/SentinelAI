from datetime import datetime

from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def list_for_session(self, user_session: str) -> list[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_session == user_session).order_by(Conversation.updated_at.desc()).all()

    def get_for_session(self, conversation_id: str, user_session: str) -> Conversation | None:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_session == user_session).first()

    def create(self, user_session: str) -> Conversation:
        conversation = Conversation(user_session=user_session)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def add_message(self, conversation: Conversation, role: str, content: str) -> Message:
        if role == "user" and conversation.title == "New conversation":
            conversation.title = " ".join(content.split())[:117].rstrip() + ("..." if len(" ".join(content.split())) > 117 else "")
        conversation.updated_at = datetime.utcnow()
        message = Message(conversation_id=conversation.id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def delete(self, conversation: Conversation) -> None:
        self.db.delete(conversation)
        self.db.commit()
