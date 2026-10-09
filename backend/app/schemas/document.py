from datetime import datetime

from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: str
    original_filename: str
    stored_filename: str
    storage_path: str
    content_type: str
    file_size_bytes: int
    uploader_id: str
    allowed_roles: list[str] = Field(default_factory=list)
    allowed_users: list[str] = Field(default_factory=list)
    processing_status: str
    uploaded_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
