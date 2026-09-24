from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.all_models import Case, Document, ResearchSession, Report
from app.schemas.agent_schemas import CaseCreate, CaseUpdate

class CaseService:
    @staticmethod
    def create_case(db: Session, case_in: CaseCreate, user_id: str) -> Case:
        new_case = Case(
            user_id=user_id,
            title=case_in.title,
            description=case_in.description,
            jurisdiction=case_in.jurisdiction or "Federal / Common Law",
            legal_domain=case_in.legal_domain or "Commercial & Contract",
            client_name=case_in.client_name
        )
        db.add(new_case)
        db.commit()
        db.refresh(new_case)
        return new_case

    @staticmethod
    def list_cases(db: Session, user_id: Optional[str] = None) -> List[Case]:
        query = db.query(Case)
        if user_id:
            query = query.filter(Case.user_id == user_id)
        return query.order_by(Case.created_at.asc()).all()

    @staticmethod
    def get_case_by_id(db: Session, case_id: str) -> Case:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
        return case

    @staticmethod
    def update_case(db: Session, case_id: str, case_in: CaseUpdate) -> Case:
        case = CaseService.get_case_by_id(db, case_id)
        if case_in.title is not None:
            case.title = case_in.title
        if case_in.description is not None:
            case.description = case_in.description
        if case_in.jurisdiction is not None:
            case.jurisdiction = case_in.jurisdiction
        if case_in.legal_domain is not None:
            case.legal_domain = case_in.legal_domain
        if case_in.status is not None:
            case.status = case_in.status
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def seed_all_demo_scenarios(db: Session, user_id: str):
        """Pre-populates the 3 required academic demo scenarios if missing."""
        existing_count = db.query(Case).count()
        if existing_count >= 3:
            return

        scenarios = [
            {
                "title": "Vance v. Sterling BioPharm International LLC",
                "description": "Senior QA Director reported falsification of clinical trial safety data to the corporate compliance committee and threatened SEC/FDA reporting under Sarbanes-Oxley § 806 (18 U.S.C. § 1514A). Within three weeks, Sterling BioPharm placed Vance on indefinite administrative leave and eliminated her position under a purported restructuring. Sterling contends that Vance was employed by an outsourced consulting subsidiary and lacks standing under SOX, and that she would have been discharged regardless.",
                "jurisdiction": "US Federal / 3rd Circuit",
                "legal_domain": "Employment & Corporate Whistleblower",
                "client_name": "Eleanor Vance (Plaintiff / Whistleblower)"
            },
            {
                "title": "OmniTech Cloud Services Inc. v. Marcus & NexaCore Cyber Ltd.",
                "description": "Lead Cloud Infrastructure Architect Marcus resigned to join competitor NexaCore. Prior to leaving, Marcus used his active administrative credentials to download 40GB of proprietary container images, customer databases, and security tokens to an external hard drive in breach of OmniTech's Acceptable Use Policy. OmniTech filed a civil action under the Computer Fraud and Abuse Act (18 U.S.C. § 1030) claiming $45,000 in remediation costs. Marcus moves to dismiss under the Supreme Court precedent Van Buren v. United States, asserting that having valid credentials means he did not 'exceed authorized access' under federal cyber law.",
                "jurisdiction": "US Federal / 9th Circuit",
                "legal_domain": "Cyber Law & Trade Secret Protection",
                "client_name": "OmniTech Cloud Services Inc. (Plaintiff)"
            },
            {
                "title": "Apex Logistics Solutions LLC v. Horizon Retail Enterprise Inc.",
                "description": "Commercial dispute regarding delayed linehaul refrigerated shipments during peak holiday shopping week. Horizon withheld $120,000 in invoiced payments citing a $5,000/day/truck liquidated damages provision, and additionally claims $350,000 in lost enterprise customer goodwill. Apex challenges clause enforceability under the penalty doctrine (Restatement (Second) of Contracts § 356) and consequential damage limits under Hadley v. Baxendale.",
                "jurisdiction": "Delaware Commercial / Common Law",
                "legal_domain": "Commercial Contracts & Supply Chain",
                "client_name": "Apex Logistics Solutions LLC (Plaintiff / Carrier)"
            }
        ]

        for sc in scenarios:
            found = db.query(Case).filter(Case.title == sc["title"]).first()
            if not found:
                case_obj = Case(
                    user_id=user_id,
                    title=sc["title"],
                    description=sc["description"],
                    jurisdiction=sc["jurisdiction"],
                    legal_domain=sc["legal_domain"],
                    client_name=sc["client_name"],
                    status="active"
                )
                db.add(case_obj)
        db.commit()