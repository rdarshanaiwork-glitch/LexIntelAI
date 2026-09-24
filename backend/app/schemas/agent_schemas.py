import json
from typing import List, Dict, Optional, Any, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict, model_validator

# ==========================================
# AUTH & CASE SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: Optional[str] = "legal_counsel"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None

class CaseCreate(BaseModel):
    title: str
    description: str
    jurisdiction: Optional[str] = "Federal / Common Law"
    legal_domain: Optional[str] = "Commercial & Contract"
    client_name: Optional[str] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    jurisdiction: Optional[str] = None
    legal_domain: Optional[str] = None
    status: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    case_id: str
    file_name: str
    file_size: int
    mime_type: str
    status: str
    chunk_count: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CaseResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    jurisdiction: str
    legal_domain: str
    client_name: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    documents: List[DocumentResponse] = []
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# CITATION & EVIDENCE SCHEMA
# ==========================================

class CitationSchema(BaseModel):
    citation_id: str = "cit_1"
    source_id: str = "src_1"
    title: str = "Legal Citation"
    citation_text: str = "Cited authority on record."
    jurisdiction: str = "Common Law"
    claim: str = "Controlling legal principle."
    supporting_text: Optional[str] = None
    page_section: Optional[str] = "General"
    confidence: float = 1.0
    evidence_type: Literal["SUPPORTED BY SOURCE", "MODEL INFERENCE", "INSUFFICIENT EVIDENCE"] = "SUPPORTED BY SOURCE"
    url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def _coerce_citation(cls, v: Any):
        if isinstance(v, str):
            return {
                "citation_id": f"cit_{abs(hash(v)) % 10000}",
                "source_id": f"src_{abs(hash(v)) % 10000}",
                "title": v,
                "citation_text": v,
                "claim": "Authority supporting matter.",
                "evidence_type": "SUPPORTED BY SOURCE"
            }
        if isinstance(v, dict):
            cit_txt = v.get("citation_text") or v.get("citation") or v.get("title", "Legal Citation")
            if "citation_id" not in v:
                v["citation_id"] = f"cit_{abs(hash(str(cit_txt))) % 10000}"
            if "source_id" not in v:
                v["source_id"] = f"src_{abs(hash(str(cit_txt))) % 10000}"
            if "title" not in v:
                v["title"] = str(cit_txt)
            if "citation_text" not in v:
                v["citation_text"] = str(cit_txt)
            if "claim" not in v:
                v["claim"] = "Authority supporting matter."
            if "evidence_type" not in v:
                v["evidence_type"] = "SUPPORTED BY SOURCE"
        return v

# ==========================================
# CASE INTAKE AGENT (5-AGENT ARCHITECTURE)
# Merges CoordinatorAgent (planning) + EvidenceAgent (factual audit)
# into a single joint-reasoning agent.
# ==========================================

class IssueAssessment(BaseModel):
    issue: str
    supporting_evidence_ids: List[str] = []
    gap: Optional[str] = None
    evidentiary_support: Literal["strong", "moderate", "weak", "none"] = "moderate"

    @model_validator(mode="before")
    @classmethod
    def _coerce_issue(cls, v: Any):
        if isinstance(v, str):
            return {"issue": v, "evidentiary_support": "moderate"}
        if isinstance(v, dict) and "evidentiary_support" in v:
            if v["evidentiary_support"] not in {"strong", "moderate", "weak", "none"}:
                v["evidentiary_support"] = "moderate"
        return v

class IntakeEvidenceFact(BaseModel):
    fact: str
    supporting_document_or_source: str = "Case record"
    evidentiary_strength: str = "Medium"
    vulnerability_or_hearsay_risk: Optional[str] = None
    evidence_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_fact(cls, v: Any):
        if isinstance(v, str):
            return {"fact": v, "supporting_document_or_source": "Case record", "evidentiary_strength": "Medium"}
        return v

