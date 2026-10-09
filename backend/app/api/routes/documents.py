from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_document_uploader
from app.database.session import get_db
from app.models.user import User
from app.schemas.document import DocumentOut
from app.services.audit_log_service import AuditLogService
from app.services.document_service import DocumentService

router = APIRouter()


@router.get("", response_model=list[DocumentOut])
def list_documents(user: User = Depends(get_document_uploader), db: Session = Depends(get_db)) -> list[DocumentOut]:
    return DocumentService(db).list_for_uploader(user.id)


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    allowed_roles: list[str] = Form(default_factory=list),
    allowed_users: list[str] = Form(default_factory=list),
    user: User = Depends(get_document_uploader),
    db: Session = Depends(get_db),
) -> DocumentOut:
    try:
        document = DocumentService(db).create_document(user, file, allowed_roles, allowed_users)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    AuditLogService(db).create_log(
        action="document_upload",
        status="success",
        user_id=user.id,
        details=f"Uploaded document {document.original_filename} with ACL {', '.join(document.allowed_roles) or 'none'}",
    )
    return document
