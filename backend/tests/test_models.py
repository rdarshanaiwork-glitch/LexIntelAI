import uuid
import pytest
from app.database.session import Base, SessionLocal, engine
from app.models.all_models import User, Case, Document, ResearchSession, Report, Citation

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_user_and_case_creation():
    db = SessionLocal()
    unique_email = f"attorney_{uuid.uuid4().hex[:8]}@lexintel.ai"
    try:
        user = User(
            email=unique_email,
            hashed_password="hashed_secret_test",
            full_name="Jane Doe Esq.",
            role="senior_partner"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.id is not None
        assert user.email == unique_email

        case = Case(
            user_id=user.id,
            title="Acme Corp v. Beta Logistics",
            description="Supply chain contract dispute regarding late delivery penalties.",
            jurisdiction="Delaware Commercial"
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        assert case.id is not None
        assert case.user_id == user.id
        assert len(user.cases) >= 1

        # Test Report & Citation relationship
        session = ResearchSession(
            case_id=case.id,
            user_id=user.id,
            objective="Evaluate penalty clause enforceability."
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        report = Report(
            case_id=case.id,
            session_id=session.id,
            title="Strategic Assessment Report",
            executive_summary="Executive findings regarding contract damages.",
            limitations_disclaimer="Decision-support only."
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        citation = Citation(
            report_id=report.id,
            title="Restatement Second Contracts § 356",
            citation_text="Restat 2d Contracts § 356",
            jurisdiction="Common Law",
            source_type="statute"
        )
        db.add(citation)
        db.commit()
        db.refresh(report)
        assert len(report.citations) == 1
        assert report.citations[0].title == "Restatement Second Contracts § 356"
    finally:
        db.close()