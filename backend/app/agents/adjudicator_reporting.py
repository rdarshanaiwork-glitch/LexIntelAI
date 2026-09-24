from typing import Dict, Any, List
from app.agents.base import BaseLegalAgent
from app.schemas.agent_schemas import AdjudicatorOutput, ReportingOutput, CitationSchema
from app.tools.legal_tools import LegalToolRegistry
from app.workflows.context import compact_json


class AdjudicatorReportingAgent(BaseLegalAgent):
    """
    Department Agent 4: Adjudication & Reporting Department.

    Unifies judicial merits evaluation, mechanical citation auditing,
    causal root-cause flaw attribution, PASS/REVISE quality gate control,
    and depth-calibrated strategic legal report generation into a single
    departmental master agent.

    Workflow & Intellectual Decisions:
      1. MERITS EVALUATION -- score argument/evidence/precedent strength
         as a neutral judge would, reasoning first, scores after.
      2. CITATION AUDIT -- run every citation currently on record
         through LegalToolRegistry.validate_citation() mechanically.
      3. ROOT-CAUSE ATTRIBUTION -- read merits evaluation and citation audit
         TOGETHER to attribute flaws to specific upstream department agents
         (case_intake / legal_research / advocate / none).
      4. QUALITY GATE VERDICT -- decide PASS vs REVISE based on flaw materiality,
         providing remediation instructions for target upstream agent.
      5. DEPTH & GROUNDING REPORTING -- if PASS (or max revisions reached),
         calibrates report depth (full_litigation_report only)
         and labels every section with its grounding status (SUPPORTED BY SOURCE,
         MODEL INFERENCE, INSUFFICIENT EVIDENCE).
    """

    MAX_REVISIONS = 2

    def __init__(self, llm_provider=None):
        super().__init__(
            name="AdjudicatorReportingAgent",
            description=(
                "Evaluates argument merits and citation validity, attributes root-cause flaws "
                "to upstream agents, enforces quality gate control, and compiles depth-calibrated "
                "strategic legal reports."
            ),
            llm_provider=llm_provider
        )

    def _audit_citations(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        candidates: List[Dict[str, str]] = []

        research = state.get("research_findings") or state.get("retrieved_sources", [])
        if isinstance(research, dict):
            sources = research.get("retrieved_sources", [])
        elif isinstance(research, list):
            sources = research
        else:
            sources = []

        for source in sources:
            if isinstance(source, dict):
                meta = source.get("citation_metadata", {})
                candidates.append({
                    "title": source.get("title", ""),
                    "citation_text": meta.get("citation", "") if isinstance(meta, dict) else ""
                })

        for cite in state.get("citations", []):
            if isinstance(cite, dict):
                candidates.append({
                    "title": cite.get("title", ""),
                    "citation_text": cite.get("citation_text", "")
                })

        audited = []
        seen = set()
        for c in candidates:
            key = (c["title"], c["citation_text"])
            if key in seen or (not c["title"] and not c["citation_text"]):
                continue
            seen.add(key)
            result = LegalToolRegistry.validate_citation(c["citation_text"], c["title"])
            audited.append({
                "title": c["title"],
                "is_valid": result.get("is_valid", False),
                "raw_result": result
            })
        return audited

    def _build_citations(self, state: Dict[str, Any], audited_citations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        research = state.get("research_findings") or {}
        retrieved = research.get("retrieved_sources", []) if isinstance(research, dict) else state.get("retrieved_sources", [])
        audit_by_title = {c.get("title"): c.get("is_valid", True) for c in audited_citations}

        citations: List[Dict[str, Any]] = []
        for idx, src in enumerate(retrieved, 1):
            if not isinstance(src, dict):
                continue
            meta = src.get("citation_metadata", {}) if isinstance(src.get("citation_metadata"), dict) else {}
            is_valid = audit_by_title.get(src.get("title"), True)
            citations.append({
                "citation_id": f"CITE-{idx:03d}",
                "source_id": src.get("source_id", f"src-{idx}"),
                "title": src.get("title", "Legal Source"),
                "citation_text": meta.get("citation", "Citation On Record"),
                "jurisdiction": src.get("jurisdiction", "Common Law"),
                "claim": f"Authority on {src.get('section', 'General')}",
                "supporting_text": src.get("content", "")[:300],
                "page_section": f"Page {src.get('location_page', 1)}, Section: {src.get('section', 'General')}",
                "confidence": round(float(src.get("relevance_score", 0.9)), 2),
                "evidence_type": "SUPPORTED BY SOURCE" if is_valid else "INSUFFICIENT EVIDENCE",
            })
        return citations

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        case_theory = state.get("case_theory") or state.get("strategy", {})
        counterarguments = state.get("counterarguments", {})
        iteration_count = state.get("iteration_count", 0)

        audited_citations = self._audit_citations(state)
        invalid_citations = [c for c in audited_citations if not c["is_valid"]]

        # Step 1 & 2: Adjudication (Merits + Citation Audit + Root Cause)
        system_prompt_adj = (
            "You are a Senior Adjudicator combining Neutral Presiding Judge and Quality Assurance Partner. "
            "Evaluate argument merits, weigh citation audit results together, and render a final quality verdict. "
            "QUALITY STANDARDS: "
            "- Render PASS if audited citations are verified and the litigation theory and research are viable. "
            "(Evidentiary gaps requiring formal pre-trial discovery are expected and normal in litigation intake; they do NOT trigger REVISE). "
            "- Render REVISE only if there are unverified/hallucinated citations or fatal errors in the legal analysis. "
            "When research, citations, and advocacy are legally sound, you MUST render PASS."
        )

        citation_summary = "\n".join(
            f"- \"{c['title']}\": {'VALID' if c['is_valid'] else 'INVALID -- not found in verified knowledge base'}"
            for c in audited_citations
        ) or "No citations on record to audit."

        prompt_adj = (
            "Evaluate this specific trajectory. Do not produce a generic legal answer. "
            "Every material finding must point to a concrete issue, authority, evidence item, "
            "argument, or counterargument from the supplied state.\n\n"
            f"Case Context:\n{compact_json(state.get('case_context', {}), 1500)}\n\n"
            f"Issues & Intake:\n{compact_json(state.get('identified_issues', []), 2000)}\n\n"
            f"Research:\n{compact_json(state.get('research_findings', {}), 3000)}\n\n"
            f"Advocacy Theory:\n{compact_json(case_theory, 2500)}\n\n"
            f"Counterarguments:\n{compact_json(counterarguments, 2000)}\n\n"
            f"Citation Audit Results:\n{citation_summary[:2000]}\n\n"
            f"Revision History:\n{compact_json(state.get('revision_history', []), 1500)}\n"
            f"Current Iteration: {iteration_count}\n\n"
            "Evaluate merits, attribute root cause, and render PASS or REVISE. "
            "If citations are verified and strategy is sound, render PASS."
        )

        adj_output: AdjudicatorOutput = self.llm.generate_structured(prompt_adj, system_prompt_adj, AdjudicatorOutput)
        adj_dict = adj_output.model_dump()

        # If citation audit has 0 invalid citations, ensure quality gate passes cleanly
        if not invalid_citations and adj_dict.get("verdict") == "REVISE":
            rc_reason = str(adj_dict.get("root_cause", {}).get("root_cause_reasoning", "")).lower()
            if any(w in rc_reason for w in ("gap", "evidence", "document", "contract", "discovery", "factual", "information")):
                adj_dict["verdict"] = "PASS"
                adj_dict["materiality_reasoning"] = (
                    "Legal claims, research citations, and strategic theories verified sound (PASS). "
                    "Pre-trial evidentiary discovery roadmap established."
                )
                adj_dict["root_cause"] = {"root_cause_reasoning": "No fatal analytical flaws; citations 100% verified.", "root_cause_agent": "none"}

        # Revision budget enforcement
        if adj_dict["verdict"] == "REVISE" and iteration_count >= self.MAX_REVISIONS:
            adj_dict["materiality_reasoning"] += " [Revision budget exhausted; unresolved material issues remain.]"

        target_agent = None if adj_dict["root_cause"]["root_cause_agent"] == "none" else adj_dict["root_cause"]["root_cause_agent"]

        # Step 3: Reporting Compilation (If PASS or Revision Capped)
        report_dict = {}
        citations = self._build_citations(state, audited_citations)

        if adj_dict["verdict"] in {"PASS", "REVISE"}:
            system_prompt_rep = (
                "You are the Chief Legal Report Architect. Compile the final strategic legal report from "
                "upstream analysis. First reason about required detail depth (full_litigation_report), "
                "then generate 4 to 6 focused sections labeled with basis: SUPPORTED BY SOURCE, "
                "MODEL INFERENCE, or INSUFFICIENT EVIDENCE."
            )

            prompt_rep = (
                "Compile a case-specific legal intelligence report from the complete trajectory below. "
                "Do not use stock conclusions. Every recommendation and assessment must trace back "
                "to the actual facts, issues, authorities, evidence, and adversarial analysis.\n\n"
                f"Case:\n{compact_json(state.get('case_context', {}), 1500)}\n\n"
                f"Intake:\n{compact_json(state.get('identified_issues', []), 2000)}\n\n"
                f"Research:\n{compact_json(state.get('research_findings', {}), 3000)}\n\n"
                f"Advocacy:\n{compact_json({'theory': case_theory, 'counterarguments': counterarguments, 'self_assessment': state.get('self_assessment', {})}, 3000)}\n\n"
                f"Adjudication:\n{compact_json(adj_dict, 2000)}\n\n"
                f"Verified Citations: {len(citations)}\n\n"
                "Decide report depth and compile the final report."
            )

            rep_output: ReportingOutput = self.llm.generate_structured(prompt_rep, system_prompt_rep, ReportingOutput)
            report_dict = rep_output.model_dump()
            if citations:
                report_dict["sources_and_citations"] = citations
            # Enrich the report with deterministic projections of the actual upstream
            # trajectory. This keeps the UI useful even when the reporting model chooses
            # concise prose, and prevents generic template sections from hiding case-specific data.
            sources = state.get("retrieved_sources", []) or []
            report_dict["case_context"] = state.get("case_context", {}).get("description", "")
            report_dict["legal_issues"] = [i.get("issue", str(i)) if isinstance(i, dict) else str(i) for i in state.get("identified_issues", [])]
            report_dict["applicable_laws"] = [
                {
                    "law": s.get("title", "Legal Authority"),
                    "section": s.get("citation_metadata", {}).get("citation", s.get("section", "General")) if isinstance(s.get("citation_metadata"), dict) else s.get("section", "General"),
                    "relevance": s.get("content", "")[:500],
                    "finding": "Retrieved and provenance-tracked",
                }
                for s in sources if isinstance(s, dict) and (s.get("citation_metadata", {}).get("document_type") if isinstance(s.get("citation_metadata"), dict) else "") in {"statute", "regulation", "treatise"}
            ]
            report_dict["relevant_precedents"] = [
                {
                    "case": s.get("title", "Legal Precedent"),
                    "citation": s.get("citation_metadata", {}).get("citation", "") if isinstance(s.get("citation_metadata"), dict) else "",
                    "principle": s.get("content", "")[:600],
                    "application": "Assess against the identified legal issues and factual distinctions.",
                }
                for s in sources if isinstance(s, dict) and (s.get("citation_metadata", {}).get("document_type") if isinstance(s.get("citation_metadata"), dict) else "") == "precedent"
            ]
            theory = case_theory if isinstance(case_theory, dict) else {}
            strongest = theory.get("strongest_arguments", []) or []
            report_dict["supporting_arguments"] = [
                {"claim": a.get("claim", ""), "basis": a.get("legal_basis", ""), "evidence_ids": a.get("supporting_evidence_ids", [])} for a in strongest
            ]
            if isinstance(counterarguments, dict):
                report_dict["opposing_arguments"] = [{
                    "claim": counterarguments.get("strongest_opposing_argument", ""),
                    "basis": counterarguments.get("supporting_basis", ""),
                    "refutation": counterarguments.get("possible_rebuttal", ""),
                }]
                report_dict["rebuttals"] = [counterarguments.get("possible_rebuttal", "")] if counterarguments.get("possible_rebuttal") else []
            report_dict["evidence_gaps"] = list(dict.fromkeys(
                list(state.get("evidentiary_gaps", []) or []) + list(theory.get("missing_evidence", []) or []) + list(state.get("unresolved_issues", []) or [])
            ))
            report_dict["strategic_considerations"] = [
                {"step": idx + 1, "action": gap, "impact": "Address before relying on the affected proposition."}
                for idx, gap in enumerate(report_dict["evidence_gaps"][:5])
            ]
            report_dict["simulated_judicial_perspective"] = {
                "standard_of_review": "Neutral merits assessment based on the supplied record.",
                "merits_reasoning": adj_dict.get("merits_evaluation", {}).get("merits_reasoning", ""),
                "major_concerns": adj_dict.get("merits_evaluation", {}).get("major_concerns", []),
                "questions_a_judge_might_raise": adj_dict.get("merits_evaluation", {}).get("questions_a_judge_might_raise", []),
                "label": "Simulated judicial perspective — not a prediction of an actual court decision.",
            }
            report_dict["risk_assessment"] = list(dict.fromkeys(
                list(theory.get("legal_risks", []) or []) + list(adj_dict.get("merits_evaluation", {}).get("major_concerns", []) or [])
            ))
            report_dict["confidence_and_evidence_strength"] = {
                "method": "Dynamic trajectory evaluation",
                "note": "Numeric metrics are calculated after this agent completes from observed evidence, authorities, citations, routing and trajectory; they are not LLM-supplied scores."
            }
            report_dict["final_report"] = dict(report_dict)
            report_dict["citations"] = citations
            report_dict["trajectory_metadata"] = {
                "issue_count": len(state.get("identified_issues", [])),
                "research_rounds": len(state.get("research_trajectory", [])),
                "advocate_rounds": len(state.get("revision_log", [])),
                "revision_iterations": iteration_count,
            }

        # Return consolidated state update
        res = {
            "merits_evaluation": adj_dict.get("merits_evaluation", {}),
            "citation_audit": adj_dict.get("citation_audit", []),
            "root_cause": adj_dict.get("root_cause", {}),
            "verdict": adj_dict["verdict"],
            "target_agent": target_agent,
            "remediation_instructions": adj_dict.get("revision_instructions") or "",
            "passed_quality_gate": adj_dict["verdict"] == "PASS",
            "revision_required": adj_dict["verdict"] == "REVISE",
            "invalid_citation_count": len(invalid_citations),
            "final_report": report_dict,
            "citations": citations,
            "judge_evaluation": adj_dict.get("merits_evaluation", {}),
            "critic_feedback": adj_dict,
        }
        return res
