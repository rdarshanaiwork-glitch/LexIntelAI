from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.agent_schemas import CaseCreate, CaseResponse, CaseUpdate
from app.services.case_service import CaseService
from app.services.auth_service import get_current_user
from app.models.all_models import User

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CaseService.create_case(db, case_in, current_user.id)

@router.get("", response_model=List[CaseResponse])
def list_cases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Ensure all 3 academic demo scenarios are seeded
    CaseService.seed_all_demo_scenarios(db, current_user.id)
    return CaseService.list_cases(db, None)

@router.get("/{id}", response_model=CaseResponse)
def get_case(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return CaseService.get_case_by_id(db, id)