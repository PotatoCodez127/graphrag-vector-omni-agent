# core/agent.py
import os
import json
import re
from dotenv import load_dotenv
from ollama import AsyncClient # Changed to AsyncClient
from core.tools import tools_schema, search_company_documents, search_org_chart
from core.schemas import AgentOutput
from pydantic import ValidationError

load_dotenv()

client = AsyncClient( # Initialized as Async
    host='https://ollama.com',
    headers={'Authorization': f"Bearer {os.getenv('OLLAMA_API_KEY')}"}
)

async def run_autonomous_agent(user_prompt: str) -> AgentOutput:
    print(f"\n🧠 Agent is analyzing request: '{user_prompt}'")
    
    messages = [
        {"role": "system", "content": "You are Omni-Agent..."},
        {"role": "user", "content": user_prompt}
    ]
    
    for step in range(5):
        # Await the chat call
        response = await client.chat(
            model="qwen3-next:80b-cloud",
            messages=messages,
            tools=tools_schema
        )
        # ... [Tool execution logic remains same] ...
        
        # NOTE: Tool execution functions search_company_documents/search_org_chart 
        # should ideally be async as well if they perform I/O, 
        # but for this logic, we await the chat response.
        
    # [Synthesizer logic follows similar await pattern]
    # ...