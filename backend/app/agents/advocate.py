import time
from typing import Dict, Any, List
from app.agents.base import BaseLegalAgent
from app.schemas.agent_schemas import CaseTheory, AdversarialAttack, SelfAssessment, AdvocateOutput
from app.workflows.context import compact_json


class AdvocateAgent(BaseLegalAgent):
    """
    5-agent architecture: Agent 3.

    Merges the former StrategyAgent + OpponentAgent into a single agent
    that performs dialectical self-play: it builds a case theory, then
    switches persona to attack that theory as opposing counsel, then --
    the key addition that did not exist in the old fixed Strategy ->
    Opponent edge -- reads its OWN attack and judges whether it actually
    exposed something fatal, deciding for itself whether to rebuild
    before finalizing.

    Loop, each round:
      1. BUILD  — construct (or, on round 2+, rebuild) a case theory,
         informed by the prior round's self-assessment if this is a
         revision.
      2. ATTACK — same agent, opposing-counsel persona, sees only the
         finalized theory (not the model's confidence/reasoning about
         it) and attacks it as hard as it can. This separation keeps
         the attack genuinely adversarial rather than a softened
         self-critique that already "knows" it's on the same side.
      3. ASSESS — the agent reads both the theory and the attack and
         makes a materiality judgment: is this damage fatal/significant
         (worth rebuilding for) or minor/survivable (note and move on)?
      4. If requires_revision and rounds remain, loop back to BUILD with
         the assessment's revision_notes injected. Otherwise finalize.

    Intellectual decisions this agent makes (not rule-based):
      - Argument prioritization when building the theory (which claim
        is strongest) — a holistic judgment about convergence of
        evidence, statute, and precedent, not a formula.
      - Genuine adversarial reasoning when attacking — generating the
        actual strongest counterargument requires reasoning as if it
        doesn't already know its own answer is right.
      - Materiality judgment in the self-assessment: deciding whether a
        given objection is fatal to the theory's load-bearing premise,
        versus a survivable, note-worthy objection. This decision is
        what determines whether the loop runs again at all.

    What stays rule-based on purpose:
      - MAX_ROUNDS is a hard engineering ceiling, not a legal-reasoning
        decision, so it doesn't undercut the "intellectual" framing --
        only the total number of self-play attempts is bounded.
    """

    MAX_ROUNDS = 2

    def __init__(self, llm_provider=None):
        super().__init__(
            name="AdvocateAgent",
            description=(
                "Builds a case theory, attacks it as opposing counsel, and decides for itself "
                "-- based on the materiality of its own attack -- whether to rebuild before "
                "finalizing."
            ),
            llm_provider=llm_provider
        )

    def _build_theory(self, inputs_text: str, prior_round: Dict[str, Any] = None) -> CaseTheory:
        system_prompt = (
            "You are Lead Legal Counsel and Strategic Trial Architect. Build the theory of the "
            "case: pick the overall narrative, rank arguments strongest-to-weakest, and tie every "
            "factual assertion to a specific evidence ID so nothing is argued without a citable "
            "basis. Never argue a claim that isn't supported by the record provided."
        )

        prompt = f"Case Inputs:\n{inputs_text}\n\n"
        if prior_round:
            prompt += (
                f"PRIOR ATTACK on your last theory: {prior_round['attack']['attack_on_our_argument']}\n"
                f"Revision notes from self-assessment: {prior_round['assessment']['revision_notes']}\n\n"
                "Rebuild the theory to address this specific objection -- do not simply restate the "
                "prior theory. Prefer a different evidentiary anchor if the prior one was the "
                "problem.\n\n"
            )
        prompt += "Construct the case theory."

        return self.llm.generate_structured(prompt, system_prompt, CaseTheory)

    def _attack(self, theory: CaseTheory, round_number: int) -> AdversarialAttack:
        system_prompt = (
            "You are Adversarial Opposing Counsel. You are shown only the finalized case theory "
            "below -- not its author's confidence or reasoning about it. Rigorously attack this "
            "position: find the single weakest link, raise plausible affirmative defenses, and "
            "question whether the evidence actually supports the claim as strongly as asserted. "
            "Do not pull punches -- a soft attack is useless for stress-testing the theory."
        )

        prompt = (
            f"ROUND: {round_number}\n"
            f"Case Theory To Attack:\n"
            f"Theory: {theory.theory_of_the_case}\n"
            f"Strongest Arguments: {[a.claim for a in theory.strongest_arguments]}\n"
            f"Evidence Relied On: {theory.supporting_evidence}\n\n"
            "Deliver your strongest opposing argument and identify exactly which claim it targets."
        )

        return self.llm.generate_structured(prompt, system_prompt, AdversarialAttack)

    def _self_assess(self, theory: CaseTheory, attack: AdversarialAttack, round_number: int) -> SelfAssessment:
        system_prompt = (
            "You are the same Lead Counsel who built this theory, now reading the opposing attack "
            "against it. Make a materiality judgment, not a reflexive one: does this attack actually "
            "undermine the load-bearing premise of your strongest argument (fatal/significant -- "
            "worth rebuilding), or is it a real but survivable objection you can simply note "
            "(minor/survivable -- no rebuild needed)? Be honest even if it means admitting the "
            "theory needs to change."
        )

        prompt = (
            f"ROUND: {round_number}\n"
            f"Your Theory: {theory.theory_of_the_case}\n"
            f"Strongest Argument: {theory.strongest_arguments[0].claim if theory.strongest_arguments else 'N/A'}\n\n"
            f"Opposing Attack: {attack.attack_on_our_argument}\n"
            f"Targets: {attack.targets_argument}\n"
            f"Potential Weaknesses Raised: {attack.potential_weaknesses}\n\n"
            "Assess the materiality of this attack and decide whether revision is required."
        )

        return self.llm.generate_structured(prompt, system_prompt, SelfAssessment)

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        research = state.get("statute_analysis") or state.get("research_findings") or {}
        precedent = state.get("precedent_analysis", {})
        evidence = state.get("evidence_analysis", {})

        inputs_text = compact_json({
            "case": state.get("case_context", {}),
            "objective": state.get("user_query", ""),
            "issues": state.get("identified_issues", []),
            "evidence": evidence,
            "research": research,
            "precedent": precedent,
            "sources": state.get("retrieved_sources", []),
            "unresolved_issues": state.get("unresolved_issues", []),
            "revision_history": state.get("revision_history", []),
            "revision_request": state.get("remediation_instructions", ""),
        }, 5000)

        revision_log: List[Dict[str, Any]] = []
        prior_round = None
        theory = None
        attack = None
        assessment = None

        for round_number in range(1, self.MAX_ROUNDS + 1):
            theory = self._build_theory(inputs_text, prior_round)
            time.sleep(0.8)
            attack = self._attack(theory, round_number)
            time.sleep(0.8)
            assessment = self._self_assess(theory, attack, round_number)

            round_record = {
                "round": round_number,
                "theory": theory.model_dump(),
                "attack": attack.model_dump(),
                "assessment": assessment.model_dump(),
            }

            if not assessment.requires_revision or round_number == self.MAX_ROUNDS:
                if assessment.requires_revision and round_number == self.MAX_ROUNDS:
                    # Hit the safety ceiling while still flagged for revision --
                    # finalize as-is but keep the flag visible downstream
                    # (e.g. for the Adjudicator agent to weigh).
                    round_record["revision_capped"] = True
                revision_log.append(round_record)
                break

            revision_log.append(round_record)
            prior_round = round_record

        result = AdvocateOutput(
            case_theory=theory,
            counterarguments=attack,
            self_assessment=assessment,
            revision_rounds_used=len(revision_log),
            revision_log=revision_log,
        ).model_dump()

        # Compatibility aliases consumed by the report persistence layer.
        result["strategy"] = result["case_theory"]
        result["affirmative_arguments"] = result["case_theory"].get("strongest_arguments", [])

        return result
