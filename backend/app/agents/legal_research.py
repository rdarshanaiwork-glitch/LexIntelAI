import time
from typing import Dict, Any, List, Optional
from app.agents.base import BaseLegalAgent
from app.schemas.agent_schemas import ResearchStep, LegalResearchOutput, LegalResearchSynthesis, RetrievedSourceChunk
from app.tools.legal_tools import LegalToolRegistry
from app.workflows.context import compact_json

ACTION_TO_SOURCE_TYPE = {
    "search_statute": "statute",
    "search_precedent": "precedent",
    "search_general": None,
}


class LegalResearchAgent(BaseLegalAgent):
    """
    5-agent architecture: Agent 2.

    Merges the former ResearchAgent + StatuteAgent + PrecedentAgent into
    a single agent that runs its own bounded tool-use loop, instead of
    three separate one-shot agents each making exactly one fixed
    top_k=N tool call in a preset order.

    How the loop works, each turn:
      1. The model is shown the issues, what's been searched so far,
         and the RESULTS of the previous search (not just "did results
         come back", but their actual content).
      2. The model returns a structured ResearchStep: it judges the
         prior results, decides whether coverage is now sufficient,
         and if not, picks the next tool (statute / precedent /
         general) and writes its own reformulated query.
      3. If it chose to keep searching, we actually execute that tool
         call via LegalToolRegistry, append the (deduplicated, relevant
         subset of) results to the running context, and loop.
      4. The loop stops when the model says "finish" / coverage_sufficient,
         or when MAX_ITERATIONS is hit as a hard safety ceiling.
      5. A final structured call synthesizes everything gathered into
         per-issue findings.

    Intellectual decisions this agent makes (not rule-based):
      - Search-strategy selection per issue (statute-first vs
        precedent-first vs general), based on reasoning about the
        legal nature of the issue.
      - Query formulation and reformulation, based on judging the
        actual content of prior results, not a static concatenated query.
      - Content-based relevance judgment, replacing the old
        `if not results: "INSUFFICIENT EVIDENCE"` non-empty check.
      - The stopping decision itself (diminishing returns), instead of
        a hardcoded top_k count regardless of quality.

    What stays rule-based on purpose:
      - MAX_ITERATIONS is a hard engineering ceiling to prevent runaway
        search loops / cost. It bounds *how many* attempts are allowed,
        not *what* the model decides within each attempt.
    """

    MAX_ITERATIONS = 3
    RESULTS_PER_SEARCH = 5

    def __init__(self, llm_provider=None):
        super().__init__(
            name="LegalResearchAgent",
            description=(
                "Runs an autonomous, bounded tool-use loop over statute, precedent, and "
                "general legal search — deciding its own search strategy, query phrasing, "
                "relevance judgment, and stopping point."
            ),
            llm_provider=llm_provider
        )

    def _decide_next_step(
        self,
        issues_text: str,
        transcript: List[Dict[str, Any]],
        step_number: int
    ) -> ResearchStep:
        system_prompt = (
            "You are a Senior Legal Research Librarian running your own research loop. "
            "On each turn you must: (1) judge the relevance and quality of the PRIOR search "
            "results shown below (if any) -- not merely whether results exist, but whether "
            "they actually address the issue; (2) decide whether overall coverage across all "
            "issues is now sufficient; (3) if not, choose the single best next action -- "
            "search_statute (local verified statutes), search_precedent (local verified case law), "
            "search_general (local repository), or search_live_web (live web search for external court judgments, "
            "appellate precedents, or recent law articles) -- and write a properly "
            "reformulated legal-research query for it, phrased the way a law librarian would, "
            "not the raw client narrative. Never claim coverage is sufficient without having "
            "actually searched at least once."
        )

        transcript_text = compact_json(transcript, 14000) if transcript else "None yet (first step)."

        prompt = (
            f"Legal Issues To Research:\n{issues_text}\n\n"
            f"Steps taken so far: {len(transcript)}\n"
            f"Research Transcript:\n{transcript_text}\n\n"
            f"This is step {step_number} of at most {self.MAX_ITERATIONS}. "
            "Judge prior results (if any), decide if coverage is sufficient, and choose the next action."
        )

        return self.llm.generate_structured(prompt, system_prompt, ResearchStep)

    def _synthesize(self, issues_text: str, transcript: List[Dict[str, Any]]) -> LegalResearchOutput:
        system_prompt = (
            "You are a Senior Legal Research Librarian finalizing your research memo. "
            "Synthesize everything actually retrieved across all search steps into structured, "
            "per-issue findings. Distinguish controlling authority from persuasive/tangential "
            "authority. If an issue never turned up controlling authority despite searching, "
            "say so explicitly in unresolved_issues rather than fabricating a source."
        )

        all_results = [r for t in transcript for r in t["results"]]
        transcript_text = "\n\n".join(
            f"Step {t['step']} ({t['action']}, query=\"{t['query']}\"): "
            + (", ".join(r["title"] for r in t["results"]) if t["results"] else "no results")
            for t in transcript
        ) or "No searches were executed."

        prompt = (
            f"Legal Issues:\n{issues_text}\n\n"
            f"Search Transcript:\n{transcript_text}\n\n"
            f"Full Retrieved Content:\n{compact_json(all_results, 4000)}\n\n"
            "Produce structured findings, one per issue, plus a coverage assessment and any "
            "unresolved issues."
        )

        time.sleep(0.8)  # Let token bucket refill before synthesis
        synth = self.llm.generate_structured(prompt, system_prompt, LegalResearchSynthesis)
        output = LegalResearchOutput(
            findings=synth.findings,
            coverage_assessment=synth.coverage_assessment,
            unresolved_issues=synth.unresolved_issues,
            retrieved_sources=[RetrievedSourceChunk.model_validate(r) for r in all_results],
            search_queries_used=[t["query"] for t in transcript if t.get("query")],
            total_search_rounds=len(transcript)
        )
        return output

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        issues = state.get("identified_issues") or [
            {"issue": i} for i in state.get("legal_issues", [])
        ]
        issues_text = "\n".join(f"- {i.get('issue', i) if isinstance(i, dict) else i}" for i in issues) \
            or state.get("user_query", "")

        transcript: List[Dict[str, Any]] = []

        for step_number in range(1, self.MAX_ITERATIONS + 1):
            decision = self._decide_next_step(issues_text, transcript, step_number)

            if decision.next_action == "finish" or decision.coverage_sufficient:
                break

            query = decision.query or issues_text
            if decision.next_action == "search_live_web":
                raw_results = LegalToolRegistry.search_live_web_precedents(query=query, max_results=self.RESULTS_PER_SEARCH)
            else:
                source_type = ACTION_TO_SOURCE_TYPE.get(decision.next_action)
                raw_results = LegalToolRegistry.search_legal_knowledge(
                    query=query, top_k=self.RESULTS_PER_SEARCH, source_type=source_type,
                    jurisdiction=state.get("case_context", {}).get("jurisdiction")
                )

            transcript.append({
                "step": step_number,
                "action": decision.next_action,
                "query": query,
                "reasoning": decision.reasoning,
                "results": raw_results,
            })

            # Hard safety ceiling reached this turn -- stop even if the model
            # would have kept going, to bound cost/runaway loops.
            if step_number == self.MAX_ITERATIONS:
                break

        output = self._synthesize(issues_text, transcript)
        result = output.model_dump()
        result["research_trajectory"] = transcript

        # Compatibility alias for the canonical research state.
        result["key_findings"] = [f["key_principle"] for f in result.get("findings", [])]

        return result
