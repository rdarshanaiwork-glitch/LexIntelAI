import sys
from app.core.providers.remote import GroqLLMProvider
from app.schemas.agent_schemas import (
    CaseIntakeOutput,
    ResearchStep,
    LegalResearchSynthesis,
    CaseTheory,
    AdversarialAttack,
    SelfAssessment,
    AdvocateOutput,
    AdjudicatorOutput,
    ReportingOutput
)

sys.stdout.reconfigure(encoding='utf-8')
groq = GroqLLMProvider()
print("Using Groq Model:", groq.model)

print("\n--- Test 1: CaseIntakeOutput ---")
try:
    c = groq.generate_structured(
        prompt="Decompose case: Employee Jane Doe reports accounting fraud under SOX in California and was fired 15 days later.",
        system_prompt="You are a legal intake agent.",
        response_model=CaseIntakeOutput
    )
    print("CaseIntakeOutput OK:", len(c.identified_issues), "issues, strategy:", c.execution_strategy)
except Exception as e:
    print("CaseIntakeOutput failed:", e)

print("\n--- Test 2: ResearchStep & LegalResearchSynthesis ---")
try:
    step = groq.generate_structured(
        prompt="Investigate Sarbanes-Oxley whistleblower provisions.",
        system_prompt="You are a legal research agent.",
        response_model=ResearchStep
    )
    print("ResearchStep OK:", step.next_action)
    synth = groq.generate_structured(
        prompt="Synthesize legal research for whistleblower retaliation under SOX.",
        system_prompt="You are a legal research synthesis librarian.",
        response_model=LegalResearchSynthesis
    )
    print("LegalResearchSynthesis OK:", len(synth.findings), "findings")
except Exception as e:
    print("Research components failed:", e)

print("\n--- Test 3: CaseTheory, AdversarialAttack & SelfAssessment ---")
try:
    ct = groq.generate_structured(
        prompt="Formulate a plaintiff case theory for wrongful termination under SOX.",
        system_prompt="You are a plaintiff litigation strategist.",
        response_model=CaseTheory
    )
    print("CaseTheory OK, strongest arguments:", len(ct.strongest_arguments))

    att = groq.generate_structured(
        prompt=f"Attack this theory: {ct.theory_of_the_case}",
        system_prompt="You are aggressive defense counsel.",
        response_model=AdversarialAttack
    )
    print("AdversarialAttack OK, opposing argument:", att.strongest_opposing_argument[:60])

    sa = groq.generate_structured(
        prompt=f"Assess attack materiality: {att.strongest_opposing_argument}",
        system_prompt="You are legal counsel.",
        response_model=SelfAssessment
    )
    print("SelfAssessment OK, requires_revision:", sa.requires_revision, "damage:", sa.damage_assessment)
except Exception as e:
    print("Advocate components failed:", e)

print("\n--- Test 4: AdjudicatorOutput & ReportingOutput ---")
try:
    adj = groq.generate_structured(
        prompt="Adjudicate merits of SOX retaliation claim with strong documentary timing.",
        system_prompt="You are a senior neutral judge.",
        response_model=AdjudicatorOutput
    )
    print("AdjudicatorOutput OK, verdict:", adj.verdict)

    rep = groq.generate_structured(
        prompt="Compile strategic legal report for SOX retaliation matter.",
        system_prompt="You are an expert legal reporting agent.",
        response_model=ReportingOutput
    )
    print("ReportingOutput OK, title:", rep.title, "sections:", len(rep.sections))
except Exception as e:
    print("Adjudicator components failed:", e)

print("\nALL 4 AGENT OUTPUT SCHEMAS TESTED.")
