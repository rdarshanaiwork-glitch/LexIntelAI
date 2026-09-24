from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.agent_schemas import ResearchStartRequest, ResearchSessionResponse
from app.services.research_service import ResearchService
from app.services.auth_service import get_current_user
from app.models.all_models import User, ResearchSession

router = APIRouter(prefix="/research", tags=["Research"])

@router.post("/start", response_model=ResearchSessionResponse, status_code=status.HTTP_201_CREATED)
def start_research(
    req: ResearchStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return ResearchService.start_research(
        db=db,
        case_id=req.case_id,
        user_id=current_user.id,
        objective=req.objective,
        execution_strategy="full_litigation",
        document_ids=req.document_ids
    )

@router.get("/case/{case_id}/sessions", response_model=List[ResearchSessionResponse])
def get_case_sessions(case_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ResearchSession).filter(ResearchSession.case_id == case_id).order_by(ResearchSession.created_at.desc()).all()

@router.get("/{id}", response_model=ResearchSessionResponse)
def get_research_session(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ResearchService.get_session(db, id)

@router.get("/{id}/status")
def get_research_status(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = ResearchService.get_session(db, id)
    return {
        "id": session.id,
        "case_id": session.case_id,
        "status": session.status,
        "current_agent": session.current_agent,
        "iteration_count": session.iteration_count,
        "execution_steps": [
            {
                "agent_name": step.agent_name,
                "step_number": step.step_number,
                "status": step.status,
                "execution_time_ms": step.execution_time_ms,
                "output_payload_json": step.output_payload_json
            }
            for step in session.agent_executions
        ],
        "state_snapshot": session.state_snapshot_json,
        "report_id": session.reports[0].id if session.reports else None
    }