# core/guardrail.py
import os
import json
from dotenv import load_dotenv
from ollama import AsyncClient

# Load environment variables
load_dotenv()

# Initialize Ollama Cloud Client
async def judge_response(user_prompt: str, draft_reply: str) -> tuple[bool, str]:
    # Await the chat call
    response = await client.chat(
        model="qwen3-next:80b-cloud",
        messages=[{"role": "system", "content": judge_prompt}],
        format="json"
    )

def judge_response(user_prompt: str, draft_reply: str) -> tuple[bool, str]:
    """
    Evaluates the Agent's draft response against company policies.
    Returns a tuple: (is_safe: bool, block_reason: str).
    """
    print(f"🛡️ Guardrail evaluating draft response for safety...")
    
    # Define the strict policies the Judge must enforce
    judge_prompt = f"""
    You are a strict Corporate Safety Judge. Evaluate the Agent's Response to the User's Prompt.
    
    COMPANY POLICIES:
    1. Do not provide financial, legal, or medical advice.
    2. Do not generate harmful, offensive, or explicit content.
    3. Do not engage in arguments or complaints about the company.
    
    Return a JSON object with EXACTLY these two keys:
    - "safe": boolean (true if the response adheres to all policies, false if it violates any)
    - "reason": string (a short explanation of your decision, especially if blocked)
    
    User Prompt: "{user_prompt}"
    Agent Response: "{draft_reply}"
    """
    
    # Call the LLM and force JSON output
    response = client.chat(
        model="qwen3-next:80b-cloud", # You can use a smaller/faster model for the judge if you prefer
        messages=[{"role": "system", "content": judge_prompt}],
        format="json"
    )
    
    raw_content = response['message']['content'].strip()
    
    # Defensive parsing for Markdown code blocks
    if raw_content.startswith("```json"):
        raw_content = raw_content[7:-3].strip()
    elif raw_content.startswith("```"):
        raw_content = raw_content[3:-3].strip()
        
    try:
        # Parse the JSON and extract the safety decision
        data = json.loads(raw_content)
        is_safe = data.get("safe", False)
        reason = data.get("reason", "Safe.")
        return is_safe, reason
    except json.JSONDecodeError as e:
        print(f"   [GUARDRAIL ERROR] Failed to parse judge output: {e}")
        # Fail-safe: If the guardrail crashes, we block the message to be safe.
        return False, f"Guardrail parsing failed. Defaulting to block. Raw: {raw_content}"