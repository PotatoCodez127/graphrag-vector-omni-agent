# main.py
from fastapi import FastAPI, HTTPException
from core.agent import run_autonomous_agent
from core.guardrail import judge_response
from core.schemas import AgentOutput

app = FastAPI(title="Omni-Agent Enterprise Engine")

@app.post("/api/chat", response_model=AgentOutput)
async def chat_endpoint(user_prompt: str):
    # Call the async agent
    draft_json_output = await run_autonomous_agent(user_prompt) 
    
    # Call the async guardrail
    is_safe, block_reason = await judge_response(
        user_prompt, 
        draft_json_output.conversational_reply
    )
    
    if not is_safe:
        raise HTTPException(status_code=403, detail=f"Response blocked: {block_reason}")
        
    return draft_json_output