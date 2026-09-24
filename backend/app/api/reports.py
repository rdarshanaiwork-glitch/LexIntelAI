from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.agent_schemas import ReportResponse
from app.services.research_service import ResearchService
from app.services.auth_service import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/{id}", response_model=ReportResponse)
def get_report(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResearchService.get_report_by_id(db, id)