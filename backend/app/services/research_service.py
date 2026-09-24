import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.all_models import ResearchSession, AgentExecution, Report, Citation, Case, Document
from app.workflows.legal_graph import legal_workflow_app
from app.database.session import SessionLocal
from app.core.config import settings

logger = logging.getLogger('lexintel.research_service')

class ResearchService:
    @staticmethod
    def start_research(
        db: Session, 
        case_id: str, 
        user_id: str, 
        objective: str, 
        execution_strategy: str = "full_litigation",
        document_ids: Optional[List[str]] = None
    ) -> ResearchSession:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

        # Query prior completed research sessions for this case to provide cross-turn memory
        prior_session = (
            db.query(ResearchSession)
            .filter(ResearchSession.case_id == case_id, ResearchSession.status == "completed")
            .order_by(ResearchSession.created_at.desc())
            .first()
        )
        prior_memory = None
        if prior_session and prior_session.state_snapshot_json:
            snap = prior_session.state_snapshot_json
            prior_memory = {
                "prior_session_id": prior_session.id,
                "prior_objective": prior_session.objective,
                "prior_legal_issues": snap.get("legal_issues", []),
                "prior_theory": snap.get("case_theory", {}).get("theory_of_the_case", ""),
                "prior_revision_history": snap.get("revision_history", [])
            }

        # Create session record
        session = ResearchSession(
            case_id=case_id,
            user_id=user_id,
            objective=objective,
            current_agent="CaseIntakeAgent",
            status="in_progress",
            iteration_count=0,
            state_snapshot_json={"execution_strategy": execution_strategy, "prior_memory": prior_memory}
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        # Run multi-agent pipeline with memory
        ResearchService.execute_pipeline(session.id, execution_strategy=execution_strategy, prior_memory=prior_memory, document_ids=document_ids)
        db.refresh(session)
        return session

    @staticmethod
    def execute_pipeline(session_id: str, execution_strategy: str = "full_litigation", prior_memory: Optional[Dict[str, Any]] = None, document_ids: Optional[List[str]] = None):
        db = SessionLocal()
        try:
            session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
            if not session:
                return

            case = session.case
            docs = case.documents
            if document_ids:
                wanted = set(document_ids)
                docs = [d for d in docs if d.id in wanted]

            doc_dicts = [
                {
                    "file_name": d.file_name,
                    # Keep a useful context window while preserving the full document id
                    # so downstream agents can retrieve the complete exhibit when needed.
                    "snippet": (d.extracted_text or "")[:6000],
                    "extracted_text": d.extracted_text or "",
                    "file_path": d.file_path,
                    "document_id": d.id,
                }
                for d in docs
            ]

            initial_state = {
                "session_id": session_id,
                "case_id": case.id,
                "strategy_requested": execution_strategy,
                "case_context": {
                    "case_id": case.id,
                    "title": case.title,
                    "description": case.description,
                    "jurisdiction": case.jurisdiction,
                    "legal_domain": case.legal_domain
                },
                "user_query": session.objective,
                "execution_strategy": execution_strategy,
                "prior_session_memory": prior_memory,
                "uploaded_documents": doc_dicts,
                "iteration_count": 0,
                "max_revisions": int(getattr(settings, "MAX_REVISIONS", 0)),
                "execution_history": [],
                "revision_history": [],
                "errors": []
            }

            logger.info(f"Triggering LangGraph workflow for session {session_id} (strategy: {execution_strategy})")
            final_state = legal_workflow_app.invoke(initial_state)

            # Persist the actual trajectory step-by-step. The output stored for a repeated
            # agent is the output from that specific invocation, not the final state alias.
            history = final_state.get("execution_history", [])
            for step_num, item in enumerate(history, 1):
                agent_exec = AgentExecution(
                    session_id=session.id,
                    agent_name=item.get("agent", "Agent"),
                    step_number=step_num,
                    status=item.get("status", "completed"),
                    execution_time_ms=item.get("time_ms", 0),
                    input_payload_json={
                        "strategy": execution_strategy,
                        "is_revision": item.get("is_revision", False),
                        "iteration": final_state.get("iteration_count", 0),
                    },
                    output_payload_json=item.get("output_payload") or {},
                )
                db.add(agent_exec)

            # Create Report
            report_data = final_state.get("final_report", {})
            if report_data:
                exec_summary = report_data.get("executive_summary", "Executive summary generated by multi-agent analysis.")
                fact_analysis = report_data.get("case_context") or report_data.get("factual_analysis", case.description)
                stat_matrix = report_data.get("statutory_matrix") or report_data.get("applicable_laws", [])
                prec_analysis = report_data.get("precedent_analysis") or report_data.get("relevant_precedents", [])
                strat_recs = report_data.get("strategic_recommendations") or report_data.get("strategic_considerations", [])
                opp_args = report_data.get("opposing_arguments", [])
                judge_eval = report_data.get("simulated_judicial_perspective") or report_data.get("judicial_evaluation", {})
                crit_summary = final_state.get("critic_feedback", {})

                new_report = Report(
                    case_id=case.id,
                    session_id=session.id,
                    title=report_data.get("title", f"Strategic Legal Intelligence Report: {case.title}"),
                    executive_summary=exec_summary,
                    factual_analysis=fact_analysis,
                    statutory_matrix=stat_matrix if isinstance(stat_matrix, list) else [stat_matrix],
                    precedent_analysis=prec_analysis if isinstance(prec_analysis, list) else [prec_analysis],
                    strategic_recommendations=strat_recs if isinstance(strat_recs, list) else [strat_recs],
                    opposing_arguments=opp_args if isinstance(opp_args, list) else [opp_args],
                    judicial_evaluation=judge_eval if isinstance(judge_eval, dict) else {"details": judge_eval},
                    critique_summary=crit_summary if isinstance(crit_summary, dict) else {"details": crit_summary},
                    confidence_score=float((final_state.get("merits_evaluation") or {}).get("argument_strength", 0.0)),
                    limitations_disclaimer=report_data.get("disclaimer", "Decision-support intelligence only. Not formal legal counsel or actual judicial prediction."),
                    full_report_json=report_data
                )
                db.add(new_report)
                db.flush()

                # Save citations with grounding evidence types
                citations_list = report_data.get("sources_and_citations") or report_data.get("citations", [])
                for cite in citations_list:
                    if isinstance(cite, dict):
                        citation_record = Citation(
                            report_id=new_report.id,
                            source_id=cite.get("source_id", ""),
                            title=cite.get("title", "Legal Authority"),
                            citation_text=cite.get("citation_text", ""),
                            jurisdiction=cite.get("jurisdiction", "Common Law"),
                            quote=cite.get("supporting_text") or cite.get("quote"),
                            relevance_score=cite.get("confidence", 1.0),
                            source_type=cite.get("source_type", "statute"),
                            evidence_type=cite.get("evidence_type", "SUPPORTED BY SOURCE")
                        )
                        db.add(citation_record)

            session.status = final_state.get("status", "failed") if final_state.get("status") in {"completed", "failed", "inconclusive"} else "failed"
            session.current_agent = "Completed" if session.status == "completed" else final_state.get("current_agent", "Unknown")
            session.iteration_count = final_state.get("iteration_count", 0)
            session.state_snapshot_json = {
                "session_id": session_id,
                "execution_strategy": execution_strategy,
                "prior_memory": prior_memory,
                "identified_issues": final_state.get("identified_issues", []),
                "plan": final_state.get("plan", {}),
                "legal_issues": final_state.get("legal_issues", []),
                "research_findings": final_state.get("research_findings", {}),
                "research_trajectory": final_state.get("research_trajectory", []),
                "case_theory": final_state.get("case_theory", {}),
                "counterarguments": final_state.get("counterarguments", {}),
                "self_assessment": final_state.get("self_assessment", {}),
                "merits_evaluation": final_state.get("merits_evaluation", {}),
                "critic": final_state.get("critic_feedback", {}),
                "revision_history": final_state.get("revision_history", []),
                "execution_history": final_state.get("execution_history", []),
                "final_report": report_data,
                "run_evaluation": final_state.get("run_evaluation", {}),
                "verdict": final_state.get("verdict", "PASS"),
                "passed_quality_gate": final_state.get("passed_quality_gate", True),
                "citation_audit": final_state.get("citation_audit", [])
            }
            db.commit()
            logger.info(f"Session {session_id} completed successfully.")
        except Exception as e:
            logger.error(f"Execution failed for session {session_id}: {e}", exc_info=True)
            session.status = "failed"
            session.current_agent = "Failed"
            session.state_snapshot_json = {**(session.state_snapshot_json or {}), "error": str(e)}
            db.commit()
        finally:
            db.close()

    @staticmethod
    def get_session(db: Session, session_id: str) -> ResearchSession:
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research session not found.")
        return session

    @staticmethod
    def get_report_by_id(db: Session, report_id: str) -> Report:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
        return report