import sys
from app.core.providers.remote import OllamaLLMProvider
from app.schemas.agent_schemas import (
    CaseIntakeOutput,
    ResearchStep,
    LegalResearchSynthesis,
    CaseTheory,
    AdversarialAttack,
    SelfAssessment,
    AdjudicatorOutput,
    ReportingOutput
)

sys.stdout.reconfigure(encoding='utf-8')

print("Testing local Ollama with gpt-oss:20b across all 4 departments...")
ollama = OllamaLLMProvider(model="gpt-oss:20b")

# Test 1: Intake
print("\n--- Department 1: CaseIntakeAgent ---")
c = ollama.generate_structured(
    prompt="Decompose case: John Doe was fired 10 days after reporting Clean Air Act violations in Texas.",
    system_prompt="You are a legal intake agent.",
    response_model=CaseIntakeOutput
)
print("CaseIntakeOutput OK:", len(c.identified_issues), "issues, strategy:", c.execution_strategy)

# Test 2: Research
print("\n--- Department 2: LegalResearchAgent ---")
step = ollama.generate_structured(
    prompt="Investigate EPA whistleblower protections under 42 U.S.C. 7622.",
    system_prompt="You are a legal research agent.",
    response_model=ResearchStep
)
print("ResearchStep OK:", step.next_action, "| query:", step.query)
synth = ollama.generate_structured(
    prompt="Synthesize legal authorities on Clean Air Act whistleblower retaliation.",
    system_prompt="You are a legal research synthesis librarian.",
    response_model=LegalResearchSynthesis
)
print("LegalResearchSynthesis OK:", len(synth.findings), "findings")

# Test 3: Advocacy
print("\n--- Department 3: AdvocateAgent ---")
ct = ollama.generate_structured(
    prompt="Formulate a plaintiff case theory for Clean Air Act retaliatory discharge.",
    system_prompt="You are a plaintiff litigation strategist.",
    response_model=CaseTheory
)
print("CaseTheory OK:", len(ct.strongest_arguments), "strongest arguments")

att = ollama.generate_structured(
    prompt=f"Attack this theory as defense counsel: {ct.theory_of_the_case}",
    system_prompt="You are aggressive defense counsel.",
    response_model=AdversarialAttack
)
print("AdversarialAttack OK, opposing argument:", att.strongest_opposing_argument[:70])

sa = ollama.generate_structured(
    prompt=f"Assess attack materiality: {att.strongest_opposing_argument}",
    system_prompt="You are legal counsel.",
    response_model=SelfAssessment
)
print("SelfAssessment OK, damage:", sa.damage_assessment, "requires_revision:", sa.requires_revision)

# Test 4: Adjudication & Reporting
print("\n--- Department 4: AdjudicatorReportingAgent ---")
adj = ollama.generate_structured(
    prompt="Adjudicate merits of Clean Air Act whistleblower retaliatory discharge.",
    system_prompt="You are a senior neutral judge.",
    response_model=AdjudicatorOutput
)
print("AdjudicatorOutput OK, verdict:", adj.verdict)

rep = ollama.generate_structured(
    prompt="Compile strategic legal report for Clean Air Act retaliatory discharge matter.",
    system_prompt="You are an expert legal reporting agent.",
    response_model=ReportingOutput
)
print("ReportingOutput OK, title:", rep.title, "| sections:", len(rep.sections))

print("\nALL 4 DEPARTMENTS VALIDATED ON LOCAL OLLAMA gpt-oss:20b SUCCESSFULLY!")