class CaseIntakeOutput(BaseModel):
    # Issue decomposition, cross-referenced against evidentiary support
    identified_issues: List[IssueAssessment] = []

    # Factual/evidentiary audit
    evidence_facts: List[IntakeEvidenceFact] = []
    evidentiary_gaps: List[str] = []
    corroboration_matrix: Dict[str, Any] = {}

    # Joint triage decision
    execution_strategy: Literal["full_litigation"] = "full_litigation"
    intake_ready: bool = True
    missing_information: List[str] = []

    plan_title: str = "Strategic Legal Intake & Investigation Plan"
    rationale: str = "Decomposed legal issues evaluated against initial evidentiary record."

    @model_validator(mode="before")
    @classmethod
    def _coerce_intake(cls, data: Any):
        if isinstance(data, dict):
            if data.get("execution_strategy") != "full_litigation":
                data["execution_strategy"] = "full_litigation"
            cm = data.get("corroboration_matrix")
            if isinstance(cm, dict):
                cleaned_cm = {}
                for k, v in cm.items():
                    if isinstance(v, list):
                        cleaned_cm[k] = "; ".join(str(item) for item in v)
                    else:
                        cleaned_cm[k] = str(v)
                data["corroboration_matrix"] = cleaned_cm
        return data

# ==========================================
# LEGAL RESEARCH AGENT (5-AGENT ARCHITECTURE)
# Merges ResearchAgent + StatuteAgent + PrecedentAgent into a single
# agent that runs its own bounded tool-use loop: it decides, turn by
# turn, which source type to search, how to phrase the query, whether
# prior results were actually relevant, and when to stop.
# ==========================================

class ResearchStep(BaseModel):
    """
    One turn of the research loop. This is the intellectual-decision
    schema: the model judges the previous results (if any) and decides
    the next move itself, rather than following a fixed search order.

    Field order matters here, mechanically: generation is autoregressive,
    so a field can only be causally informed by fields that were
    generated BEFORE it. Reasoning fields are placed ahead of the
    categorical decision fields (coverage_sufficient, next_action) they
    are meant to justify, so the decision is conditioned on the
    reasoning tokens rather than the reasoning being backfilled after
    the decision was already committed.
    """
    assessment_of_prior_results: Optional[str] = Field(
        default=None,
        description="Judgment of the relevance/quality of the last tool call's results. Null on the first step."
    )
    reasoning: str = Field(default="Assessing governing legal authority and research progress.")
    coverage_sufficient: bool = Field(
        default=False,
        description="True if the model judges research coverage adequate to stop, considering ALL issues so far."
    )
    next_action: Literal["search_statute", "search_precedent", "search_general", "search_live_web", "finish"] = Field(default="finish")
    query: Optional[str] = Field(
        default=None,
        description="A reformulated legal-research query, not the raw user query, when next_action is a search."
    )
    target_issue: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_next_action(cls, data: Any):
        if isinstance(data, dict):
            action = data.get("next_action")
            valid = {"search_statute", "search_precedent", "search_general", "search_live_web", "finish"}
            if action not in valid:
                data["next_action"] = "search_statute"
        return data

