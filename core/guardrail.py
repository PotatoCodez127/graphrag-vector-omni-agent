# core/guardrail.py
import os
import json
from dotenv import load_dotenv
from ollama import AsyncClient

load_dotenv()

# Initialize Async Client
client = AsyncClient(
    host='https://ollama.com',
    headers={'Authorization': f"Bearer {os.getenv('OLLAMA_API_KEY')}"}
)

async def judge_response(user_prompt: str, draft_reply: str) -> tuple[bool, str]:
    """
    Evaluates the Agent's draft response against company policies.
    """
    judge_prompt = f"""
    You are a strict Corporate Safety Judge. Evaluate the Agent's Response.
    COMPANY POLICIES: 1. No financial/legal/medical advice. 2. No harmful content.
    Return JSON with keys: "safe" (bool), "reason" (str).
    
    User Prompt: "{user_prompt}"
    Agent Response: "{draft_reply}"
    """
    
    response = await client.chat(
        model="qwen3-next:80b-cloud",
        messages=[{"role": "system", "content": judge_prompt}],
        format="json"
    )
    
    raw_content = response['message']['content'].strip()
    if raw_content.startswith("```json"):
        raw_content = raw_content[7:-3].strip()
    
    try:
        data = json.loads(raw_content)
        return data.get("safe", False), data.get("reason", "Safe.")
    except (json.JSONDecodeError, AttributeError):
        return False, "Guardrail parsing failed. Defaulting to block."