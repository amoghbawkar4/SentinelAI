from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.models.user import User

SUPPORTED_ROLES = [
    "Employee",
    "Manager",
    "HR",
    "Payroll Administrator",
    "Security Analyst",
    "SentinelAI Administrator",
]


def _sanitize_filename(filename: str) -> str:
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", ascii_name).strip("._")
    return safe or "document"


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def validate_allowed_roles(raw_roles: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw_value in raw_roles or []:
            value = (raw_value or "").strip()
            if not value:
                continue
            if value not in SUPPORTED_ROLES:
                raise ValueError(f"Unsupported role in ACL: {value}")
            if value not in seen:
                seen.add(value)
                cleaned.append(value)
        if not cleaned:
            raise ValueError("At least one role must be selected for the document access list.")
        return cleaned

    @staticmethod
    def validate_allowed_users(raw_users: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for raw_value in raw_users or []:
            value = (raw_value or "").strip()
            if not value or value in seen:
                continue
            cleaned.append(value)
            seen.add(value)
        return cleaned

    @staticmethod
    def validate_file(file: UploadFile | None) -> tuple[str, str, int, str]:
        if file is None or not file.filename:
            raise ValueError("A document file is required.")

        filename = Path(file.filename).name
        suffix = Path(filename).suffix.lower()
        if suffix not in {ext.lower() for ext in settings.allowed_document_extensions}:
            raise ValueError("Unsupported file type.")

        content = file.file.read()
        file.file.seek(0)
        if len(content) == 0:
            raise ValueError("The uploaded file is empty.")
        if len(content) > settings.max_document_size_bytes:
            raise ValueError(f"File exceeds the maximum size of {settings.max_upload_size_mb} MB.")

        safe_name = _sanitize_filename(filename)
        known_type = file.content_type or "application/octet-stream"
        return filename, safe_name, len(content), known_type

    def create_document(self, uploader: User, file: UploadFile, allowed_roles: list[str], allowed_users: list[str]) -> Document:
        original_name, safe_name, file_size, content_type = self.validate_file(file)
        clean_roles = self.validate_allowed_roles(allowed_roles)
        clean_users = self.validate_allowed_users(allowed_users)

        for user_id in clean_users:
            if not self.db.query(User).filter(User.id == user_id).first():
                raise ValueError(f"Invalid user in ACL: {user_id}")

        storage_dir = Path(settings.document_storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)

        stored_filename = f"{uuid4().hex}_{safe_name}"
        storage_path = storage_dir / stored_filename
        with storage_path.open("wb") as stored_file:
            while True:
                chunk = file.file.read(8192)
                if not chunk:
                    break
                stored_file.write(chunk)
        file.file.seek(0)

        document = Document(
            original_filename=original_name,
            stored_filename=stored_filename,
            storage_path=str(storage_path),
            content_type=content_type,
            file_size_bytes=file_size,
            uploader_id=uploader.id,
            allowed_roles=clean_roles,
            allowed_users=clean_users,
            processing_status="RECEIVED",
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list_for_uploader(self, uploader_id: str) -> list[Document]:
        return self.db.query(Document).filter(Document.uploader_id == uploader_id).order_by(Document.uploaded_at.desc()).all()