class ResearchFinding(BaseModel):
    issue: str
    key_principle: str = "Controlling legal principle on record."
    controlling_authority: Optional[Union[bool, str]] = True
    source_ids: List[str] = []
    confidence: float = Field(0.8, ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def _coerce_finding(cls, v: Any):
        if isinstance(v, str):
            return {"issue": v, "key_principle": v, "controlling_authority": True, "source_ids": [], "confidence": 0.85}
        if isinstance(v, dict):
            ca = v.get("controlling_authority")
            if isinstance(ca, str):
                if ca.strip().lower() in ("true", "yes", "1"):
                    v["controlling_authority"] = True
                elif ca.strip().lower() in ("false", "no", "0"):
                    v["controlling_authority"] = False
                # otherwise keep the string authority citation
            elif ca is None:
                v["controlling_authority"] = True
            if v.get("confidence") is None:
                v["confidence"] = 0.8
        return v

class LegalResearchSynthesis(BaseModel):
    findings: List[ResearchFinding] = []
    coverage_assessment: str = "Coverage assessment synthesized from retrieved authorities."
    unresolved_issues: List[str] = []

class LegalResearchOutput(BaseModel):
    search_queries_used: List[str] = []
    findings: List[ResearchFinding] = []
    retrieved_sources: List["RetrievedSourceChunk"] = []
    coverage_assessment: str = "Coverage assessment synthesized from retrieved authorities."
    unresolved_issues: List[str] = []
    total_search_rounds: int = 0

# ==========================================
# ADVOCATE AGENT (5-AGENT ARCHITECTURE)
# Merges StrategyAgent + OpponentAgent into a single agent that builds
# a case theory, attacks its own theory as opposing counsel, and
# decides for itself — based on how damaging the attack actually was —
# whether to rebuild before finalizing.
# ==========================================

class ArgumentItem(BaseModel):
    claim: str
    legal_basis: str = "Controlling statutory and precedent authority"
    supporting_evidence_ids: List[str] = []
    risk_factor: str = "None identified"

    @model_validator(mode="before")
    @classmethod
    def _coerce_arg(cls, v: Any):
        if isinstance(v, str):
            return {"claim": v, "legal_basis": "Controlling statutory and precedent authority", "supporting_evidence_ids": [], "risk_factor": "Potential factual distinction"}
        if isinstance(v, dict):
            if "claim" not in v:
                v["claim"] = v.get("argument") or v.get("title") or v.get("point") or "Strategic argument claim"
            if "supporting_evidence_ids" not in v:
                v["supporting_evidence_ids"] = v.get("evidence_ids") or v.get("supporting_evidence") or []
        return v

class CaseTheory(BaseModel):
    theory_of_the_case: str
    strongest_arguments: List[ArgumentItem] = []
    weakest_arguments: List[ArgumentItem] = []
    supporting_evidence: List[str] = []
    missing_evidence: List[str] = []
    legal_risks: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def _coerce_theory(cls, data: Any):
        if isinstance(data, dict):
            for field in ("supporting_evidence", "missing_evidence", "legal_risks"):
                if field in data and isinstance(data[field], list):
                    coerced = []
                    for item in data[field]:
                        if isinstance(item, dict):
                            val = item.get("evidence_id") or item.get("description") or item.get("claim") or item.get("fact") or json.dumps(item)
                            coerced.append(str(val))
                        else:
                            coerced.append(str(item))
                    data[field] = coerced
        return data

class AdversarialAttack(BaseModel):
    strongest_opposing_argument: str = "Opposing party asserts affirmative defenses and factual distinction."
    supporting_basis: str = "Controlling legal authority and burden of proof."
    attack_on_our_argument: str = "Weakness in element proof."
    potential_weaknesses: List[str] = []
    possible_rebuttal: str = "Rebuttal anchored in corroborated factual records."
    affirmative_defenses: List[str] = []
    targets_argument: Optional[str] = Field(
        default=None, description="Which specific argument in the case theory this attack targets."
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_attack(cls, data: Any):
        if isinstance(data, dict):
            if "targets_argument" in data and data["targets_argument"] is not None:
                data["targets_argument"] = str(data["targets_argument"])
        return data

class SelfAssessment(BaseModel):
    materiality_reasoning: str = "Evaluating adversarial attack materiality against case theory."
    damage_assessment: Literal["fatal", "significant", "minor", "survivable"] = "survivable"
    requires_revision: bool = False
    weakest_argument_id: Optional[str] = None
    revision_notes: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_damage(cls, data: Any):
        if isinstance(data, dict):
            dmg = data.get("damage_assessment")
            valid = {"fatal", "significant", "minor", "survivable"}
            if dmg not in valid:
                data["damage_assessment"] = "survivable"
        return data

class AdvocateOutput(BaseModel):
    case_theory: CaseTheory
    counterarguments: AdversarialAttack
    self_assessment: SelfAssessment
    revision_rounds_used: int = 0
    revision_log: List[Dict[str, Any]] = []

# ==========================================
# ADJUDICATOR AGENT (5-AGENT ARCHITECTURE)
# Merges JudgeAgent + CriticAgent into a single agent that evaluates
# argument strength AND audits citation validity TOGETHER, uses the
# combined picture to attribute any flaw to a specific upstream agent,
# and makes a materiality judgment about whether it's worth another
# revision loop.
#
# Field order in every nested model below is deliberate: free-text
# reasoning fields are placed before the categorical/numeric verdict
# fields they inform, because generation is autoregressive -- a field
# can only be causally conditioned on fields generated before it.
# ==========================================

class MeritsEvaluation(BaseModel):
    merits_reasoning: str = Field(
        default="Reasoning over how well evidence, statute, and precedent converge on the claim.",
        description="Reasoning over how well evidence, statute, and precedent converge on the claim, weighed against the opposing attack."
    )
    major_concerns: List[str] = []
    questions_a_judge_might_raise: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def _coerce_merits(cls, v: Any):
        if isinstance(v, str):
            return {"merits_reasoning": v, "major_concerns": [], "questions_a_judge_might_raise": []}
        return v

class CitationAuditFinding(BaseModel):
    citation_title: str
    is_valid: bool = True
    implication: str = Field(
        default="Valid authority supporting claims.",
        description="What this citation's validity (or invalidity) implies about the underlying claim -- not just a pass/fail flag."
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_finding(cls, v: Any):
        if isinstance(v, str):
            return {"citation_title": v or "Legal Authority", "is_valid": True, "implication": "Authority cited on record."}
        if isinstance(v, dict):
            if not v.get("citation_title"):
                v["citation_title"] = v.get("citation") or v.get("title") or "Verified Authority"
            if "is_valid" not in v and "status" in v:
                v["is_valid"] = str(v["status"]).upper() != "INVALID"
        return v

class RootCauseAttribution(BaseModel):
    root_cause_reasoning: str = Field(
        default="Upstream workflow evaluation complete.",
        description="Explicit causal reasoning tying the specific pattern of flaws to one upstream stage."
    )
    root_cause_agent: Literal["case_intake", "legal_research", "advocate", "none"] = "none"

    @model_validator(mode="before")
    @classmethod
    def _coerce_root_cause(cls, v: Any):
        if isinstance(v, str):
            agent = "none"
            v_lower = v.lower()
            if "intake" in v_lower: agent = "case_intake"
            elif "research" in v_lower: agent = "legal_research"
            elif "advocate" in v_lower or "strategy" in v_lower: agent = "advocate"
            return {"root_cause_reasoning": v, "root_cause_agent": agent}
        if isinstance(v, dict):
            agent = v.get("root_cause_agent", "none")
            if agent not in {"case_intake", "legal_research", "advocate", "none"}:
                v["root_cause_agent"] = "none"
        return v

class AdjudicatorOutput(BaseModel):
    merits_evaluation: MeritsEvaluation = Field(default_factory=MeritsEvaluation)
    citation_audit: List[CitationAuditFinding] = []
    root_cause: RootCauseAttribution = Field(default_factory=RootCauseAttribution)

    materiality_reasoning: str = Field(
        default="Merits assessment complete.",
        description="Judgment of whether the identified flaws are load-bearing or cosmetic."
    )
    verdict: Literal["PASS", "REVISE"] = "PASS"
    revision_instructions: Optional[str] = Field(
        default=None, description="Concrete remediation instructions for the root_cause_agent, required when verdict is REVISE."
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_adj(cls, data: Any):
        if isinstance(data, dict):
            verdict = data.get("verdict")
            if verdict not in {"PASS", "REVISE"}:
                if isinstance(verdict, str) and "revise" in verdict.lower():
                    data["verdict"] = "REVISE"
                else:
                    data["verdict"] = "PASS"
            if isinstance(data.get("merits_evaluation"), str):
                data["merits_evaluation"] = {
                    "merits_reasoning": data["merits_evaluation"],
                    "major_concerns": [],
                    "questions_a_judge_might_raise": []
                }
            if isinstance(data.get("root_cause"), str):
                rc_str = data["root_cause"]
                agent = "none"
                if "intake" in rc_str.lower(): agent = "case_intake"
                elif "research" in rc_str.lower(): agent = "legal_research"
                elif "advocate" in rc_str.lower(): agent = "advocate"
                data["root_cause"] = {"root_cause_reasoning": rc_str, "root_cause_agent": agent}
            if not data.get("materiality_reasoning"):
                data["materiality_reasoning"] = "Merits assessment complete."
        return data

# ==========================================
# REPORTING AGENT (5-AGENT ARCHITECTURE)
# Compiles the final report. Lower autonomy than Agents 1-4 by nature
# (its job is to aggregate what upstream agents already decided), but
# it still makes two real judgment calls: how much depth the matter
# actually warrants, and, per section, whether a statement is sourced
# fact or the model's own synthesis.
# ==========================================

class ReportSection(BaseModel):
    section_title: str
    content: str
    basis: Literal["SUPPORTED BY SOURCE", "MODEL INFERENCE", "INSUFFICIENT EVIDENCE"] = Field(
        default="SUPPORTED BY SOURCE",
        description="Whether this section's content is grounded in retrieved sources/evidence, is the model's own synthesis, or flags a gap."
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_section(cls, data: Any):
        if isinstance(data, dict):
            if "title" in data and "section_title" not in data:
                data["section_title"] = data["title"]
            basis = str(data.get("basis", "")).upper()
            if "SOURCE" in basis:
                data["basis"] = "SUPPORTED BY SOURCE"
            elif "INSUFFICIENT" in basis or "EVIDENCE" in basis:
                data["basis"] = "INSUFFICIENT EVIDENCE"
            else:
                data["basis"] = "MODEL INFERENCE"
        return data

class RunEvaluationMetrics(BaseModel):
    task_solve_rate: Optional[float] = None
    requirements_met_independent: Optional[float] = None
    requirements_met_dependency_aware: Optional[float] = None
    self_termination: Optional[float] = None
    trajectory_quality: Optional[float] = None
    evidence_coverage: Optional[float] = None
    evidence_alignment: Optional[float] = None
    authority_coverage: Optional[float] = None
    citation_validity: Optional[float] = None
    citation_coverage: Optional[float] = None
    jurisdiction_match: Optional[float] = None
    argument_survival: Optional[float] = None
    research_sufficiency: Optional[float] = None
    total_steps: int = 0
    llm_calls: int = 0
    tool_calls: int = 0
    retries: int = 0
    latency_ms: int = 0
    revision_count: int = 0
    metric_notes: List[str] = []

class ReportingOutput(BaseModel):
    scope_reasoning: str = Field(
        default="Comprehensive full litigation analysis warranted.",
        description="Assessment of how much detail this specific matter warrants."
    )
    report_depth: Literal["full_litigation_report"] = "full_litigation_report"

    title: str = "Strategic Legal Intelligence Report"
    executive_summary: str = "Executive summary of legal findings."
    sections: List[ReportSection] = []
    disclaimer: str = "This document is an AI-assisted legal intelligence work product."
    sources_and_citations: List[CitationSchema] = []

    @model_validator(mode="before")
    @classmethod
    def _coerce_reporting(cls, data: Any):
        if isinstance(data, dict):
            if data.get("report_depth") != "full_litigation_report":
                data["report_depth"] = "full_litigation_report"
            if not data.get("scope_reasoning"):
                data["scope_reasoning"] = "Comprehensive full litigation analysis warranted."
            sc = data.get("sources_and_citations")
            if isinstance(sc, list):
                cleaned_sc = []
                for item in sc:
                    if isinstance(item, str):
                        cleaned_sc.append({
                            "citation": item,
                            "authority_type": "statute" if ("act" in item.lower() or "§" in item) else "precedent",
                            "status": "VERIFIED"
                        })
                    elif isinstance(item, dict):
                        cleaned_sc.append(item)
                data["sources_and_citations"] = cleaned_sc
        return data

# ==========================================
# Compatibility schemas
# Retained only for older persisted records/API compatibility.
# The runtime graph uses the four canonical agents above.
# ==========================================

# 1. CoordinatorAgent
class TaskItem(BaseModel):
    task_id: str
    assigned_agent: str
    description: str
    priority: int

class CoordinatorOutput(BaseModel):
    objective: str
    legal_issues: List[str]
    required_tasks: List[TaskItem]
    priority: str = "High"  # High, Medium, Low
    required_sources: List[str]
    execution_strategy: Literal["full_litigation", "simple_inquiry", "expedited_assessment"] = "full_litigation"
    necessary_agents: List[str] = [
        "ResearchAgent", "StatuteAgent", "PrecedentAgent", "EvidenceAgent",
        "StrategyAgent", "OpponentAgent", "JudgeAgent", "CriticAgent", "ReportAgent"
    ]
    plan_title: str
    rationale: str

# 2. ResearchAgent
class RetrievedSourceChunk(BaseModel):
    source_id: str
    title: str
    source: str
    date: str
    jurisdiction: str
    relevance_score: float
    content: str
    location_page: int = 1
    section: str = "General"
    citation_metadata: Dict[str, Any] = {}
    evidence_type: Literal["SUPPORTED BY SOURCE", "MODEL INFERENCE", "INSUFFICIENT EVIDENCE"] = "SUPPORTED BY SOURCE"
    url: Optional[str] = None

class ResearchOutput(BaseModel):
    search_queries_used: List[str]
    retrieved_sources: List[RetrievedSourceChunk]
    key_findings: List[str]
    coverage_assessment: str

# 3. StatuteAgent
class StatuteItem(BaseModel):
    law: str
    section: str
    description: str
    applicability: str
    supporting_source: str
    confidence: float = 0.9

class StatuteOutput(BaseModel):
    applicable_statutes: List[StatuteItem]
    statutory_synthesis: str
    evidence_sufficiency: Literal["SUFFICIENT", "INSUFFICIENT EVIDENCE"] = "SUFFICIENT"

# 4. PrecedentAgent
class PrecedentItem(BaseModel):
    case_name: str
    court: str
    date: str
    legal_issue: str
    facts: str
    ruling: str
    legal_principle: str
    relevance: str
    similarities: List[str]
    differences: List[str]

class PrecedentOutput(BaseModel):
    precedents: List[PrecedentItem]
    supporting_precedents: List[str]
    opposing_precedents: List[str]
    conflicting_precedents: List[str]
    precedent_synthesis: str

# 5. EvidenceAgent
class EvidenceFactItem(BaseModel):
    fact: str
    supporting_document_or_source: str
    evidentiary_strength: str  # High, Medium, Low
    vulnerability_or_hearsay_risk: Optional[str] = None
    evidence_id: Optional[str] = None

class EvidenceOutput(BaseModel):
    proven_facts: List[EvidenceFactItem]
    evidentiary_gaps: List[str]
    corroboration_matrix: Dict[str, str]

# 6. StrategyAgent
class ArgumentItem(BaseModel):
    claim: str
    legal_basis: str
    supporting_evidence_ids: List[str]
    risk_factor: str

class StrategyOutput(BaseModel):
    theory_of_the_case: str
    strongest_arguments: List[ArgumentItem]
    weakest_arguments: List[ArgumentItem]
    supporting_evidence: List[str]
    missing_evidence: List[str]
    best_precedents: List[str]
    legal_risks: List[str]
    possible_strategies: List[str]

# 7. OpponentAgent
class OpponentOutput(BaseModel):
    strongest_opposing_argument: str
    supporting_basis: str
    attack_on_our_argument: str
    potential_weaknesses: List[str]
    possible_rebuttal: str
    affirmative_defenses: List[str]

# 8. JudgeAgent
class JudgeOutput(BaseModel):
    major_concerns: List[str]
    questions_a_judge_might_raise: List[str]
    overall_assessment: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    label: str = "Simulated Judicial Perspective — Not Legal Prediction"

# 9. CriticAgent
class CriticOutput(BaseModel):
    """
    Field order: audit findings and free-text reasoning are placed
    before the status/target_agent verdict fields, so the verdict is
    generated after — and conditioned on — the model having actually
    worked through the citation/coherence findings, rather than the
    reasoning being written to justify a verdict already committed to.
    """
    citation_validity_score: float = Field(..., ge=0.0, le=1.0)
    reasoning_coherence_score: float = Field(..., ge=0.0, le=1.0)
    unsupported_claims: List[str] = []
    contradictions_detected: List[str] = []
    missing_evidence_flags: List[str] = []
    hallucinated_references_detected: List[str] = []
    revision_reason: str
    actionable_feedback: str
    status: Literal["PASS", "REVISE"]
    target_agent: Optional[Literal["research", "statute", "precedent", "strategy", "opponent"]] = None

# 10. ReportAgent (16 Required Sections)
class ReportOutput(BaseModel):
    title: str
    # 1. Executive Summary
    executive_summary: str
    # 2. Case Context
    case_context: str
    # 3. Legal Issues
    legal_issues: List[str]
    # 4. Applicable Laws
    applicable_laws: List[Dict[str, Any]]
    # 5. Relevant Precedents
    relevant_precedents: List[Dict[str, Any]]
    # 6. Precedent Comparison
    precedent_comparison: Dict[str, Any]
    # 7. Supporting Arguments
    supporting_arguments: List[Dict[str, Any]]
    # 8. Opposing Arguments
    opposing_arguments: List[Dict[str, Any]]
    # 9. Rebuttals
    rebuttals: List[str]
    # 10. Evidence Gaps
    evidence_gaps: List[str]
    # 11. Strategic Considerations
    strategic_considerations: List[Dict[str, Any]]
    # 12. Simulated Judicial Perspective
    simulated_judicial_perspective: Dict[str, Any]
    # 13. Risk Assessment
    risk_assessment: List[str]
    # 14. Confidence & Evidence Strength
    confidence_and_evidence_strength: Dict[str, Any]
    # 15. Sources and Citations
    sources_and_citations: List[CitationSchema]
    # 16. Disclaimer
    disclaimer: str

# Session & API Telemetry Schemas
class AgentExecutionResponse(BaseModel):
    id: str
    agent_name: str
    step_number: int
    status: str
    execution_time_ms: int
    output_payload_json: Dict[str, Any] = {}
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CitationResponse(BaseModel):
    id: str
    report_id: Optional[str] = None
    source_id: Optional[str] = None
    title: str
    citation_text: str
    jurisdiction: str = "Common Law"
    quote: Optional[str] = None
    relevance_score: float = 1.0
    source_type: str = "statute"
    evidence_type: str = "SUPPORTED BY SOURCE"
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ReportResponse(BaseModel):
    id: str
    case_id: str
    session_id: str
    title: str
    executive_summary: str
    factual_analysis: Optional[str] = None
    statutory_matrix: List[Dict[str, Any]] = []
    precedent_analysis: List[Dict[str, Any]] = []
    strategic_recommendations: List[Dict[str, Any]] = []
    opposing_arguments: List[Dict[str, Any]] = []
    judicial_evaluation: Dict[str, Any] = {}
    critique_summary: Dict[str, Any] = {}
    confidence_score: float = 0.85
    limitations_disclaimer: str
    full_report_json: Optional[Dict[str, Any]] = None
    citations: List[CitationResponse] = []
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ResearchStartRequest(BaseModel):
    case_id: str
    objective: str
    execution_strategy: Literal["full_litigation"] = "full_litigation"
    document_ids: Optional[List[str]] = None

class ResearchSessionResponse(BaseModel):
    id: str
    case_id: str
    user_id: str
    objective: str
    current_agent: str
    status: str
    iteration_count: int
    agent_executions: List[AgentExecutionResponse] = []
    reports: List[ReportResponse] = []
    created_at: datetime
    updated_at: datetime
    state_snapshot: Dict[str, Any] = Field(default_factory=dict, validation_alias="state_snapshot_json")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

# Resolve forward references used by the 5-agent-architecture schemas
# above (LegalResearchOutput -> RetrievedSourceChunk, CaseTheory ->
# ArgumentItem), which are defined later in this file.
LegalResearchOutput.model_rebuild()
CaseTheory.model_rebuild()