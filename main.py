# main.py
@app.post("/api/chat", response_model=AgentOutput)
async def chat_endpoint(user_prompt: str):
    # Await the async chain
    draft_json_output = await run_autonomous_agent(user_prompt) 
    
    is_safe, block_reason = await judge_response(user_prompt, draft_json_output.conversational_reply)
    
    if not is_safe:
        raise HTTPException(status_code=403, detail="Response blocked.")
    return draft_json_output