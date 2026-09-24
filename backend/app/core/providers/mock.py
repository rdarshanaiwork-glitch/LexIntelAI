import logging
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel
from app.core.providers.base import BaseLLMProvider, T

logger = logging.getLogger("lexintel.llm.mock")

class MockLLMProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.2) -> str:
        return f"[LexIntel AI Reasoning Engine]\nQuery Analysis: {prompt[:120]}...\nAuthoritative consensus confirms controlling statutory and precedent frameworks apply."

    def generate_structured(self, prompt: str, system_prompt: Optional[str], response_model: Type[T], temperature: float = 0.2) -> T:
        name = response_model.__name__
        p_lower = prompt.lower()
        is_whistleblower = any(w in p_lower for w in ["whistleblower", "vance", "sox", "sarbanes", "retaliation", "fda", "clinical trial"])
        is_cyber = any(w in p_lower for w in ["cyber", "cfaa", "omnitech", "van buren", "computer fraud", "exceeds authorized access", "credentials"])

        logger.info(f"MockLLM generating structured response for {name} (Domain: {'Whistleblower' if is_whistleblower else 'Cyber' if is_cyber else 'Contract'})")
        data: dict = {}

        if name == "ReportingOutput":
            is_simple = "simple_inquiry" in prompt.lower()
            if is_simple:
                data = {
                    "scope_reasoning": "The matter was triaged as a simple inquiry with a single, well-supported issue and no adversarial revision cycles -- a brief memo is proportionate; a full 16-section litigation dossier would be padding.",
                    "report_depth": "simple_inquiry_brief",
                    "title": "LexIntel AI Legal Intelligence Brief",
                    "executive_summary": "This brief addresses the client's inquiry based on the applicable statutory and precedent authority located during research.",
                    "sections": [
                        {"section_title": "Issue & Governing Authority", "content": "The controlling statutory or common-law authority located during research directly addresses the inquiry.", "basis": "SUPPORTED BY SOURCE"},
                        {"section_title": "Practical Guidance", "content": "Based on the authority identified, the recommended course of action is outlined below, though this does not constitute a litigation strategy.", "basis": "MODEL INFERENCE"}
                    ],
                    "disclaimer": "DISCLAIMER: This system provides AI-assisted legal research and decision support for informational purposes. It does not constitute legal advice and does not replace a qualified legal professional.",
                    "sources_and_citations": []
                }
            else:
                data = {
                    "scope_reasoning": "The matter involves multiple interacting issues, went through adversarial self-play and at least one revision cycle, and carries real litigation stakes -- full-depth treatment is warranted so nothing material is compressed out.",
                    "report_depth": "full_litigation_report",
                    "title": "LexIntel AI Strategic Legal Intelligence Dossier",
                    "executive_summary": "Comprehensive multi-agent legal intelligence evaluation synthesizing statutory, precedent, evidentiary, adversarial, and judicial dimensions of the dispute.",
                    "sections": [
                        {"section_title": "Case Context & Legal Issues", "content": "The matter presents the legal issues identified during intake, cross-referenced against the evidentiary record.", "basis": "SUPPORTED BY SOURCE"},
                        {"section_title": "Applicable Law & Precedent", "content": "Controlling statutory and precedent authority located during research directly governs the primary claim.", "basis": "SUPPORTED BY SOURCE"},
                        {"section_title": "Case Theory & Adversarial Testing", "content": "The case theory was stress-tested through self-play adversarial review; the finalized theory survived that scrutiny after one revision round addressing a timing-element objection.", "basis": "SUPPORTED BY SOURCE"},
                        {"section_title": "Quality Review Findings", "content": "The Adjudicator's review is reflected in the confidence ratings and any flagged sourcing issues noted in the citations section.", "basis": "MODEL INFERENCE"},
                        {"section_title": "Risk Assessment & Strategic Considerations", "content": "Residual litigation risk and recommended next procedural steps are outlined based on the overall analysis.", "basis": "MODEL INFERENCE"},
                        {"section_title": "Evidentiary Gaps", "content": "Independent third-party damage valuation remains outstanding and is not yet corroborated.", "basis": "INSUFFICIENT EVIDENCE"}
                    ],
                    "disclaimer": "DISCLAIMER: This system provides AI-assisted legal research and decision support for informational purposes. It does not constitute legal advice, does not replace a qualified legal professional, and simulated judicial assessments are not predictions of actual court decisions.",
                    "sources_and_citations": []
                }

        elif name == "AdjudicatorOutput":
            invalid_cite_flag = "invalid --" in prompt.lower()
            if invalid_cite_flag:
                data = {
                    "merits_evaluation": {
                        "merits_reasoning": "The theory survived adversarial self-play and rests on a reasonably strong evidentiary anchor, but one relied-upon citation does not resolve against the verified knowledge base.",
                        "argument_strength": 0.78,
                        "evidence_strength": 0.8,
                        "precedent_strength": 0.55,
                        "major_concerns": ["A cited authority could not be verified against the knowledge base."],
                        "questions_a_judge_might_raise": ["Can counsel produce the source for the unverified citation, or substitute a verified one?"]
                    },
                    "citation_audit": [
                        {"citation_title": "Unverified Authority", "is_valid": False, "implication": "The underlying claim it supports is not currently sourced, even though the reasoning around it is otherwise sound."}
                    ],
                    "root_cause": {
                        "root_cause_reasoning": "The argument construction itself is coherent and survived self-attack; the flaw traces specifically to a citation that was never verified when the research findings were synthesized, not to weak reasoning.",
                        "root_cause_agent": "legal_research"
                    },
                    "materiality_reasoning": "An unverified citation supporting a load-bearing claim is significant enough to warrant one more pass, but the overall theory does not need to be rebuilt from scratch -- only the sourcing.",
                    "verdict": "REVISE",
                    "revision_instructions": "Re-verify or replace the flagged citation with one confirmed against the knowledge base before resynthesizing findings."
                }
            else:
                data = {
                    "merits_evaluation": {
                        "merits_reasoning": "The theory rests on a well-corroborated evidentiary anchor, survived adversarial self-play, and all cited authority resolves cleanly against the verified knowledge base.",
                        "argument_strength": 0.85,
                        "evidence_strength": 0.82,
                        "precedent_strength": 0.88,
                        "major_concerns": [],
                        "questions_a_judge_might_raise": ["Whether the secondary, lower-confidence claim needs independent damages substantiation."]
                    },
                    "citation_audit": [
                        {"citation_title": "Controlling Authority On Record", "is_valid": True, "implication": "The primary claim is properly sourced and supports the argument as framed."}
                    ],
                    "root_cause": {
                        "root_cause_reasoning": "No material flaw was identified in citations, argument construction, or the factual record.",
                        "root_cause_agent": "none"
                    },
                    "materiality_reasoning": "No load-bearing flaw was found; the analysis meets the quality bar for the final report as-is.",
                    "verdict": "PASS",
                    "revision_instructions": None
                }

        elif name == "ResearchStep":
            is_first_step = "Steps taken so far: 0" in prompt
            if is_first_step:
                domain_query = (
                    "SOX 1514A contractor employee whistleblower retaliation" if is_whistleblower else
                    "CFAA exceeds authorized access credentials trade secret misappropriation" if is_cyber else
                    "liquidated damages penalty clause enforceability foreseeability"
                )
                domain_action = "search_precedent" if (is_whistleblower or is_cyber) else "search_statute"
                data = {
                    "assessment_of_prior_results": None,
                    "coverage_sufficient": False,
                    "next_action": domain_action,
                    "query": domain_query,
                    "target_issue": None,
                    "reasoning": "No searches performed yet; starting with the source type most likely to control this issue."
                }
            else:
                data = {
                    "assessment_of_prior_results": "Prior results are on-point and directly address the controlling legal question.",
                    "coverage_sufficient": True,
                    "next_action": "finish",
                    "query": None,
                    "target_issue": None,
                    "reasoning": "Controlling authority has been located for the primary issue; further searching shows diminishing returns."
                }

        elif name == "LegalResearchOutput":
            if is_whistleblower:
                data = {
                    "search_queries_used": [],
                    "findings": [
                        {"issue": "Contractor employee standing under SOX § 1514A", "key_principle": "SOX whistleblower protection extends to contractor employees per Lawson v. FMR LLC.", "controlling_authority": True, "source_ids": [], "confidence": 0.93},
                        {"issue": "Protected activity via internal QA report", "key_principle": "Internal reporting of suspected fraud to a supervisor qualifies as protected activity under § 1514A(a)(1).", "controlling_authority": True, "source_ids": [], "confidence": 0.85}
                    ],
                    "retrieved_sources": [],
                    "coverage_assessment": "Controlling Supreme Court authority located on the standing question; statutory basis for the protected-activity issue is well established.",
                    "unresolved_issues": [],
                    "total_search_rounds": 0
                }
            elif is_cyber:
                data = {
                    "search_queries_used": [],
                    "findings": [
                        {"issue": "CFAA exceeds-authorized-access theory", "key_principle": "Van Buren limits CFAA liability to technological, not policy-based, access restrictions -- weakening this theory.", "controlling_authority": True, "source_ids": [], "confidence": 0.7},
                        {"issue": "Trade secret misappropriation via bulk download", "key_principle": "Unauthorized bulk downloading of proprietary data ahead of resignation supports a Defend Trade Secrets Act claim.", "controlling_authority": True, "source_ids": [], "confidence": 0.9}
                    ],
                    "retrieved_sources": [],
                    "coverage_assessment": "CFAA theory is adverse but well-researched; trade secret theory has strong statutory support.",
                    "unresolved_issues": ["Quantified valuation of the misappropriated trade secret material."],
                    "total_search_rounds": 0
                }
            else:
                data = {
                    "search_queries_used": [],
                    "findings": [
                        {"issue": "Enforceability of the liquidated damages clause", "key_principle": "Restatement (Second) of Contracts § 356 bars unreasonably large liquidated damages as unenforceable penalties.", "controlling_authority": True, "source_ids": [], "confidence": 0.92},
                        {"issue": "Foreseeability of the lost goodwill claim", "key_principle": "Hadley v. Baxendale bars consequential damages absent special notice of circumstances at contract formation.", "controlling_authority": True, "source_ids": [], "confidence": 0.88}
                    ],
                    "retrieved_sources": [],
                    "coverage_assessment": "Controlling common-law authority located for both the penalty-clause and foreseeability issues.",
                    "unresolved_issues": [],
                    "total_search_rounds": 0
                }

        elif name == "CaseTheory":
            is_revision = "PRIOR ATTACK" in prompt.upper()
            if not is_revision:
                data = {
                    "theory_of_the_case": "The client's position is anchored in controlling statutory protection and binding precedent, invalidating the opposing party's core theory.",
                    "strongest_arguments": [
                        {"claim": "Primary statutory or common-law protection strictly governs and favors the client.", "legal_basis": "Controlling statutory and precedent authority", "supporting_evidence_ids": ["EV-001"], "risk_factor": "Opponent may assert a factual distinction."}
                    ],
                    "weakest_arguments": [
                        {"claim": "Peripheral claim for consequential/goodwill damages.", "legal_basis": "General foreseeability doctrine", "supporting_evidence_ids": ["EV-002"], "risk_factor": "Lacks contemporaneous notice documentation."}
                    ],
                    "supporting_evidence": ["EV-001: Corroborated contemporaneous record"],
                    "missing_evidence": ["Independent third-party damage valuation"],
                    "legal_risks": ["Risk of prolonged motion practice."]
                }
            else:
                data = {
                    "theory_of_the_case": "Revised theory reframes the primary claim around the strongest corroborated evidence, dropping reliance on the timing-dependent element the prior attack exposed.",
                    "strongest_arguments": [
                        {"claim": "Reframed primary claim anchored to independently corroborated evidence rather than contested timing.", "legal_basis": "Controlling statutory authority, re-applied to the stronger evidentiary anchor", "supporting_evidence_ids": ["EV-003"], "risk_factor": "Opponent may raise a narrower, less severe objection."}
                    ],
                    "weakest_arguments": [
                        {"claim": "Peripheral consequential damages claim, now de-emphasized.", "legal_basis": "General foreseeability doctrine", "supporting_evidence_ids": ["EV-002"], "risk_factor": "Still lacks contemporaneous notice documentation."}
                    ],
                    "supporting_evidence": ["EV-003: Independently corroborated record addressing the prior objection"],
                    "missing_evidence": ["Independent third-party damage valuation"],
                    "legal_risks": ["Residual risk on the de-emphasized secondary claim only."]
                }

        elif name == "AdversarialAttack":
            is_second_round = "ROUND: 2" in prompt.upper()
            if not is_second_round:
                data = {
                    "strongest_opposing_argument": "The timing element the primary claim depends on is not actually established by the cited evidence -- it shows a related but distinct date.",
                    "supporting_basis": "Strict reading of the evidentiary record and the statutory timing requirement.",
                    "attack_on_our_argument": "The claim's core timing premise is unsupported as pleaded, which is fatal to the theory as currently framed.",
                    "potential_weaknesses": ["Evidence cited for the timing element does not actually establish that date.", "No fallback evidentiary anchor was offered."],
                    "possible_rebuttal": "A different, independently corroborated evidence item could establish the required timing without relying on the contested document.",
                    "affirmative_defenses": ["Statute of limitations on the timing-dependent theory."],
                    "targets_argument": "Primary statutory or common-law protection strictly governs and favors the client."
                }
            else:
                data = {
                    "strongest_opposing_argument": "Even with the reframed evidentiary anchor, the opposing party may argue the underlying obligation was substantially, if imperfectly, performed.",
                    "supporting_basis": "Substantial performance doctrine.",
                    "attack_on_our_argument": "This is a narrower objection than the prior one and does not undermine the reframed theory's core premise.",
                    "potential_weaknesses": ["Minor performance gap remains factually undisputed."],
                    "possible_rebuttal": "Substantial performance does not excuse the specific statutory violation at issue, which is a strict, not substantial-compliance, standard.",
                    "affirmative_defenses": ["Substantial performance (limited scope)."],
                    "targets_argument": "Reframed primary claim anchored to independently corroborated evidence rather than contested timing."
                }

        elif name == "SelfAssessment":
            is_second_round = "ROUND: 2" in prompt.upper()
            if not is_second_round:
                data = {
                    "materiality_reasoning": "The attack directly targets the timing element that the primary claim's strongest argument depends on, and the cited evidence does not actually establish that date -- this is load-bearing, not peripheral.",
                    "damage_assessment": "significant",
                    "requires_revision": True,
                    "weakest_argument_id": "Primary statutory or common-law protection strictly governs and favors the client.",
                    "revision_notes": "The attack exposes that the timing element is not actually supported by the cited evidence. Reframe the primary claim around a different, independently corroborated evidence item before finalizing."
                }
            else:
                data = {
                    "materiality_reasoning": "This second attack raises a substantial-performance objection against the reframed theory, but it targets a narrower, non-load-bearing point and does not undermine the reframed evidentiary anchor.",
                    "damage_assessment": "survivable",
                    "requires_revision": False,
                    "weakest_argument_id": None,
                    "revision_notes": None
                }

        elif name == "CaseIntakeOutput":
            if is_whistleblower:
                data = {
                    "identified_issues": [
                        {
                            "issue": "Whether an employee of an outsourced subsidiary qualifies as an 'employee' under SOX § 1514A",
                            "evidentiary_support": "strong",
                            "supporting_evidence_ids": ["EV-001"],
                            "gap": None
                        },
                        {
                            "issue": "Whether reporting internal trial data manipulation constitutes protected activity",
                            "evidentiary_support": "moderate",
                            "supporting_evidence_ids": ["EV-002"],
                            "gap": "Independent confirmation of report contents beyond claimant's own account is not yet on file."
                        }
                    ],
                    "evidence_facts": [
                        {"fact": "QA report on trial data manipulation was filed internally three weeks before termination.", "supporting_document_or_source": "Internal QA correspondence", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "Low; corroborated by timestamped email.", "evidence_id": "EV-001"},
                        {"fact": "Termination notice cites 'restructuring' as the stated basis.", "supporting_document_or_source": "Termination letter", "evidentiary_strength": "Medium", "vulnerability_or_hearsay_risk": "None; authenticated business record.", "evidence_id": "EV-002"}
                    ],
                    "evidentiary_gaps": ["Independent corroboration that the QA report specifically referenced trial data manipulation."],
                    "corroboration_matrix": {"Temporal proximity": "Corroborated by dated correspondence", "Content of report": "Partially corroborated; claimant account only"},
                    "execution_strategy": "full_litigation",
                    "intake_ready": True,
                    "missing_information": [],
                    "plan_title": "Whistleblower Retaliation Intake Assessment",
                    "rationale": "Strong temporal-proximity evidence and a clear statutory hook justify full litigation treatment; one issue carries a moderate evidentiary gap flagged for downstream research."
                }
            elif is_cyber:
                data = {
                    "identified_issues": [
                        {
                            "issue": "Whether an employee with valid credentials 'exceeds authorized access' under CFAA § 1030(a)(2)",
                            "evidentiary_support": "weak",
                            "supporting_evidence_ids": ["EV-001"],
                            "gap": "Van Buren precedent likely forecloses this theory on credentialed access alone; needs precedent research before relying on it."
                        },
                        {
                            "issue": "Misappropriation of trade secrets via bulk data download",
                            "evidentiary_support": "strong",
                            "supporting_evidence_ids": ["EV-002"],
                            "gap": None
                        }
                    ],
                    "evidence_facts": [
                        {"fact": "Employee held active, valid system credentials at time of download.", "supporting_document_or_source": "Access control logs", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "None; system-generated record.", "evidence_id": "EV-001"},
                        {"fact": "40GB of proprietary data was downloaded shortly before resignation.", "supporting_document_or_source": "Server logs", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "Low.", "evidence_id": "EV-002"}
                    ],
                    "evidentiary_gaps": ["Quantified valuation of the downloaded trade secret material."],
                    "corroboration_matrix": {"Download volume/timing": "Corroborated by server logs", "Trade secret status of data": "Not yet independently corroborated"},
                    "execution_strategy": "full_litigation",
                    "intake_ready": True,
                    "missing_information": [],
                    "plan_title": "Cyber Data Theft Intake Assessment",
                    "rationale": "CFAA theory is evidentiarily strong but legally fragile post-Van Buren; trade secret theory is both evidentiarily and legally strong, so full litigation treatment is warranted with prioritized research on the CFAA weakness."
                }
            else:
                data = {
                    "identified_issues": [
                        {
                            "issue": "Enforceability of the $5,000/day liquidated damages penalty clause",
                            "evidentiary_support": "strong",
                            "supporting_evidence_ids": ["EV-001"],
                            "gap": None
                        },
                        {
                            "issue": "Foreseeability of the $350,000 lost goodwill claim",
                            "evidentiary_support": "weak",
                            "supporting_evidence_ids": [],
                            "gap": "No documentation establishing that special commercial circumstances were communicated at contract formation."
                        }
                    ],
                    "evidence_facts": [
                        {"fact": "Delivery was delayed 4 days against a freight contract valued at $1,200.", "supporting_document_or_source": "Freight contract and delivery logs", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "Low; timestamped delivery record.", "evidence_id": "EV-001"},
                        {"fact": "Opposing party asserts $350,000 in lost goodwill without itemized support.", "supporting_document_or_source": "Demand letter", "evidentiary_strength": "Low", "vulnerability_or_hearsay_risk": "High; unverified claimant assertion.", "evidence_id": "EV-002"}
                    ],
                    "evidentiary_gaps": ["No contemporaneous notice of special commercial circumstances at contract formation."],
                    "corroboration_matrix": {"Delay timing": "Corroborated by delivery logs", "Goodwill loss amount": "Uncorroborated; no independent accounting"},
                    "execution_strategy": "full_litigation",
                    "intake_ready": True,
                    "missing_information": [],
                    "plan_title": "Commercial Freight Dispute Intake Assessment",
                    "rationale": "Penalty-clause issue is well-evidenced and legally strong; the goodwill claim is evidentiarily weak on the opposing side, which shapes how the case should be prioritized downstream."
                }

        elif name == "CoordinatorOutput":
            if is_whistleblower:
                data = {
                    "objective": "Evaluate whistleblower retaliation claims under Sarbanes-Oxley § 806 (18 U.S.C. § 1514A) and contractor employee standing under Lawson v. FMR LLC.",
                    "legal_issues": [
                        "Whether an employee of an outsourced subsidiary qualifies as an 'employee' under SOX § 1514A pursuant to Lawson v. FMR LLC",
                        "Whether reporting internal trial data manipulation constitutes protected activity under 18 U.S.C. § 1514A(a)(1)",
                        "Whether the plaintiff can establish contributing factor causation and overcome restructuring defense"
                    ],
                    "required_tasks": [
                        {"task_id": "T1", "assigned_agent": "EvidenceAgent", "description": "Audit temporal proximity between QA report and adverse action", "priority": 1},
                        {"task_id": "T2", "assigned_agent": "StatuteAgent", "description": "Dissect SOX § 1514A statutory elements and burdens of proof", "priority": 2},
                        {"task_id": "T3", "assigned_agent": "PrecedentAgent", "description": "Contrast Lawson v. FMR LLC regarding contractor standing", "priority": 3},
                        {"task_id": "T4", "assigned_agent": "StrategyAgent", "description": "Synthesize affirmative claims and settlement posture", "priority": 4}
                    ],
                    "priority": "High",
                    "required_sources": ["18 U.S.C. § 1514A", "Lawson v. FMR LLC (571 U.S. 429)"],
                    "execution_strategy": "full_litigation",
                    "necessary_agents": ["ResearchAgent", "StatuteAgent", "PrecedentAgent", "EvidenceAgent", "StrategyAgent", "OpponentAgent", "JudgeAgent", "CriticAgent", "ReportAgent"],
                    "plan_title": "Whistleblower Retaliation Strategic Plan",
                    "rationale": "High statutory reinstatement liability justifies prioritized review of contractor standing."
                }
            elif is_cyber:
                data = {
                    "objective": "Evaluate civil claim viability under Computer Fraud and Abuse Act (18 U.S.C. § 1030) in light of Supreme Court precedent Van Buren v. United States.",
                    "legal_issues": [
                        "Whether an employee with valid credentials 'exceeds authorized access' under § 1030(a)(2) by violating Acceptable Use Policies",
                        "Application of Van Buren's 'gates-up / gates-down' technological access model to enterprise data exfiltration",
                        "Satisfaction of the $5,000 aggregate annual loss threshold under 18 U.S.C. § 1030(g)"
                    ],
                    "required_tasks": [
                        {"task_id": "T1", "assigned_agent": "EvidenceAgent", "description": "Verify forensic audit logs and quantify $5,000 remediation costs", "priority": 1},
                        {"task_id": "T2", "assigned_agent": "StatuteAgent", "description": "Analyze CFAA § 1030(a)(2) civil standing requirements", "priority": 2},
                        {"task_id": "T3", "assigned_agent": "PrecedentAgent", "description": "Analyze Van Buren v. United States limiting CFAA to technological barriers", "priority": 3},
                        {"task_id": "T4", "assigned_agent": "StrategyAgent", "description": "Pivot claims toward Defend Trade Secrets Act and breach of contract", "priority": 4}
                    ],
                    "priority": "High",
                    "required_sources": ["18 U.S.C. § 1030", "Van Buren v. United States (593 U.S. 374)"],
                    "execution_strategy": "full_litigation",
                    "necessary_agents": ["ResearchAgent", "StatuteAgent", "PrecedentAgent", "EvidenceAgent", "StrategyAgent", "OpponentAgent", "JudgeAgent", "CriticAgent", "ReportAgent"],
                    "plan_title": "Cyber Data Theft & CFAA Jurisdictional Strategy",
                    "rationale": "Strong risk of Rule 12(b)(6) dismissal under Van Buren necessitates concurrent trade secret pleading."
                }
            else:
                data = {
                    "objective": "Evaluate enforceability of $5,000/day liquidated damages penalty clause and foreseeability of $350,000 lost goodwill claim.",
                    "legal_issues": [
                        "Enforceability of clause fixing liquidated damages at 4x freight price under Restatement (Second) of Contracts § 356",
                        "Foreseeability of remote commercial goodwill loss under the landmark rule of Hadley v. Baxendale",
                        "Whether commercial telematics outage constitutes excuse under Restatement § 241"
                    ],
                    "required_tasks": [
                        {"task_id": "T1", "assigned_agent": "EvidenceAgent", "description": "Audit delivery delay stamps and freight contract fee structures", "priority": 1},
                        {"task_id": "T2", "assigned_agent": "StatuteAgent", "description": "Examine Restatement § 356 and Uniform Commercial Code penalty doctrines", "priority": 2},
                        {"task_id": "T3", "assigned_agent": "PrecedentAgent", "description": "Compare Hadley v. Baxendale regarding special circumstance notice", "priority": 3},
                        {"task_id": "T4", "assigned_agent": "StrategyAgent", "description": "Formulate partial summary judgment on penalty doctrine", "priority": 4}
                    ],
                    "priority": "High",
                    "required_sources": ["Restatement (Second) of Contracts § 356", "Hadley v. Baxendale (1854)"],
                    "execution_strategy": "full_litigation",
                    "necessary_agents": ["ResearchAgent", "StatuteAgent", "PrecedentAgent", "EvidenceAgent", "StrategyAgent", "OpponentAgent", "JudgeAgent", "CriticAgent", "ReportAgent"],
                    "plan_title": "Commercial Freight Dispute & Penalty Defense Strategy",
                    "rationale": "Substantial financial exposure on penalty clause ($120k withheld) justifies immediate affirmative motion practice."
                }

            data["tasks"] = data.get("required_tasks", [])
            data["case_summary"] = data.get("objective", "")
            data["jurisdiction_analysis"] = "Jurisdiction analysis establishes governing standards and burdens of proof."
            data["recommended_agents"] = data.get("necessary_agents", [])
            data["plan_explanation"] = data.get("rationale", "")

        elif name == "ResearchOutput":
            if is_whistleblower:
                data = {
                    "search_queries_used": ["Sarbanes-Oxley 18 U.S.C. 1514A whistleblower", "Lawson v FMR LLC contractor standing"],
                    "retrieved_sources": [
                        {
                            "source_id": "statute_whistleblower_sox.txt", "title": "Sarbanes-Oxley Act § 806 (18 U.S.C. § 1514A)",
                            "source": "statute_whistleblower_sox.txt", "date": "2002-07-30", "jurisdiction": "US Federal", "relevance_score": 0.96,
                            "content": "No company registered under section 12... including any contractor, subcontractor, or agent... may discharge, demote, suspend, threaten, harass, or discriminate against an employee...",
                            "location_page": 1, "section": "Section 1514A", "citation_metadata": {"citation": "18 U.S.C. § 1514A", "document_type": "statute", "court": "US Congress"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        },
                        {
                            "source_id": "precedent_lawson_v_fmr.md", "title": "Lawson v. FMR LLC",
                            "source": "precedent_lawson_v_fmr.md", "date": "2014-03-04", "jurisdiction": "US Federal / Supreme Court", "relevance_score": 0.94,
                            "content": "Whistleblower protection under 18 U.S.C. § 1514A extends to employees of contractors and subcontractors of public companies...",
                            "location_page": 1, "section": "Holding and Rule of Law", "citation_metadata": {"citation": "571 U.S. 429", "document_type": "precedent", "court": "Supreme Court of the United States"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        }
                    ],
                    "key_findings": ["Lawson v. FMR LLC grants standing to contractor employees reporting fraud.", "Contributing factor standard governs causation."],
                    "coverage_assessment": "Comprehensive authority supporting whistleblower standing."
                }
            elif is_cyber:
                data = {
                    "search_queries_used": ["CFAA 18 U.S.C. 1030 exceeds authorized access", "Van Buren v United States gates up"],
                    "retrieved_sources": [
                        {
                            "source_id": "statute_cfaa_cyber_fraud.txt", "title": "Computer Fraud and Abuse Act (18 U.S.C. § 1030)",
                            "source": "statute_cfaa_cyber_fraud.txt", "date": "1986-10-16", "jurisdiction": "US Federal", "relevance_score": 0.95,
                            "content": "Whoever intentionally accesses a computer without authorization or exceeds authorized access, and thereby obtains information...",
                            "location_page": 1, "section": "Section 1030(a)(2)", "citation_metadata": {"citation": "18 U.S.C. § 1030", "document_type": "statute", "court": "US Congress"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        },
                        {
                            "source_id": "precedent_van_buren_v_us.md", "title": "Van Buren v. United States",
                            "source": "precedent_van_buren_v_us.md", "date": "2021-06-03", "jurisdiction": "US Federal / Supreme Court", "relevance_score": 0.93,
                            "content": "An individual exceeds authorized access when he accesses areas that are off-limits. The CFAA does NOT cover an individual with valid credentials who accesses information for an improper purpose.",
                            "location_page": 1, "section": "Holding and Rule of Law", "citation_metadata": {"citation": "593 U.S. 374", "document_type": "precedent", "court": "Supreme Court of the United States"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        }
                    ],
                    "key_findings": ["Van Buren creates severe jurisdictional barrier to CFAA claims where employee held valid credentials.", "Must pivot toward Defend Trade Secrets Act."],
                    "coverage_assessment": "Clear doctrinal conflict between corporate policy and federal CFAA threshold."
                }
            else:
                data = {
                    "search_queries_used": ["Restatement Second Contracts 356 liquidated damages penalty", "Hadley v Baxendale consequential damages"],
                    "retrieved_sources": [
                        {
                            "source_id": "statute_contract_law.txt", "title": "Restatement (Second) of Contracts § 356",
                            "source": "statute_contract_law.txt", "date": "1981-01-01", "jurisdiction": "Common Law", "relevance_score": 0.95,
                            "content": "A term fixing unreasonably large liquidated damages is unenforceable on grounds of public policy as a penalty.",
                            "location_page": 1, "section": "Section 356", "citation_metadata": {"citation": "Restat 2d Contracts § 356", "document_type": "statute", "court": "ALI"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        },
                        {
                            "source_id": "precedent_hadley_v_baxendale.md", "title": "Hadley v. Baxendale",
                            "source": "precedent_hadley_v_baxendale.md", "date": "1854-02-23", "jurisdiction": "Common Law", "relevance_score": 0.92,
                            "content": "Where two parties have made a contract which one of them has broken, damages should be such as may reasonably be supposed to have been in the contemplation of both parties.",
                            "location_page": 1, "section": "Holding and Rule of Law", "citation_metadata": {"citation": "(1854) 9 Exch 341", "document_type": "precedent", "court": "Court of Exchequer"},
                            "evidence_type": "SUPPORTED BY SOURCE"
                        }
                    ],
                    "key_findings": ["Liquidated damages fixed at 400% of freight price violate Section 356 public policy.", "Hadley rule bars uncommunicated lost retail goodwill."],
                    "coverage_assessment": "Comprehensive common law coverage on penalty doctrine."
                }

        elif name == "StatuteOutput":
            if is_whistleblower:
                data = {
                    "applicable_statutes": [
                        {"law": "Sarbanes-Oxley Act", "section": "18 U.S.C. § 1514A", "description": "Prohibits retaliatory adverse personnel actions against employees reporting fraud.", "applicability": "Directly triggered by QA report on trial manipulation.", "supporting_source": "18 U.S.C. § 1514A", "confidence": 0.95},
                        {"law": "AIR21 Burdens of Proof", "section": "49 U.S.C. § 42121(b)", "description": "Contributing factor causation governs.", "applicability": "3-week proximity establishes contributing factor.", "supporting_source": "49 U.S.C. § 42121(b)", "confidence": 0.92}
                    ],
                    "statutory_synthesis": "Statutory framework heavily favors employee once contributing factor causation is established.",
                    "evidence_sufficiency": "SUFFICIENT"
                }
            elif is_cyber:
                data = {
                    "applicable_statutes": [
                        {"law": "Computer Fraud and Abuse Act", "section": "18 U.S.C. § 1030(a)(2)", "description": "Liability for unauthorized access or exceeding authorized access.", "applicability": "Vulnerable: Marcus held active credentials.", "supporting_source": "18 U.S.C. § 1030(a)(2)", "confidence": 0.70},
                        {"law": "Defend Trade Secrets Act", "section": "18 U.S.C. § 1836", "description": "Civil action for misappropriation of trade secrets.", "applicability": "Highly applicable: Downloading 40GB proprietary data constitutes misappropriation.", "supporting_source": "18 U.S.C. § 1836", "confidence": 0.94}
                    ],
                    "statutory_synthesis": "Statutory relief is robust under trade secret statutes, but fragile under CFAA unauthorized access provisions.",
                    "evidence_sufficiency": "SUFFICIENT"
                }
            else:
                data = {
                    "applicable_statutes": [
                        {"law": "Restatement (Second) of Contracts", "section": "Section 356", "description": "Unreasonably large liquidated damages are unenforceable penalties.", "applicability": "$5,000/day penalty is disproportionate to $1,200 freight fee.", "supporting_source": "Restat 2d Contracts § 356", "confidence": 0.95},
                        {"law": "Restatement (Second) of Contracts", "section": "Section 241", "description": "Materiality of performance failure.", "applicability": "Delay of 4 days was technical breach, but delivery was tendered.", "supporting_source": "Restat 2d Contracts § 241", "confidence": 0.90}
                    ],
                    "statutory_synthesis": "Controlling contract provisions invalidate punitive liquidated damage terms.",
                    "evidence_sufficiency": "SUFFICIENT"
                }

        elif name == "PrecedentOutput":
            if is_whistleblower:
                data = {
                    "precedents": [
                        {
                            "case_name": "Lawson v. FMR LLC", "court": "Supreme Court of the United States", "date": "2014-03-04",
                            "legal_issue": "Whether SOX § 1514A shelters employees of private contractors.",
                            "facts": "Contractor employees discharged after reporting mutual fund accounting concerns.",
                            "ruling": "SOX whistleblower protection unequivocally extends to contractor employees.",
                            "legal_principle": "Contractor employees are insulated from retaliatory dismissal when reporting corporate fraud.",
                            "relevance": "Direct controlling precedent resolving Sterling BioPharm's standing defense.",
                            "similarities": ["Contractor personnel reporting fraud", "Corporate claim of lack of direct employment"],
                            "differences": ["Mutual fund accounting vs clinical safety reporting"]
                        }
                    ],
                    "supporting_precedents": ["Lawson v. FMR LLC (571 U.S. 429)"],
                    "opposing_precedents": [],
                    "conflicting_precedents": [],
                    "precedent_synthesis": "Lawson v. FMR LLC is unanimous binding authority defeating the primary defense of contractor standing."
                }
            elif is_cyber:
                data = {
                    "precedents": [
                        {
                            "case_name": "Van Buren v. United States", "court": "Supreme Court of the United States", "date": "2021-06-03",
                            "legal_issue": "Whether accessing data with valid credentials for unauthorized purpose violates CFAA.",
                            "facts": "Police sergeant with valid credentials searched database for personal payment.",
                            "ruling": "CFAA does NOT cover individual with lawful credentials who accesses info for improper purpose.",
                            "legal_principle": "CFAA liability requires technological gate-breaching, not contractual policy violation.",
                            "relevance": "Critical adverse precedent severely weakening OmniTech's CFAA claim against Marcus.",
                            "similarities": ["Employees with authorized credentials", "Downloading data contrary to employer policy"],
                            "differences": ["Criminal prosecution vs civil action with trade secret elements"]
                        }
                    ],
                    "supporting_precedents": [],
                    "opposing_precedents": ["Van Buren v. United States (593 U.S. 374)"],
                    "conflicting_precedents": ["Pre-Van Buren circuit decisions applying broad contract access tests"],
                    "precedent_synthesis": "Van Buren is binding adverse authority on the CFAA claim, necessitating trade secret alternative."
                }
            else:
                data = {
                    "precedents": [
                        {
                            "case_name": "Hadley v. Baxendale", "court": "Court of Exchequer", "date": "1854-02-23",
                            "legal_issue": "Whether carrier is liable for remote lost profits from delay without notice.",
                            "facts": "Mill crankshaft delayed 7 days by common carrier; mill idle and lost profits.",
                            "ruling": "Consequential damages recoverable only if in contemplation of both parties at formation.",
                            "legal_principle": "Consequential damages require foreseeability or explicit special notice.",
                            "relevance": "Direct authority barring Horizon's $350,000 lost goodwill claim.",
                            "similarities": ["Delayed commercial transportation", "Claim for enterprise lost profits"],
                            "differences": ["19th-century steam engine shaft vs modern refrigerated linehaul"]
                        }
                    ],
                    "supporting_precedents": ["Hadley v. Baxendale (1854) 9 Exch 341"],
                    "opposing_precedents": [],
                    "conflicting_precedents": [],
                    "precedent_synthesis": "Hadley v. Baxendale remains the foundational common law authority barring speculative consequential damages."
                }

        elif name == "EvidenceOutput":
            data = {
                "proven_facts": [
                    {"fact": "Documented notices and actions occurred within corroborated timeframes.", "supporting_document_or_source": "Case documentation record", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "Low; corroborated by business email timestamps.", "evidence_id": "EV-001"},
                    {"fact": "Financial withholding, adverse action, or computer exfiltration is formally recorded.", "supporting_document_or_source": "Corporate correspondence / Server logs", "evidentiary_strength": "High", "vulnerability_or_hearsay_risk": "None; authenticated business record.", "evidence_id": "EV-002"}
                ],
                "evidentiary_gaps": ["Complete pre-dispute internal correspondence required.", "Independent economic appraisal needed to substantiate claimed damages."],
                "corroboration_matrix": {"Action timing": "Corroborated by contemporaneous digital records", "Claimed damages": "Uncorroborated; lacks external accounting validation"}
            }

        elif name == "StrategyOutput":
            data = {
                "theory_of_the_case": "The client's position is anchored in controlling statutory protections and binding Supreme Court doctrine, shifting economic leverage by invalidating overreaching claims.",
                "strongest_arguments": [
                    {"claim": "Primary statutory or common law protection strictly governs the dispute.", "legal_basis": "Controlling statutory and precedent authority", "supporting_evidence_ids": ["EV-001"], "risk_factor": "Opponent will assert factual distinction or waiver."}
                ],
                "weakest_arguments": [
                    {"claim": "Attempting to claim absolute contractual immunity.", "legal_basis": "Equitable doctrines", "supporting_evidence_ids": ["EV-002"], "risk_factor": "Technical breach or policy infraction cannot be entirely denied."}
                ],
                "supporting_evidence": ["EV-001: Contemporaneous electronic notifications and delivery logs"],
                "missing_evidence": ["Independent third-party financial damage calculation"],
                "best_precedents": ["Controlling Supreme Court authority on point"],
                "legal_risks": ["Risk of prolonged motion practice incurring substantial litigation costs"],
                "possible_strategies": ["File early dispositive motion for partial summary judgment or dismissal.", "Serve formal settlement tender with fee-shifting notice."]
            }

        elif name == "OpponentOutput":
            data = {
                "strongest_opposing_argument": "Opponent will argue sophisticated commercial parties voluntarily bargained for strict risk allocation terms and operational policies.",
                "supporting_basis": "Freedom of contract and express terms of corporate agreement.",
                "attack_on_our_argument": "Client seeks to evade clear contractual commitments and established institutional rules through post-hoc legal doctrines.",
                "potential_weaknesses": ["Client's admitted deviation from standard performance timeline or policy parameters.", "Absence of secondary contingency systems during operational disruption."],
                "possible_rebuttal": "Public policy expressly invalidates disproportionate penalties and jurisdictional overreach regardless of contractual recitals.",
                "affirmative_defenses": ["Failure to mitigate damages", "Equitable estoppel and contractual waiver"]
            }

        elif name == "JudgeOutput":
            data = {
                "argument_strength": 0.82, "evidence_strength": 0.78, "precedent_strength": 0.88,
                "major_concerns": ["Whether factual record conclusively establishes full compliance with procedural notice preconditions."],
                "questions_a_judge_might_raise": ["Did the claiming party provide timely opportunity to cure before assessing unilateral withholding?", "What empirical benchmark was utilized at contract formation?"],
                "overall_assessment": "The court is highly likely to uphold the client's doctrinal defenses, significantly curtailing the opponent's financial demands.",
                "confidence": 0.85, "label": "Simulated Judicial Perspective — Not Legal Prediction"
            }

        elif name == "CriticOutput":
            data = {
                "status": "PASS", "target_agent": None,
                "revision_reason": "Analysis meets rigorous evidentiary, citation, and reasoning quality thresholds.",
                "citation_validity_score": 0.96, "reasoning_coherence_score": 0.94,
                "unsupported_claims": [], "contradictions_detected": [],
                "missing_evidence_flags": ["Quantification of third-party downtime costs"],
                "hallucinated_references_detected": [],
                "actionable_feedback": "Ensure all strategic recommendations emphasize that judicial simulations are decision-support aids rather than guarantees."
            }

        elif name == "ReportOutput":
            data = {
                "title": "LexIntel AI Strategic Legal Intelligence Dossier",
                "executive_summary": "Comprehensive multi-agent legal intelligence evaluation synthesizing statutory, precedent, evidentiary, adversarial, and judicial dimensions of the dispute. The analysis confirms that while technical obligations require management, the adverse party's outsized damages demands are legally vulnerable under established controlling doctrine.",
                "case_context": prompt[:300],
                "legal_issues": [
                    "Enforceability of challenged contractual or statutory provisions",
                    "Jurisdictional prerequisites and procedural standing",
                    "Quantum of provable damages versus speculative consequential loss"
                ],
                "applicable_laws": [
                    {"law": "Controlling Statutory Code", "section": "Primary Substantive Section", "relevance": "Directly governs legal liability standards", "finding": "Favorable"}
                ],
                "relevant_precedents": [
                    {"case": "Controlling Supreme Court Precedent", "citation": "Authoritative Reporter", "principle": "Direct statutory boundary rule", "application": "Defeats opponent's core theory"}
                ],
                "precedent_comparison": {
                    "supporting": ["Primary controlling appellate and supreme court precedent"],
                    "opposing": ["Distinguishable trial-level decisions with divergent factual records"],
                    "conflicting": ["Historical jurisdictional split resolved by recent high court authority"]
                },
                "supporting_arguments": [
                    {"claim": "Substantive legal doctrine strictly precludes the asserted penalty or overreach.", "basis": "Binding precedent and statutory text"}
                ],
                "opposing_arguments": [
                    {"claim": "Freedom of contract and strict corporate policy adherence.", "refutation": "Public policy firmly overrides private penalty covenants"}
                ],
                "rebuttals": ["Adverse party failed to provide required special notice at inception, barring remote consequential recovery."],
                "evidence_gaps": ["Contemporaneous communications establishing baseline mutual contemplation of risk."],
                "strategic_considerations": [
                    {"step": 1, "action": "File Partial Summary Judgment or Dismissal Motion", "impact": "Eliminate primary financial exposure"},
                    {"step": 2, "action": "Tender Confessed Actual Damage Amount", "impact": "Neutralize fee-shifting and prejudgment interest"},
                    {"step": 3, "action": "Engage in Structured Mediation", "impact": "Resolve dispute within realistic commercial boundaries"}
                ],
                "simulated_judicial_perspective": {
                    "standard_of_review": "De novo on legal questions; Preponderance of the evidence on factual claims",
                    "predicted_disposition": "80% likelihood court adopts client's doctrinal defenses and severely curtails adverse claims"
                },
                "risk_assessment": [
                    "Protracted trial discovery costs could exceed initial compromised settlement value.",
                    "Judicial reluctance to disturb sophisticated enterprise risk allocations without clear penalty proof."
                ],
                "confidence_and_evidence_strength": {
                    "overall_confidence": 0.88, "statutory_confidence": 0.94, "precedent_confidence": 0.92, "evidentiary_confidence": 0.80
                },
                "sources_and_citations": [
                    {
                        "citation_id": "CITE-001", "source_id": "statute_primary", "title": "Controlling Substantive Legal Authority",
                        "citation_text": "Statutory Authority On Record", "jurisdiction": "Common Law",
                        "claim": "Prohibits unreasonable penalties and overreaching liability claims.",
                        "supporting_text": "A term fixing unreasonably large damages is unenforceable on grounds of public policy.",
                        "page_section": "Section 1", "confidence": 0.96, "evidence_type": "SUPPORTED BY SOURCE"
                    }
                ],
                "disclaimer": "DISCLAIMER: This system provides AI-assisted legal research and decision support for informational purposes. It does not constitute legal advice, does not replace a qualified legal professional, and simulated judicial assessments are not predictions of actual court decisions."
            }

        return response_model.model_validate(data)
