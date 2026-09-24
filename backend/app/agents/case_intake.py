from typing import Dict, Any, List
from app.agents.base import BaseLegalAgent
from app.schemas.agent_schemas import CaseIntakeOutput
from app.tools.legal_tools import LegalToolRegistry


class CaseIntakeAgent(BaseLegalAgent):
    """
    5-agent architecture: Agent 1.

    Merges the former CoordinatorAgent (issue decomposition, strategy
    triage) and EvidenceAgent (factual/evidentiary audit) into a single
    agent that reasons over both jointly, rather than as two independent
    one-shot passes.

    Intellectual decisions this agent makes (not rule-based):
      - Issue decomposition: reads the actual fact pattern to infer which
        bodies of law are implicated, rather than keyword-matching.
      - Evidentiary sufficiency per issue: judges, issue by issue, whether
        the factual record actually supports it (not a global doc-count check).
      - Litigation scoping: identifies the issues and evidence needed for the mandatory
        full-litigation pipeline; it does not choose a shortcut topology.
      - Readiness gate: can flag the matter as not ready to proceed with
        specific missing information, rather than always marching forward.
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            name="CaseIntakeAgent",
            description=(
                "Jointly decomposes the matter into legal issues and audits the factual "
                "record, cross-referencing each issue against its evidentiary support to "
                "decide execution strategy and intake readiness."
            ),
            llm_provider=llm_provider
        )

    def _ground_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Reads real content for each uploaded document rather than just counting
        them. Prefers an on-disk file_path (via the tool registry, which gives
        real page/char counts) and falls back to whatever extracted-text
        snippet is already attached to the document record.
        """
        grounded: List[Dict[str, Any]] = []
        for doc in docs:
            entry: Dict[str, Any] = {
                "file_name": doc.get("file_name", "Unnamed Document"),
                "snippet": doc.get("snippet", "") or doc.get("extracted_text", "")[:500],
            }
            file_path = doc.get("file_path")
            if file_path:
                analysis = LegalToolRegistry.analyze_uploaded_document(file_path)
                if not analysis.get("error"):
                    entry["total_pages"] = analysis.get("total_pages")
                    entry["char_count"] = analysis.get("char_count")
            grounded.append(entry)
        return grounded

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_query = state.get("user_query", "") or state.get("case_context", {}).get("description", "")
        case_info = state.get("case_context", {})
        docs = state.get("uploaded_documents", [])

        grounded_docs = self._ground_documents(docs)

        system_prompt = (
            "You are the Lead Legal Intake Counsel. You perform two things at once, jointly: "
            "(1) decompose the matter into distinct legal issues by reading the actual facts, not by "
            "keyword-matching; and (2) audit the factual record for what is actually proven, "
            "corroborated, or missing. Then cross-reference every identified issue against the "
            "evidentiary record to rate its evidentiary_support as strong, moderate, weak, or none, "
            "and explain the specific gap where support is not strong. The production workflow is "
            "always Full Litigation, so do not choose a shortcut route. Instead decide whether the "
            "matter is sufficiently specified to proceed and list missing information explicitly. "
            "Never fabricate a document or fact that was not provided."
        )

        doc_summary = "\n".join(
            f"- {d['file_name']}"
            + (f" ({d['total_pages']} pages, {d['char_count']} chars)" if d.get("total_pages") else "")
            + (f": {d['snippet']}" if d.get("snippet") else "")
            for d in grounded_docs
        ) or "No documents uploaded."

        prompt = (
            f"Matter: {case_info.get('title', 'Legal Matter')}\n"
            f"Jurisdiction: {case_info.get('jurisdiction', 'Common Law')}\n"
            f"Client Narrative: {user_query}\n\n"
            f"Uploaded Documents:\n{doc_summary}\n\n"
            "Decompose the dispute into legal issues, audit the factual record, cross-reference "
            "each issue's evidentiary support, and decide intake_ready plus the missing information "
            "that should remain visible to downstream agents."
        )

        output: CaseIntakeOutput = self.llm.generate_structured(prompt, system_prompt, CaseIntakeOutput)
        result = output.model_dump()

        # Compatibility aliases for the canonical typed workflow state.
        result["legal_issues"] = [i["issue"] for i in result.get("identified_issues", [])]
        result["evidence_analysis"] = {
            "proven_facts": result.get("evidence_facts", []),
            "evidentiary_gaps": result.get("evidentiary_gaps", []),
            "corroboration_matrix": result.get("corroboration_matrix", {}),
        }

        return result
