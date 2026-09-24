from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.agent_schemas import DocumentResponse
from app.services.doc_service import DocumentService
from app.services.auth_service import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await DocumentService.upload_and_process_document(db, case_id, file)

@router.get("/{id}", response_model=DocumentResponse)
def get_document(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return DocumentService.get_document_by_id(db, id)