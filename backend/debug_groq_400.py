import httpx
import json
import sys
from app.core.config import settings
from app.schemas.agent_schemas import LegalResearchSynthesis

sys.stdout.reconfigure(encoding='utf-8')

schema = LegalResearchSynthesis.model_json_schema()
props = schema.get('properties', {})
clean_template = {k: f"<{props[k].get('type', 'value')}>" for k in props}
sys_content = (
    "You are a legal research synthesis librarian.\n"
    "You MUST respond ONLY with a single valid JSON object. Do NOT return schema definitions. Fill in concrete instantiated values for these keys:\n"
    + json.dumps(clean_template, indent=2)
)
user_content = "Synthesize legal research for whistleblower retaliation under SOX.\n\nRespond strictly with the required JSON object containing your actual findings and instantiated values."

payload = {
    "model": "openai/gpt-oss-20b",
    "messages": [{"role": "system", "content": sys_content}, {"role": "user", "content": user_content}],
    "temperature": 0.2,
    "max_tokens": 4096,
    "response_format": {"type": "json_object"}
}

with httpx.Client(timeout=45) as client:
    res = client.post(
        f"{settings.GROQ_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"},
        json=payload
    )
    print("STATUS with max_tokens 4096:", res.status_code)
    data = res.json()
    content = data["choices"][0]["message"]["content"]
    print("Content length:", len(content))
    obj = json.loads(content)
    parsed = LegalResearchSynthesis.model_validate(obj)
    print("LegalResearchSynthesis validated cleanly! Findings:", len(parsed.findings))
