import os
import re
import shutil
import uuid
from typing import List
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.all_models import Document, Case
from app.core.config import settings
from app.rag.knowledge_service import knowledge_service

MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".json"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/json",
    "application/octet-stream"
}

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal and special character exploits."""
    base_name = os.path.basename(filename)
    clean_name = re.sub(r"[^\w\.-]", "_", base_name)
    return clean_name or "uploaded_document"

class DocumentService:
    @staticmethod
    async def upload_and_process_document(db: Session, case_id: str, file: UploadFile) -> Document:
        # 1. Filename sanitization
        safe_original_name = sanitize_filename(file.filename or "document")
        ext = os.path.splitext(safe_original_name)[1].lower()

        # 2. Extension validation
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension '{ext}' is not permitted. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # 3. MIME type validation
        content_type = file.content_type or "application/octet-stream"
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MIME type '{content_type}' is not permitted."
            )

        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated Case not found.")

        # 4. File size validation and safe streaming
        unique_filename = f"{uuid.uuid4().hex}_{safe_original_name}"
        save_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

        total_bytes = 0
        with open(save_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE:
                    buffer.close()
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Uploaded file exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)} MB."
                    )
                buffer.write(chunk)

        # Parse & Chunk & Ingest into vector store
        try:
            chunks = knowledge_service.ingest_file(save_path)
            extracted_text = "\n\n".join([c["text"] for c in chunks[:5]])  # preview
            status_val = "processed"
            chunk_count = len(chunks)
        except Exception as e:
            extracted_text = f"Processing error: {e}"
            status_val = "error"
            chunk_count = 0

        doc_record = Document(
            case_id=case_id,
            file_name=safe_original_name,
            file_path=save_path,
            file_size=total_bytes,
            mime_type=content_type,
            status=status_val,
            extracted_text=extracted_text,
            chunk_count=chunk_count,
            metadata_json={"original_name": safe_original_name, "sanitized": True}
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)
        return doc_record

    @staticmethod
    def get_document_by_id(db: Session, doc_id: str) -> Document:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
        return doc

    @staticmethod
    def list_documents_for_case(db: Session, case_id: str) -> List[Document]:
        return db.query(Document).filter(Document.case_id == case_id).all()
