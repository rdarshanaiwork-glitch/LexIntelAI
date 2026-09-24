import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Float, DateTime, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="legal_counsel")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    cases = relationship("Case", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("ResearchSession", back_populates="user", cascade="all, delete-orphan")

class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    jurisdiction = Column(String(100), default="Federal / Common Law")
    legal_domain = Column(String(100), default="Commercial & Contract")
    client_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, archived, closed
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("User", back_populates="cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    sessions = relationship("ResearchSession", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")
    messages = relationship("ConversationMessage", back_populates="case", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), default="text/plain")
    status = Column(String(50), default="uploaded")  # uploaded, processed, error
    extracted_text = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="documents")

class LegalSource(Base):
    __tablename__ = "legal_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # statute, precedent, regulation, treatise
    citation = Column(String(255), nullable=True)
    court = Column(String(255), nullable=True)
    jurisdiction = Column(String(100), default="Common Law")
    year = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    objective = Column(Text, nullable=False)
    current_agent = Column(String(50), default="CaseIntakeAgent")
    status = Column(String(50), default="pending")  # pending, in_progress, completed, failed
    iteration_count = Column(Integer, default=0)
    state_snapshot_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    case = relationship("Case", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    agent_executions = relationship("AgentExecution", back_populates="session", cascade="all, delete-orphan", order_by="AgentExecution.step_number")
    reports = relationship("Report", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    step_number = Column(Integer, default=1)
    status = Column(String(50), default="completed")  # running, completed, failed
    execution_time_ms = Column(Integer, default=0)
    input_payload_json = Column(JSON, default=dict)
    output_payload_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ResearchSession", back_populates="agent_executions")

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    factual_analysis = Column(Text, nullable=True)
    statutory_matrix = Column(JSON, default=list)
    precedent_analysis = Column(JSON, default=list)
    strategic_recommendations = Column(JSON, default=list)
    opposing_arguments = Column(JSON, default=list)
    judicial_evaluation = Column(JSON, default=dict)
    critique_summary = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.85)
    limitations_disclaimer = Column(Text, nullable=False)
    full_report_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="reports")
    session = relationship("ResearchSession", back_populates="reports")
    citations = relationship("Citation", back_populates="report", cascade="all, delete-orphan")

class Citation(Base):
    __tablename__ = "citations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    source_id = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    citation_text = Column(String(255), nullable=False)
    jurisdiction = Column(String(100), default="Common Law")
    quote = Column(Text, nullable=True)
    relevance_score = Column(Float, default=1.0)
    source_type = Column(String(50), default="statute")  # statute, precedent, exhibit
    evidence_type = Column(String(50), default="SUPPORTED BY SOURCE")  # SUPPORTED BY SOURCE, MODEL INFERENCE, INSUFFICIENT EVIDENCE
    created_at = Column(DateTime, default=utc_now)

    report = relationship("Report", back_populates="citations")

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(100), default="user")  # user, agent, system
    role = Column(String(50), default="user")
    content = Column(Text, nullable=False)
    meta_info_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=utc_now)

    case = relationship("Case", back_populates="messages")
    session = relationship("ResearchSession", back_populates="messages")